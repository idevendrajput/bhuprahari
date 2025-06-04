Bhuprahari Backend (Python Flask)
1. Introduction
The Bhuprahari Backend is a Python Flask web service powering a land change detection and alert system. It integrates with Google Maps Static API for imagery, uses OpenCV for image comparison, manages area configurations, handles user authentication with JWTs, stores data in MySQL, and sends real-time alerts via Firebase Cloud Messaging. It acts as the core intelligence for monitoring land for unauthorized changes.

2. Features
User Authentication: Secure registration and login with JWT for API authorization.

Area Configuration: Define and manage geographical areas for monitoring.

Automated Image Capture: Periodically captures satellite imagery tiles from Google Maps.

Image Comparison: Utilizes OpenCV to detect visual changes between images.

Change Detection Alerts: Records detected changes in the database.

Real-time Notifications: Sends FCM alerts upon monitoring session completion if changes are detected.

Scheduled Monitoring: Automates capture and comparison using APScheduler.

Data Persistence: Stores all data in a MySQL database.

RESTful API: Provides endpoints for frontend integration.

3. API Endpoints
All API endpoints are prefixed with /api/.

Authentication
POST /api/auth/register: Register a new user.

POST /api/auth/login: Authenticate user, get JWT tokens.

Area Configuration
POST /api/area-configs: Create a new monitoring area. (Auth required)

GET /api/area-configs: Retrieve all defined areas. (Auth required)

GET /api/area-configs/{config_id}: Retrieve a specific area by ID. (Auth required)

Image Monitoring & Alerts
POST /api/monitor/capture/{area_config_id}: Manually trigger image capture for an area. (Auth required)

POST /api/monitor/compare/{area_config_id}: Manually trigger image comparison for an area. (Auth required)

GET /api/monitor/image-tiles/area/{area_config_id}: Retrieve historical image tiles for an area. (Auth required)

GET /api/alerts/sessions: Retrieve all past monitoring sessions. (Auth required)

GET /api/alerts/sessions/{session_id}/details: Retrieve details for a specific alert session. (Auth required)

4. Database Schema
The backend uses MySQL. Tables include users, area_configs, image_tiles, alert_sessions, and alert_details. The detailed CREATE TABLE statements are available in the project files.

5. Local Development Setup
Prerequisites
Python 3.10+

pip, venv

MySQL Server (running locally)

Steps
Clone/Copy Project:

git clone <your-repo-url>
cd bhuprahari_backend_python/flaskapp

Create & Activate Virtual Environment:

python3 -m venv venv
source venv/bin/activate

Install Dependencies:

pip install -r requirements.txt
# For OpenCV: sudo apt install libgl1-mesa-glx -y

Create captured_images directory: mkdir captured_images

Place Firebase Service Account Key: Download your Firebase JSON key to flaskapp/ root.

Configure config.py: Update database URI, API keys, JWT secret, Firebase path, FCM token, and cron expression for local testing.

Initialize Database Tables:

python3 -c "from app import app, db; db.init_app(app); with app.app_context(): db.create_all()"

Run with Gunicorn:

gunicorn --workers 3 --bind 127.0.0.1:3308 app:app

6. Deployment to Ubuntu VPS
This section outlines the process for deploying the Flask application to an Ubuntu VPS using Gunicorn and Nginx.

Prerequisites (on VPS)
Ubuntu 22.04+

SSH access, sudo privileges

Python 3.10+, pip, venv

MySQL Server

Nginx

Steps
Initial Setup:

Connect via SSH.

sudo apt update && sudo apt upgrade -y

Configure UFW: sudo ufw allow OpenSSH 'Nginx HTTP'

Install Python, pip, venv, Nginx if not present.

MySQL Setup:

Install MySQL Server: sudo apt install mysql-server -y

Run sudo mysql_secure_installation.

Create bhuprahari database and bhuprahari_user with password and grant privileges.

Application Files:

Create project directory: mkdir ~/bhuprahari_app && cd ~/bhuprahari_app

Copy flaskapp directory: scp -r /path/to/local/flaskapp your_username@your_vps_ip_address:~/bhuprahari_app/

Navigate to flaskapp: cd ~/bhuprahari_app/flaskapp

Create & Activate Venv: python3 -m venv venv && source venv/bin/activate

Install Dependencies: pip install -r requirements.txt (and sudo apt install libgl1-mesa-glx -y for OpenCV).

Configure config.py for production (absolute paths, strong JWT secret, production API keys).

Place Firebase JSON Key in flaskapp/ root.

Create captured_images directory: mkdir -p captured_images

Initialize DB Tables:

python3 -c "from app import app, db; db.init_app(app); with app.app_context(): db.create_all()"

Gunicorn Configuration:

Install Gunicorn: pip install gunicorn

Create Systemd service file: sudo nano /etc/systemd/system/bhuprahari.service

[Unit]
Description=Gunicorn instance for Bhuprahari
After=network.target

[Service]
User=your_username # Or root
Group=www-data     # Or root
WorkingDirectory=/home/your_username/bhuprahari_app/flaskapp
ExecStart=/home/your_username/bhuprahari_app/flaskapp/venv/bin/gunicorn --workers 3 --bind unix:/home/your_username/bhuprahari_app/flaskapp/bhuprahari.sock -m 007 app:app
Restart=always

[Install]
WantedBy=multi-user.target

Reload & Start: sudo systemctl daemon-reload && sudo systemctl start bhuprahari && sudo systemctl enable bhuprahari

Nginx Configuration:

Create Nginx config: sudo nano /etc/nginx/sites-available/bhuprahari

server {
    listen 80;
    server_name your_domain.com your_vps_ip_address;

    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        include proxy_params;
        proxy_pass http://unix:/home/your_username/bhuprahari_app/flaskapp/bhuprahari.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static_images/ {
        alias /home/your_username/bhuprahari_app/flaskapp/captured_images/;
        try_files $uri $uri/ =404;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ =404;
    }
}

Enable & Restart: sudo ln -s /etc/nginx/sites-available/bhuprahari /etc/nginx/sites-enabled/ sudo rm /etc/nginx/sites-enabled/default sudo nginx -t && sudo systemctl restart nginx

7. Troubleshooting
Refer to the comprehensive troubleshooting guide in the project documentation for common issues and solutions.

8. Future Enhancements
HTTPS/SSL for secure communication.

Dedicated error logging.

Scalability improvements (load balancing, containerization).

Database migrations.

Admin interface.

Advanced image comparison algorithms.

Dynamic FCM tokens for targeted notifications.
