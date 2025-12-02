# Quick Start Guide

Get your DomSafe Flask app running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Neon.tech account (free)
- [ ] Adafruit IO account (free)

## Step 1: Clone and Setup (2 minutes)

```bash
# Navigate to your project
cd ~/iot-home-defense-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd flask_app
pip install -r requirements.txt
```

## Step 2: Configure Environment (2 minutes)

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

Required values:
- `MQTT_USERNAME`: Your Adafruit IO username
- `MQTT_KEY`: Your Adafruit IO key (found at io.adafruit.com/YOUR_USERNAME/keys)
- `DATABASE_URL`: Your Neon.tech PostgreSQL connection string

## Step 3: Setup Database (1 minute)

```bash
# Connect to your Neon.tech database and run:
psql YOUR_DATABASE_URL -f schema.sql

# Or copy/paste schema.sql into Neon.tech SQL Editor
```

## Step 4: Test Setup

```bash
python test_setup.py
```

If all tests pass, you're ready!

## Step 5: Run the App

```bash
python app.py
```

Open browser: http://localhost:5000

## Quick Checks

### ✓ Homepage loads
Visit http://localhost:5000

### ✓ Live data works
Check if temperature is updating on dashboard

### ✓ Device control works
Try turning a device on/off

### ✓ Historical data works
Go to Environmental page, select a date, click Load Data

## Common Issues

### "Database connection failed"
- Check your DATABASE_URL in .env
- Verify you ran schema.sql
- Test connection: `psql YOUR_DATABASE_URL -c "SELECT 1"`

### "Adafruit IO connection failed"
- Verify MQTT_USERNAME and MQTT_KEY in .env
- Check feeds exist at io.adafruit.com
- Test: `curl -H "X-AIO-Key: YOUR_KEY" https://io.adafruit.com/api/v2/YOUR_USERNAME/feeds`

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

### "No data showing"
- Make sure your Raspberry Pi is running and sending data
- Check Adafruit IO dashboard for incoming data
- Run sync_data.py to populate database: `python sync_data.py`

## Next Steps

1. **Deploy to Production**: See DEPLOYMENT.md
2. **Customize**: Modify templates to match your branding
3. **Add Features**: Add more sensors, devices, or pages
4. **Secure**: Add authentication (Flask-Login)

## File Structure Reference

```
flask_app/
├── app.py              # Main Flask application
├── templates/          # HTML pages
│   ├── base.html      # Navigation and layout
│   ├── index.html     # Dashboard
│   ├── environmental.html
│   ├── security.html
│   ├── devices.html
│   └── about.html
├── requirements.txt   # Python dependencies
├── schema.sql        # Database structure
├── sync_data.py      # Sync local CSVs to cloud
└── .env             # Your credentials (DON'T COMMIT!)
```

## Development Tips

### Auto-reload on changes
```bash
export FLASK_ENV=development
python app.py
```

### View detailed errors
Enable debug mode (development only!):
```python
# In app.py
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Test API endpoints
```bash
# Get live data
curl http://localhost:5000/api/live-data

# Control device
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"device":"living-room-light","action":"ON"}'
```

## Need Help?

1. Check README.md for detailed documentation
2. Review DEPLOYMENT.md for production setup
3. Run test_setup.py to diagnose issues
4. Check Render/Neon/Adafruit IO dashboards for logs

## Success!

If you see the dashboard with live data, congratulations! Your Flask app is working.

Now you can:
- Monitor your home security system
- View environmental data
- Control smart devices
- Review security events
- Access everything from anywhere!

Happy monitoring! 🏠🔒
