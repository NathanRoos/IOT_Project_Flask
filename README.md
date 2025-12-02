# DomSafe Flask Web Application

Web interface for the IoT Home Automation and Security System.

## Features

- **Live Data Monitoring**: Real-time sensor data from Adafruit IO
- **Historical Data Visualization**: Chart.js graphs for temperature, humidity, and light levels
- **Security Management**: Enable/disable system, view intrusion logs
- **Device Control**: Control smart home devices remotely
- **Responsive Design**: Works on desktop, tablet, and mobile

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (Neon.tech recommended)
- Adafruit IO account
- Active Raspberry Pi system running the IoT backend

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd flask_app
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update with your credentials:

```env
# Adafruit IO
MQTT_USERNAME=your_adafruit_username
MQTT_KEY=your_adafruit_io_key

# Database (Neon.tech)
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```

### 5. Set Up Database

Connect to your PostgreSQL database and run the schema:

```bash
psql $DATABASE_URL -f schema.sql
```

Or use a database GUI tool and execute the `schema.sql` file.

## Running the Application

### Development Mode

```bash
python app.py
```

Access the app at `http://localhost:5000`

### Production Mode (with Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Deployment Options

### Option 1: Render.com (Recommended)

1. Create account at [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Set environment variables in Render dashboard
5. Deploy

### Option 2: Heroku

```bash
# Install Heroku CLI
heroku login
heroku create your-app-name
git push heroku main
```

### Option 3: Local Raspberry Pi

```bash
# Install and configure on Raspberry Pi
sudo apt update
sudo apt install python3-pip python3-venv
# Follow installation steps above
# Use systemd service for auto-start
```

## API Endpoints

### GET `/api/live-data`
Fetch current sensor readings from Adafruit IO

**Response:**
```json
{
  "success": true,
  "data": {
    "alarm_status": "disarmed",
    "temperature": 22.5,
    "timestamp": "2025-12-01T14:30:00"
  }
}
```

### GET `/api/historical-data?date=YYYY-MM-DD&sensor=temperature`
Fetch historical data for a specific date and sensor

**Response:**
```json
{
  "success": true,
  "data": {
    "labels": ["14:00:00", "14:05:00", "14:10:00"],
    "values": [22.5, 22.7, 23.0]
  }
}
```

### GET `/api/intrusions?date=YYYY-MM-DD`
Get intrusion events for a specific date

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2025-12-01 14:30:15",
      "event_type": "alert",
      "details": "Motion detected"
    }
  ]
}
```

### POST `/api/control`
Control a device

**Request:**
```json
{
  "device": "living-room-light",
  "action": "ON"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Command sent to living-room-light"
}
```

### POST `/api/security-toggle`
Enable/disable security system

**Request:**
```json
{
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Security system enabled"
}
```

## Database Setup

### Neon.tech (Recommended)

1. Sign up at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string
4. Update `DATABASE_URL` in `.env`
5. Run `schema.sql` to create tables

### Alternative: Supabase

1. Sign up at [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → Database
4. Copy connection string
5. Update `DATABASE_URL` in `.env`

## Connecting to Adafruit IO

### Setup Feeds

Create the following feeds in your Adafruit IO dashboard:

1. `alarm-status` - System state (disarmed, armed, alert)
2. `temperature` - Temperature readings
3. `living-room-light` - Light control
4. `bedroom-fan` - Fan control
5. `garage-door` - Garage door control

### Get API Key

1. Go to Adafruit IO
2. Click on "My Key" (yellow key icon)
3. Copy "Username" and "Active Key"
4. Update `.env` file

## Project Structure

```
flask_app/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── schema.sql             # Database schema
├── .env.example           # Environment variables template
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Dashboard/home page
│   ├── environmental.html # Environmental monitoring
│   ├── security.html     # Security management
│   ├── devices.html      # Device control
│   └── about.html        # About page
└── README.md             # This file
```

## Troubleshooting

### Database Connection Issues

```python
# Test database connection
python -c "import psycopg2; conn = psycopg2.connect('YOUR_DATABASE_URL'); print('Connected!')"
```

### Adafruit IO Connection Issues

```python
# Test Adafruit IO API
curl -H "X-AIO-Key: YOUR_KEY" https://io.adafruit.com/api/v2/YOUR_USERNAME/feeds
```

### CORS Issues

If accessing from different domain, add CORS support:

```bash
pip install flask-cors
```

```python
from flask_cors import CORS
CORS(app)
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is part of the IoT Design and Prototyping course at Champlain College.

## Team

- Nathan Roos
- Louis Caron

## Course Information

- **Course**: 420-N55: IoT Design and Prototyping
- **Professor**: Prof. Haikel Hichri
- **Institution**: Champlain College Saint-Lambert
- **Semester**: Fall 2025
