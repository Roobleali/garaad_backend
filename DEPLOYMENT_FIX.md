# Fix: Switch from Gunicorn to Daphne

## Problem
Your Nginx config is correct, but you're using **Gunicorn which CANNOT handle WebSockets**. You need to use **Daphne** (which is already in your Dockerfile).

---

## Solution: Replace Gunicorn with Daphne

### Step 1: Create Daphne systemd service

SSH into your server and create `/etc/systemd/system/daphne.service`:

```bash
sudo nano /etc/systemd/system/daphne.service
```

Paste this content:

```ini
[Unit]
Description=Daphne ASGI Server for Garaad Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/garaad_backend
Environment="PATH=/var/www/garaad_backend/venv/bin"
ExecStart=/var/www/garaad_backend/venv/bin/daphne -u /var/www/garaad_backend/daphne.sock garaad.asgi:application
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Step 2: Update Nginx to use Daphne socket

Edit your Nginx config:

```bash
sudo nano /etc/nginx/sites-available/api.garaad.org
```

Change this line:
```nginx
proxy_pass http://unix:/var/www/garaad_backend/gunicorn.sock;
```

To:
```nginx
proxy_pass http://unix:/var/www/garaad_backend/daphne.sock;
```

### Step 3: Stop Gunicorn, Start Daphne

```bash
# Stop and disable Gunicorn
sudo systemctl stop gunicorn
sudo systemctl disable gunicorn

# Enable and start Daphne
sudo systemctl enable daphne
sudo systemctl start daphne

# Check status
sudo systemctl status daphne

# Reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Step 4: Verify it works

Check the logs:
```bash
sudo journalctl -u daphne -f
```

You should see:
```
Starting Daphne ASGI Server...
Listening on Unix socket /var/www/garaad_backend/daphne.sock
```

---

## Your Final Nginx Config (Already Correct!)

Your current Nginx config already has the WebSocket headers, just needs to point to Daphne:

```nginx
server {
    server_name api.garaad.org 167.172.108.123;

    location /static/ {
        root /var/www/garaad_backend;
    }

    location /media/ {
        alias /home/root/garaad_backend/media/;
    }

    location / {
        # CHANGE THIS LINE TO USE DAPHNE
        proxy_pass http://unix:/var/www/garaad_backend/daphne.sock;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/api.garaad.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.garaad.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 80;
    server_name api.garaad.org 167.172.108.123;
    return 301 https://$host$request_uri;
}
```

---

## After Deployment

WebSockets will connect successfully and you'll see in your Django logs:
```
WebSocket Auth Success: abdishakuuralimohamed
User abdishakuuralimohamed connecting to community_1748720433271
```

The "Cannot read properties of undefined (reading 'id')" error will also be fixed because the frontend will receive proper data via WebSocket.
