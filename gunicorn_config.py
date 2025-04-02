"""
Gunicorn configuration file for the Python Web Application.
This file contains settings for the Gunicorn WSGI server in production.
"""

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'pythonweb'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = 'logs/gunicorn-error.log'
accesslog = 'logs/gunicorn-access.log'
loglevel = 'info'

# Process hooks
def on_starting(server):
    """
    Called just before the master process is initialized.
    """
    pass

def on_reload(server):
    """
    Called before a worker is reloaded.
    """
    pass

def when_ready(server):
    """
    Called just after the server is started.
    """
    # Create log directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """
    Called just prior to forking the worker subprocess.
    """
    pass

def pre_exec(server):
    """
    Called just prior to forking off a secondary
    master process during things like config reloading.
    """
    pass

def worker_int(worker):
    """
    Called just after a worker exited on SIGINT or SIGQUIT.
    """
    pass

def worker_abort(worker):
    """
    Called when a worker received the SIGABRT signal.
    """
    pass

def worker_exit(server, worker):
    """
    Called just after a worker has been exited, in the worker process.
    """
    pass

def child_exit(server, worker):
    """
    Called just after a worker has been exited, in the master process.
    """
    pass
