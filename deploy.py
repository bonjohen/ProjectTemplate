#!/usr/bin/env python
"""
Deployment script for the Python Web Application.
This script automates the deployment process for production environments.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

# Define colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_step(message):
    """Print a step message with formatting"""
    print(f"\n{Colors.HEADER}=== {message} ==={Colors.ENDC}")

def print_success(message):
    """Print a success message with formatting"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message with formatting"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message with formatting"""
    print(f"{Colors.WARNING}! {message}{Colors.ENDC}")

def run_command(command, error_message="Command failed"):
    """Run a shell command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"{error_message}: {e}")
        print(e.stderr)
        return None

def check_environment():
    """Check if the environment is properly set up for deployment"""
    print_step("Checking environment")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_warning("Not running in a virtual environment. It's recommended to use a virtual environment for deployment.")
    else:
        print_success("Running in a virtual environment")
    
    # Check if required environment variables are set
    required_vars = ['FLASK_APP', 'FLASK_CONFIG', 'SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print_error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    print_success("All required environment variables are set")
    
    # Check if database URL is set for production
    if os.environ.get('FLASK_CONFIG') == 'production' and not os.environ.get('DATABASE_URL'):
        print_warning("DATABASE_URL is not set. Using default SQLite database.")
    
    return True

def install_dependencies():
    """Install or update dependencies"""
    print_step("Installing dependencies")
    
    result = run_command("pip install -r requirements.txt --upgrade", "Failed to install dependencies")
    if result:
        print_success("Dependencies installed successfully")
        return True
    return False

def run_tests():
    """Run tests to ensure everything is working"""
    print_step("Running tests")
    
    # Set environment to testing
    os.environ['FLASK_CONFIG'] = 'testing'
    
    result = run_command("python -m pytest", "Tests failed")
    
    # Reset environment
    os.environ['FLASK_CONFIG'] = 'production'
    
    if result:
        print_success("All tests passed")
        return True
    return False

def compile_static_assets():
    """Compile and minify static assets"""
    print_step("Compiling static assets")
    
    # Create a directory for compiled assets if it doesn't exist
    os.makedirs('app/static/dist', exist_ok=True)
    
    # Minify CSS (using a simple file concatenation for this example)
    css_files = ['app/static/css/style.css']
    with open('app/static/dist/app.min.css', 'w') as outfile:
        for css_file in css_files:
            with open(css_file, 'r') as infile:
                outfile.write(infile.read())
    
    # Minify JS (using a simple file concatenation for this example)
    js_files = ['app/static/js/main.js']
    with open('app/static/dist/app.min.js', 'w') as outfile:
        for js_file in js_files:
            with open(js_file, 'r') as infile:
                outfile.write(infile.read())
    
    print_success("Static assets compiled successfully")
    return True

def setup_database():
    """Set up or migrate the database"""
    print_step("Setting up database")
    
    # Run database migrations
    result = run_command("flask db upgrade", "Database migration failed")
    if not result:
        return False
    
    print_success("Database migrated successfully")
    return True

def create_production_wsgi():
    """Create a WSGI file for production"""
    print_step("Creating WSGI file")
    
    wsgi_content = """import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Set Flask environment to production
os.environ['FLASK_CONFIG'] = 'production'

from run import app as application

if __name__ == '__main__':
    application.run()
"""
    
    with open('wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print_success("WSGI file created successfully")
    return True

def create_nginx_config():
    """Create an Nginx configuration file"""
    print_step("Creating Nginx configuration")
    
    server_name = input("Enter the server name (e.g., example.com): ") or "example.com"
    
    nginx_config = f"""server {{
    listen 80;
    server_name {server_name};

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /static/ {{
        alias /path/to/your/app/static/;
        expires 30d;
    }}
}}
"""
    
    with open('nginx_config.conf', 'w') as f:
        f.write(nginx_config)
    
    print_success(f"Nginx configuration created: nginx_config.conf")
    print_warning("You need to update the static files path in the Nginx configuration")
    return True

def create_systemd_service():
    """Create a systemd service file"""
    print_step("Creating systemd service file")
    
    service_name = input("Enter the service name (default: pythonweb): ") or "pythonweb"
    user = input("Enter the user to run the service (default: www-data): ") or "www-data"
    app_dir = os.path.abspath(os.getcwd())
    
    service_content = f"""[Unit]
Description=Gunicorn instance to serve Python Web Application
After=network.target

[Service]
User={user}
Group={user}
WorkingDirectory={app_dir}
Environment="PATH={app_dir}/venv/bin"
ExecStart={app_dir}/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    with open(f'{service_name}.service', 'w') as f:
        f.write(service_content)
    
    print_success(f"Systemd service file created: {service_name}.service")
    print(f"To install the service, run:")
    print(f"  sudo cp {service_name}.service /etc/systemd/system/")
    print(f"  sudo systemctl enable {service_name}")
    print(f"  sudo systemctl start {service_name}")
    return True

def create_deployment_docs():
    """Create deployment documentation"""
    print_step("Creating deployment documentation")
    
    docs_content = """# Deployment Guide

## Prerequisites

- Python 3.9 or higher
- Nginx
- PostgreSQL (recommended for production)
- Systemd (for service management)

## Deployment Steps

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` for production
   - Make sure to set `FLASK_CONFIG=production`
   - Set a strong `SECRET_KEY`
   - Configure `DATABASE_URL` for PostgreSQL

5. Set up the database:
   ```
   flask db upgrade
   ```

6. Run the deployment script:
   ```
   python deploy.py
   ```

7. Configure Nginx:
   - Copy the generated `nginx_config.conf` to `/etc/nginx/sites-available/`
   - Create a symbolic link: `sudo ln -s /etc/nginx/sites-available/nginx_config.conf /etc/nginx/sites-enabled/`
   - Test the configuration: `sudo nginx -t`
   - Restart Nginx: `sudo systemctl restart nginx`

8. Set up the systemd service:
   - Copy the generated service file to `/etc/systemd/system/`
   - Enable the service: `sudo systemctl enable <service-name>`
   - Start the service: `sudo systemctl start <service-name>`

9. Set up SSL/TLS with Certbot:
   ```
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d example.com -d www.example.com
   ```

## Maintenance

- Update the application:
  ```
  git pull
  pip install -r requirements.txt --upgrade
  flask db upgrade
  sudo systemctl restart <service-name>
  ```

- View logs:
  ```
  sudo journalctl -u <service-name>
  ```

- Backup the database:
  ```
  pg_dump -U <username> <database> > backup_$(date +%Y%m%d).sql
  ```

## Troubleshooting

- Check the application logs:
  ```
  sudo journalctl -u <service-name>
  ```

- Check Nginx logs:
  ```
  sudo tail -f /var/log/nginx/error.log
  ```

- Verify the application is running:
  ```
  sudo systemctl status <service-name>
  ```
"""
    
    with open('DEPLOYMENT.md', 'w') as f:
        f.write(docs_content)
    
    print_success("Deployment documentation created: DEPLOYMENT.md")
    return True

def backup_database():
    """Create a backup of the database"""
    print_step("Backing up database")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Check if we're using SQLite
    if 'sqlite' in os.environ.get('DATABASE_URL', 'sqlite'):
        # SQLite backup
        db_path = os.path.join(os.path.dirname(__file__), 'app.db')
        if os.path.exists(db_path):
            backup_path = os.path.join(backup_dir, f"app_backup_{timestamp}.db")
            import shutil
            shutil.copy2(db_path, backup_path)
            print_success(f"SQLite database backed up to {backup_path}")
        else:
            print_warning("SQLite database file not found")
    else:
        # PostgreSQL backup
        db_url = os.environ.get('DATABASE_URL')
        if db_url and db_url.startswith('postgresql'):
            backup_path = os.path.join(backup_dir, f"pg_backup_{timestamp}.sql")
            # Extract database name from URL
            db_name = db_url.split('/')[-1]
            result = run_command(f"pg_dump {db_name} > {backup_path}", "PostgreSQL backup failed")
            if result is not None:
                print_success(f"PostgreSQL database backed up to {backup_path}")
        else:
            print_warning("PostgreSQL database URL not found or not configured")
    
    return True

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy the Python Web Application")
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-assets', action='store_true', help='Skip compiling static assets')
    parser.add_argument('--skip-docs', action='store_true', help='Skip creating deployment documentation')
    parser.add_argument('--backup', action='store_true', help='Create a database backup')
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.BLUE}Python Web Application Deployment{Colors.ENDC}")
    print(f"Starting deployment at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not check_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Run tests if not skipped
    if not args.skip_tests and not run_tests():
        return False
    
    # Compile static assets if not skipped
    if not args.skip_assets and not compile_static_assets():
        return False
    
    # Set up database
    if not setup_database():
        return False
    
    # Create WSGI file
    if not create_production_wsgi():
        return False
    
    # Create Nginx configuration
    if not create_nginx_config():
        return False
    
    # Create systemd service
    if not create_systemd_service():
        return False
    
    # Create deployment documentation if not skipped
    if not args.skip_docs and not create_deployment_docs():
        return False
    
    # Backup database if requested
    if args.backup and not backup_database():
        return False
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}Deployment completed successfully!{Colors.ENDC}")
    print(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nNext steps:")
    print(f"1. Review and update the Nginx configuration in nginx_config.conf")
    print(f"2. Install and configure the systemd service")
    print(f"3. Set up SSL/TLS with Certbot")
    print(f"4. Refer to DEPLOYMENT.md for detailed instructions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
