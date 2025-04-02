# Deploying Python Web Application to PythonAnywhere

This guide provides step-by-step instructions for deploying the Python Web Application to PythonAnywhere, a Python-specific hosting platform that's ideal for Flask applications.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Why PythonAnywhere?](#why-pythonanywhere)
3. [Deployment Process](#deployment-process)
4. [Database Configuration](#database-configuration)
5. [Static Files and Media](#static-files-and-media)
6. [Custom Domain Setup](#custom-domain-setup)
7. [Scheduled Tasks](#scheduled-tasks)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have:

- Your Python Web Application code ready for deployment
- A PythonAnywhere account (sign up at [pythonanywhere.com](https://www.pythonanywhere.com/))
- A requirements.txt file listing all dependencies
- A WSGI configuration file for your application

## Why PythonAnywhere?

PythonAnywhere offers several advantages for Python web applications:

- **Python-Specific**: Designed specifically for Python applications
- **Free Tier**: Includes a free plan for small applications
- **Pre-installed Packages**: Many Python packages are pre-installed
- **Web-based Console**: Access Python consoles and bash terminals via browser
- **MySQL Database**: Free MySQL database included
- **Scheduled Tasks**: Run scheduled tasks (cron jobs)
- **Simple Deployment**: No need for complex server configuration

## Deployment Process

### Step 1: Create a PythonAnywhere Account

1. Sign up for a PythonAnywhere account at [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Choose a plan that meets your needs (Free, Hacker, Web Developer, etc.)

### Step 2: Upload Your Application Code

#### Option 1: Using Git

1. Open a Bash console in PythonAnywhere
2. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   ```

#### Option 2: Using the File Manager

1. Go to the "Files" tab in PythonAnywhere
2. Create a new directory for your application
3. Upload your files using the file manager

#### Option 3: Using the Uploader API

1. Zip your application files
2. Use the PythonAnywhere API to upload the zip file
3. Extract the files on the server

### Step 3: Create a Virtual Environment

1. Open a Bash console in PythonAnywhere
2. Navigate to your project directory:
   ```bash
   cd ~/your-project-directory
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Configure a Web App

1. Go to the "Web" tab in PythonAnywhere
2. Click "Add a new web app"
3. Choose your domain (e.g., yourusername.pythonanywhere.com)
4. Select "Manual configuration"
5. Choose the Python version that matches your application (e.g., Python 3.9)
6. Set the path to your project directory (e.g., /home/yourusername/your-project-directory)

### Step 5: Configure the WSGI File

1. In the "Web" tab, click on the WSGI configuration file link
2. Replace the contents with the following (adjust paths as needed):

```python
import sys
import os

# Add your project directory to the system path
path = '/home/yourusername/your-project-directory'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['FLASK_CONFIG'] = 'production'
os.environ['SECRET_KEY'] = 'your-secure-secret-key'

# Import your application
from run import app as application
```

3. Save the file

### Step 6: Configure Static Files

1. In the "Web" tab, scroll down to "Static files"
2. Add the following mappings:
   - URL: `/static/` → Directory: `/home/yourusername/your-project-directory/app/static`
   - URL: `/favicon.ico` → Directory: `/home/yourusername/your-project-directory/app/static/img/favicon.ico`

### Step 7: Set Up the Database

1. Go to the "Databases" tab
2. Initialize your MySQL database (included with your account)
3. Note your database name, username, and password

### Step 8: Configure Environment Variables

1. In the "Web" tab, scroll down to "Environment variables"
2. Add the following variables:
   - `FLASK_CONFIG`: `production`
   - `SECRET_KEY`: `your-secure-secret-key`
   - `DATABASE_URL`: `mysql://yourusername:password@yourusername.mysql.pythonanywhere-services.com/yourusername$dbname`

### Step 9: Initialize the Database

1. Open a Bash console in PythonAnywhere
2. Navigate to your project directory:
   ```bash
   cd ~/your-project-directory
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Run database migrations:
   ```bash
   flask db upgrade
   ```
5. Initialize the database with default data:
   ```bash
   flask init-db
   ```

### Step 10: Reload the Web App

1. Go to the "Web" tab
2. Click the "Reload" button for your web app
3. Visit your site at yourusername.pythonanywhere.com

## Database Configuration

### Using MySQL Database

1. Configure your application to use MySQL:
   ```python
   # In config.py
   class ProductionConfig(Config):
       SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
   ```

2. Install the MySQL client in your virtual environment:
   ```bash
   pip install mysqlclient
   ```

3. Create database tables:
   ```bash
   flask db upgrade
   ```

### Database Backup and Restore

1. Backup your database:
   ```bash
   mysqldump -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p 'yourusername$dbname' > backup.sql
   ```

2. Restore from backup:
   ```bash
   mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p 'yourusername$dbname' < backup.sql
   ```

## Static Files and Media

### Serving Static Files

PythonAnywhere automatically serves files from the static directory you configured. Make sure your application references static files correctly:

```python
url_for('static', filename='css/style.css')
```

### Handling User Uploads

1. Configure your application to save uploads to a specific directory:
   ```python
   UPLOAD_FOLDER = '/home/yourusername/your-project-directory/app/static/uploads'
   ```

2. Add a static files mapping for the uploads directory:
   - URL: `/static/uploads/` → Directory: `/home/yourusername/your-project-directory/app/static/uploads`

## Custom Domain Setup

### Free Accounts

Free accounts can only use the default yourusername.pythonanywhere.com domain.

### Paid Accounts

1. Register your domain with a domain registrar
2. Go to the "Web" tab in PythonAnywhere
3. Click on the "Add a new domain" button
4. Enter your domain name
5. Configure your domain's DNS settings:
   - Add a CNAME record pointing to yourusername.pythonanywhere.com
   - Or add an A record pointing to the IP address provided by PythonAnywhere

## Scheduled Tasks

PythonAnywhere allows you to set up scheduled tasks (similar to cron jobs):

1. Go to the "Tasks" tab
2. Add a new scheduled task
3. Set the time when the task should run
4. Enter the command to run (include the path to your virtual environment's Python):
   ```
   /home/yourusername/your-project-directory/venv/bin/python /home/yourusername/your-project-directory/scheduled_task.py
   ```

## Troubleshooting

### Common Issues and Solutions

#### Application Error

- **Check Error Logs**: Go to the "Web" tab and click on the "Error log" link
- **WSGI Configuration**: Verify your WSGI file is correctly configured
- **Virtual Environment**: Ensure all dependencies are installed in your virtual environment
- **File Permissions**: Check file permissions for your application files

#### Database Connection Issues

- **Connection String**: Verify your DATABASE_URL environment variable
- **MySQL Client**: Ensure mysqlclient is installed in your virtual environment
- **Database Permissions**: Check that your user has the necessary permissions

#### Static Files Not Loading

- **Static Files Configuration**: Verify your static files mappings in the "Web" tab
- **File Paths**: Ensure your templates reference static files correctly
- **Cache Issues**: Try clearing your browser cache

#### Slow Application Performance

- **Free Plan Limitations**: Free plans have CPU and bandwidth restrictions
- **Database Optimization**: Add indexes to frequently queried fields
- **Caching**: Implement caching for frequently accessed data

## Conclusion

PythonAnywhere provides a straightforward way to deploy Python web applications without managing servers or infrastructure. Its Python-specific features make it an excellent choice for Flask applications, especially for developers who want a simple deployment process.

The free tier is suitable for small projects and testing, while paid plans offer more resources and features like custom domains and always-on tasks.

## Resources

- [PythonAnywhere Help Pages](https://help.pythonanywhere.com/)
- [PythonAnywhere Forums](https://www.pythonanywhere.com/forums/)
- [Python Web Application Documentation](../../README.md)
- [Flask on PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/)
