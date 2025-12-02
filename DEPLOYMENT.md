# Deployment Guide - Render.com

This guide walks you through deploying the DomSafe Flask app on Render.com (free tier).

## Prerequisites

- GitHub account
- Render.com account (free)
- Neon.tech PostgreSQL database (free tier)
- Adafruit IO account

## Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
```bash
cd flask_app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/domsafe-flask.git
git push -u origin main
```

2. **Ensure these files are in your repository**:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `templates/` directory with all HTML files
   - `.env.example` (do NOT commit `.env`)

## Step 2: Set Up Neon.tech Database

1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project: "domsafe-db"
3. Copy the connection string (starts with `postgresql://`)
4. In Neon dashboard, go to SQL Editor
5. Paste and run the contents of `schema.sql`
6. Verify tables are created

## Step 3: Deploy on Render.com

### Create Web Service

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `domsafe-flask`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Set Environment Variables

In the Render dashboard, go to "Environment" tab and add:

```
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=<generate-a-random-secret-key>

MQTT_USERNAME=<your-adafruit-username>
MQTT_KEY=<your-adafruit-io-key>

DATABASE_URL=<your-neon-database-url>

MQTT_HOST=io.adafruit.com
MQTT_PORT=1883
MQTT_TIMEOUT=60
TOPICS=alarm-status,temperature

LED_BLINK_INTERVAL=0.5
DETECTION_DELAY=10
ALARM_DELAY=15
```

### Generate Secret Key

Use Python to generate a secure secret key:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 4: Configure Adafruit IO

1. Go to [io.adafruit.com](https://io.adafruit.com)
2. Create the following feeds:
   - `alarm-status`
   - `temperature`
   - `humidity` (optional)
   - `light` (optional)
   - `living-room-light`
   - `bedroom-fan`
   - `garage-door`

3. Get your credentials:
   - Click yellow key icon for "My Key"
   - Copy Username and Active Key
   - Update Render environment variables

## Step 5: Deploy

1. Click "Create Web Service" in Render
2. Wait for deployment (5-10 minutes)
3. Once deployed, you'll get a URL like: `https://domsafe-flask.onrender.com`

## Step 6: Configure Raspberry Pi

Update your Raspberry Pi to sync with cloud database:

```bash
# On Raspberry Pi, update .env file
nano ~/iot-home-defense-system/.env

# Add this line:
DATABASE_URL=<your-neon-database-url>
```

Set up automatic sync (optional):
```bash
# Create sync script
nano ~/sync_to_cloud.sh
```

Add:
```bash
#!/bin/bash
cd ~/iot-home-defense-system/flask_app
python3 sync_data.py
```

Make executable and add to cron:
```bash
chmod +x ~/sync_to_cloud.sh

# Add to crontab (sync every hour)
crontab -e

# Add this line:
0 * * * * /home/pi/sync_to_cloud.sh >> /home/pi/sync.log 2>&1
```

## Step 7: Test Deployment

1. Visit your Render URL: `https://domsafe-flask.onrender.com`
2. Check all pages load correctly
3. Test live data endpoint: `https://domsafe-flask.onrender.com/api/live-data`
4. Test device control from the web interface

## Troubleshooting

### "Application Error" on Render

Check logs in Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Look for error messages

Common issues:
- Missing environment variables
- Database connection string incorrect
- Python dependencies not installed

### Database Connection Fails

Verify connection string:
```python
# Test locally
python -c "import psycopg2; conn = psycopg2.connect('YOUR_URL'); print('OK')"
```

### Adafruit IO Not Working

Test API key:
```bash
curl -H "X-AIO-Key: YOUR_KEY" https://io.adafruit.com/api/v2/YOUR_USERNAME/feeds
```

### Free Tier Limitations

Render free tier:
- App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- 750 hours/month free

To keep alive (optional):
- Use a service like UptimeRobot to ping every 14 minutes
- Or upgrade to paid tier ($7/month)

## Alternative: Deploy Locally

If you prefer to run on Raspberry Pi:

```bash
# On Raspberry Pi
cd ~/iot-home-defense-system/flask_app

# Install dependencies
pip3 install -r requirements.txt

# Run with gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Create systemd service:
```bash
sudo nano /etc/systemd/system/domsafe-web.service
```

Add:
```ini
[Unit]
Description=DomSafe Flask Web App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/iot-home-defense-system/flask_app
Environment="PATH=/home/pi/iot-home-defense-system/venv/bin"
ExecStart=/home/pi/iot-home-defense-system/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable domsafe-web
sudo systemctl start domsafe-web
```

Access at: `http://<raspberry-pi-ip>:5000`

## Security Considerations

1. **Use HTTPS**: Render provides free SSL
2. **Secure your API keys**: Never commit `.env` to GitHub
3. **Database**: Use strong passwords
4. **Rate limiting**: Consider adding Flask-Limiter for production
5. **Authentication**: Add user login for sensitive controls

## Monitoring

Set up monitoring:
1. Render provides basic metrics in dashboard
2. Use UptimeRobot for uptime monitoring
3. Set up alerts in Neon.tech for database issues
4. Monitor Adafruit IO feed usage

## Support

If you encounter issues:
1. Check Render logs
2. Verify all environment variables
3. Test database connection
4. Test Adafruit IO API
5. Review error messages carefully

## Next Steps

- Add user authentication
- Implement WebSocket for real-time updates
- Add more sensors and devices
- Create mobile app
- Set up automated backups
