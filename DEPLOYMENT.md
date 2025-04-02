# Deployment Guide for Python Web Application

This guide provides detailed instructions for deploying the Python Web Application to a production environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Preparation](#server-preparation)
3. [Application Setup](#application-setup)
4. [Database Setup](#database-setup)
5. [Web Server Configuration](#web-server-configuration)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Process Management](#process-management)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup and Restore](#backup-and-restore)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the application, ensure you have the following:

- A server running Linux (Ubuntu 20.04 LTS or later recommended)
- Python 3.9 or higher
- PostgreSQL 12 or higher (recommended for production)
- Nginx web server
- Domain name (for production deployment)
- SSL certificate (Let's Encrypt recommended)

## Server Preparation

### Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required System Packages

```bash
sudo apt install -y python3-pip python3-dev python3-venv build-essential libssl-dev libffi-dev postgresql postgresql-contrib nginx git supervisor
```

### Create a Dedicated User (Optional but Recommended)

```bash
sudo adduser webappuser
sudo usermod -aG sudo webappuser
su - webappuser
```

## Application Setup

### Clone the Repository

```bash
git clone https://github.com/yourusername/pythonweb.git
cd pythonweb
```

### Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements-prod.txt
```

### Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
nano .env
```

Update the following variables:

```
FLASK_APP=run.py
FLASK_CONFIG=production
FLASK_DEBUG=0
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://username:password@localhost/dbname
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@example.com
```

## Database Setup

### Create PostgreSQL Database and User

```bash
sudo -u postgres psql
```

In the PostgreSQL shell:

```sql
CREATE DATABASE pythonweb;
CREATE USER pythonwebuser WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE pythonweb TO pythonwebuser;
\q
```

### Initialize the Database

```bash
flask db upgrade
```

### Create Initial Admin User

```bash
flask create-admin admin admin@example.com secure-admin-password
```

## Web Server Configuration

### Create WSGI Entry Point

Create a `wsgi.py` file in the project root:

```python
import os
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
```

### Configure Gunicorn

The `gunicorn_config.py` file should already be in your project. If not, create it using the deployment script:

```bash
python deploy.py --skip-tests
```

### Configure Nginx

Create an Nginx server block configuration:

```bash
sudo nano /etc/nginx/sites-available/pythonweb
```

Add the following configuration (replace `example.com` with your domain):

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/app/app/static/;
        expires 30d;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/pythonweb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/TLS Configuration

### Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

Follow the prompts to complete the certificate installation.

## Process Management

### Configure Supervisor

Update the `supervisor.conf` file with the correct paths:

```bash
nano supervisor.conf
```

Install the configuration:

```bash
sudo cp supervisor.conf /etc/supervisor/conf.d/pythonweb.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pythonweb
```

### Create Systemd Service (Alternative to Supervisor)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/pythonweb.service
```

Add the following content:

```ini
[Unit]
Description=Gunicorn instance to serve Python Web Application
After=network.target

[Service]
User=webappuser
Group=webappuser
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/gunicorn -c gunicorn_config.py wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable pythonweb
sudo systemctl start pythonweb
```

## Monitoring and Logging

### Configure Logging

Ensure the `logs` directory exists:

```bash
mkdir -p logs
```

### Monitor Application Status

```bash
# If using Supervisor
sudo supervisorctl status pythonweb

# If using Systemd
sudo systemctl status pythonweb
```

### View Logs

```bash
# Application logs
tail -f logs/gunicorn-error.log
tail -f logs/gunicorn-access.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Supervisor logs
tail -f logs/supervisor.err.log
tail -f logs/supervisor.out.log
```

## Backup and Restore

### Database Backup

```bash
# Create backups directory
mkdir -p backups

# Backup PostgreSQL database
pg_dump -U pythonwebuser pythonweb > backups/pythonweb_$(date +%Y%m%d_%H%M%S).sql
```

### Database Restore

```bash
# Restore from backup
psql -U pythonwebuser pythonweb < backups/backup_file.sql
```

### Application Backup

```bash
# Backup application files
tar -czvf backups/app_backup_$(date +%Y%m%d_%H%M%S).tar.gz --exclude=venv --exclude=__pycache__ --exclude=*.pyc .
```

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

Check the logs:

```bash
tail -f logs/gunicorn-error.log
```

Verify the virtual environment is activated and all dependencies are installed:

```bash
source venv/bin/activate
pip install -r requirements-prod.txt
```

#### Database Connection Issues

Verify PostgreSQL is running:

```bash
sudo systemctl status postgresql
```

Check database connection settings in `.env` file.

#### Nginx Returns 502 Bad Gateway

Verify Gunicorn is running:

```bash
ps aux | grep gunicorn
```

Check Nginx configuration:

```bash
sudo nginx -t
```

#### SSL Certificate Issues

Verify certificate renewal:

```bash
sudo certbot certificates
```

Renew certificates if needed:

```bash
sudo certbot renew
```

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the application logs for specific error messages
2. Consult the Flask and Gunicorn documentation
3. Open an issue on the project's GitHub repository

## Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Install updated dependencies
pip install -r requirements-prod.txt

# Apply database migrations
flask db upgrade

# Restart the application
sudo supervisorctl restart pythonweb
# or
sudo systemctl restart pythonweb
```

### Renewing SSL Certificates

Certbot should automatically renew certificates. To manually trigger renewal:

```bash
sudo certbot renew
```
