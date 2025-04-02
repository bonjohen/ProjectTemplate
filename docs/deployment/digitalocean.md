# Deploying Python Web Application to DigitalOcean

This guide provides step-by-step instructions for deploying the Python Web Application to a DigitalOcean Droplet (VPS), giving you full control over your server environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Why DigitalOcean?](#why-digitalocean)
3. [Server Setup](#server-setup)
4. [Application Deployment](#application-deployment)
5. [Web Server Configuration](#web-server-configuration)
6. [Database Setup](#database-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have:

- A DigitalOcean account (sign up at [digitalocean.com](https://www.digitalocean.com/))
- Your Python Web Application code in a Git repository
- A domain name (optional but recommended)
- SSH key pair for secure server access
- Basic knowledge of Linux command line

## Why DigitalOcean?

DigitalOcean offers several advantages for deploying Python web applications:

- **Full Control**: Complete control over your server environment
- **Cost-Effective**: Plans starting at $5/month
- **Scalability**: Easily resize your server as needs grow
- **SSD Storage**: Fast SSD-based virtual machines
- **Global Data Centers**: Deploy close to your users
- **Simple UI**: User-friendly control panel
- **API Access**: Automate infrastructure management
- **Monitoring**: Built-in server monitoring

## Server Setup

### Step 1: Create a Droplet

1. Log in to your DigitalOcean account
2. Click "Create" and select "Droplets"
3. Choose an image:
   - Distribution: Ubuntu 22.04 LTS
4. Select a plan:
   - Basic (Shared CPU)
   - $5/mo (1GB RAM, 1 CPU, 25GB SSD)
5. Choose a data center region close to your users
6. Add your SSH key for secure access
7. Choose a hostname (e.g., pythonweb-production)
8. Click "Create Droplet"

### Step 2: Connect to Your Droplet

1. Find your Droplet's IP address in the DigitalOcean dashboard
2. Connect via SSH:
   ```bash
   ssh root@your_droplet_ip
   ```

### Step 3: Update System Packages

```bash
apt update
apt upgrade -y
```

### Step 4: Create a Non-Root User

```bash
# Create a new user
adduser webappuser

# Add user to sudo group
usermod -aG sudo webappuser

# Switch to the new user
su - webappuser
```

### Step 5: Install Required Packages

```bash
sudo apt install -y python3-pip python3-dev python3-venv build-essential libssl-dev libffi-dev postgresql postgresql-contrib nginx git supervisor
```

### Step 6: Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable
```

## Application Deployment

### Step 1: Clone Your Repository

```bash
# Create a directory for your application
mkdir -p ~/apps
cd ~/apps

# Clone your repository
git clone https://github.com/yourusername/your-repo.git pythonweb
cd pythonweb
```

### Step 2: Set Up Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Step 3: Configure Environment Variables

Create a .env file in your project directory:

```bash
nano .env
```

Add your environment variables:

```
FLASK_APP=run.py
FLASK_CONFIG=production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://dbuser:password@localhost/pythonweb
```

### Step 4: Create a WSGI Entry Point

If you don't already have a wsgi.py file, create one:

```bash
nano wsgi.py
```

Add the following content:

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

### Step 5: Test Your Application

```bash
# Test with Gunicorn
gunicorn --bind 127.0.0.1:8000 wsgi:application
```

Press Ctrl+C to stop the test server after verifying it starts correctly.

## Web Server Configuration

### Step 1: Create a Systemd Service File

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
Group=www-data
WorkingDirectory=/home/webappuser/apps/pythonweb
Environment="PATH=/home/webappuser/apps/pythonweb/venv/bin"
EnvironmentFile=/home/webappuser/apps/pythonweb/.env
ExecStart=/home/webappuser/apps/pythonweb/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 2: Start and Enable the Service

```bash
sudo systemctl start pythonweb
sudo systemctl enable pythonweb
sudo systemctl status pythonweb
```

### Step 3: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/pythonweb
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/webappuser/apps/pythonweb/app/static/;
        expires 30d;
    }
}
```

### Step 4: Enable the Nginx Configuration

```bash
sudo ln -s /etc/nginx/sites-available/pythonweb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Database Setup

### Step 1: Create a PostgreSQL Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell
CREATE DATABASE pythonweb;
CREATE USER dbuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE pythonweb TO dbuser;
\q
```

### Step 2: Configure Database Connection

Ensure your .env file has the correct DATABASE_URL:

```
DATABASE_URL=postgresql://dbuser:password@localhost/pythonweb
```

### Step 3: Initialize the Database

```bash
cd ~/apps/pythonweb
source venv/bin/activate
flask db upgrade
flask init-db
```

## SSL/TLS Configuration

### Step 1: Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Step 2: Obtain SSL Certificate

```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

Follow the prompts to complete the certificate installation.

### Step 3: Verify Auto-Renewal

Certbot automatically adds a cron job for certificate renewal. Verify it with:

```bash
sudo systemctl status certbot.timer
```

## Monitoring and Maintenance

### Step 1: Set Up Basic Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop fail2ban

# Set up log rotation
sudo nano /etc/logrotate.d/pythonweb
```

Add the following configuration:

```
/home/webappuser/apps/pythonweb/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 webappuser www-data
}
```

### Step 2: Configure Supervisor for Process Management (Optional)

```bash
sudo nano /etc/supervisor/conf.d/pythonweb.conf
```

Add the following configuration:

```ini
[program:pythonweb]
directory=/home/webappuser/apps/pythonweb
command=/home/webappuser/apps/pythonweb/venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 wsgi:application
user=webappuser
autostart=true
autorestart=true
stderr_logfile=/home/webappuser/apps/pythonweb/logs/supervisor.err.log
stdout_logfile=/home/webappuser/apps/pythonweb/logs/supervisor.out.log
environment=FLASK_CONFIG=production
```

Create the logs directory:

```bash
mkdir -p ~/apps/pythonweb/logs
```

Reload Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

## Backup and Recovery

### Step 1: Set Up Database Backups

Create a backup script:

```bash
nano ~/backup_db.sh
```

Add the following content:

```bash
#!/bin/bash
BACKUP_DIR="/home/webappuser/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/pythonweb_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -U dbuser pythonweb > $BACKUP_FILE

# Compress the backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -type f -name "pythonweb_*.sql.gz" -mtime +30 -delete
```

Make the script executable:

```bash
chmod +x ~/backup_db.sh
```

### Step 2: Schedule Regular Backups

Add a cron job to run the backup script:

```bash
crontab -e
```

Add the following line to run the backup daily at 2 AM:

```
0 2 * * * /home/webappuser/backup_db.sh
```

### Step 3: Set Up Application Backups

Create an application backup script:

```bash
nano ~/backup_app.sh
```

Add the following content:

```bash
#!/bin/bash
BACKUP_DIR="/home/webappuser/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/app_$TIMESTAMP.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create application backup
tar -czf $BACKUP_FILE -C /home/webappuser/apps pythonweb --exclude="pythonweb/venv" --exclude="pythonweb/__pycache__" --exclude="pythonweb/*.pyc"

# Remove backups older than 30 days
find $BACKUP_DIR -type f -name "app_*.tar.gz" -mtime +30 -delete
```

Make the script executable:

```bash
chmod +x ~/backup_app.sh
```

Add a cron job to run the backup weekly:

```bash
crontab -e
```

Add the following line:

```
0 3 * * 0 /home/webappuser/backup_app.sh
```

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

- **Check Logs**: `sudo journalctl -u pythonweb.service`
- **Permissions**: Ensure file permissions are correct
- **Environment Variables**: Verify environment variables are set correctly
- **Virtual Environment**: Check that all dependencies are installed

#### Nginx Returns 502 Bad Gateway

- **Gunicorn Running**: Verify Gunicorn is running with `ps aux | grep gunicorn`
- **Socket Permissions**: Check socket file permissions if using Unix sockets
- **Nginx Configuration**: Verify Nginx configuration with `sudo nginx -t`

#### Database Connection Issues

- **Connection String**: Verify your DATABASE_URL environment variable
- **PostgreSQL Running**: Check with `sudo systemctl status postgresql`
- **Database Permissions**: Ensure your database user has the correct permissions

#### SSL Certificate Issues

- **Certificate Renewal**: Check renewal status with `sudo certbot certificates`
- **Nginx Configuration**: Verify SSL configuration in Nginx

## Conclusion

Deploying to a DigitalOcean Droplet gives you full control over your server environment, allowing for customization and optimization specific to your application's needs. While it requires more setup and maintenance than platform-as-a-service options, it offers greater flexibility and can be more cost-effective for larger applications.

This deployment approach is suitable for applications that need custom server configurations, have specific performance requirements, or need to scale beyond what shared hosting can provide.

## Resources

- [DigitalOcean Documentation](https://docs.digitalocean.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/en/stable/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Web Application Documentation](../../README.md)
