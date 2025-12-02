# Sentrix Alarm - IoT Home Automation and Security System

A comprehensive Flask web application for monitoring and controlling your IoT home security system with real-time sensor data, historical analytics, and remote device control.

## 🎯 Project Overview

Sentrix Alarm is a full-stack IoT security system that combines Raspberry Pi sensors, cloud connectivity via Adafruit IO, and a modern web interface to provide comprehensive home monitoring and control capabilities. This project was developed as part of the IoT Design and Prototyping course at Champlain College Saint-Lambert.

### Key Features

- **📊 Real-Time Monitoring**: Live sensor data updates every 5 seconds
- **📈 Historical Analytics**: Chart.js visualizations with date-range selection
- **🔒 Security Management**: Arm/disarm system, view intrusion logs
- **🎛️ Device Control**: Remote control of smart home devices
- **☁️ Cloud Integration**: Adafruit IO MQTT and PostgreSQL database
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## 🏗️ Architecture

```
┌─────────────────────┐
│   Raspberry Pi      │
│   (IoT Backend)     │
│   - DHT Sensors     │
│   - PIR Motion      │
│   - Camera Module   │
└──────────┬──────────┘
           │
           ├────────────► Adafruit IO (MQTT)
           │              - Live data feeds
           │              - Device commands
           │
           └────────────► Neon.tech PostgreSQL
                          - Historical data
                          - Security events
                          - Device logs
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Flask Web App        │
                    │   (This Application)   │
                    │   - RESTful API        │
                    │   - Real-time updates  │
                    │   - Chart.js graphs    │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   User Browser         │
                    │   - Dashboard          │
                    │   - Controls           │
                    │   - Analytics          │
                    └────────────────────────┘
```

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Contributing](#-contributing)
- [Team](#-team)

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone <your-repo-url>
cd flask_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Setup database
psql $DATABASE_URL -f schema.sql

# Test configuration
python test_setup.py

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser.

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database (Neon.tech recommended for free tier)
- Adafruit IO account (free tier available)
- Active Raspberry Pi with IoT sensors (optional for development)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd flask_app
```

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The following packages will be installed:
- `Flask==3.0.0` - Web framework
- `python-dotenv==1.0.0` - Environment variable management
- `requests==2.31.0` - HTTP requests for Adafruit IO
- `psycopg[binary]==3.2.2` - PostgreSQL adapter
- `gunicorn==21.2.0` - Production WSGI server

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Adafruit IO Configuration
MQTT_USERNAME=your_adafruit_username
MQTT_KEY=your_adafruit_io_key

# Database Configuration (Neon.tech PostgreSQL)
DATABASE_URL=postgresql://username:password@host/database?sslmode=require

# MQTT Configuration
MQTT_HOST=io.adafruit.com
MQTT_PORT=1883
MQTT_TIMEOUT=60
TOPICS=alarm-status,temperature
```

### Database Setup

#### Using Neon.tech (Recommended)

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project: "sentrix-alarm-db"
3. Copy the connection string
4. Update `DATABASE_URL` in `.env`
5. Run the schema:

```bash
psql $DATABASE_URL -f schema.sql
```

#### Database Schema

The application uses the following tables:
- `sensor_data` - Temperature, humidity, light readings
- `security_events` - Alerts, intrusions, state changes
- `device_logs` - Device control history
- `system_status` - Current system state

### Adafruit IO Setup

#### Create Feeds

1. Go to [io.adafruit.com](https://io.adafruit.com)
2. Create the following feeds:
   - `status` - System alarm status
   - `temperature` - Temperature readings
   - `humidity` - Humidity readings
   - `system` - System control
   - `screen` - Display control
   - `light` - Light control
   - `buzzer` - Buzzer control
   - `clock` - Clock display
   - `dht` - DHT sensor control

#### Get API Credentials

1. Click on "My Key" (yellow key icon)
2. Copy your Username and Active Key
3. Update `.env` with these credentials

## 🎮 Usage

### Running the Application

#### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:5000`

#### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Web Interface

#### Dashboard (`/`)
- Real-time temperature, humidity, and system status
- Auto-refreshing every 5 seconds
- Live status indicators

#### System Status (`/status`)
- Current alarm status with descriptions
- Live sensor readings
- Status history

#### Device Controls (`/controls`)
- Toggle system devices on/off
- Control system, screen, lights, buzzer, clock, DHT sensor
- Real-time status updates

#### Analytics Chart (`/chart`)
- Historical temperature data by hour
- Historical humidity data by hour
- Emergency alert counts by hour
- Interactive date range selection
- Chart.js line and bar graphs

#### About (`/about`)
- Project information
- Team members
- Technologies used
- Feature list

## 📡 API Documentation

### Endpoints

#### `GET /api/live-data`
Fetch current sensor readings from Adafruit IO

**Response:**
```json
{
  "success": true,
  "data": {
    "alarm_status": "disarmed",
    "temperature": 22.5,
    "humidity": 65.0,
    "timestamp": "2025-12-02T14:30:00"
  }
}
```

#### `GET /api/historical-data?date=YYYY-MM-DD&sensor=temperature`
Fetch historical data for a specific sensor

**Parameters:**
- `date` - Date in YYYY-MM-DD format
- `sensor` - Sensor type (`temperature` or `humidity`)

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

#### `GET /api/daily-averages?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&sensor=temperature`
Get all sensor data points with exact timestamps

**Parameters:**
- `start_date` - Start date in YYYY-MM-DD format
- `end_date` - End date in YYYY-MM-DD format
- `sensor` - Sensor type (`temperature` or `humidity`)

**Response:**
```json
{
  "success": true,
  "data": {
    "labels": ["14:00:00", "15:00:00", "16:00:00"],
    "values": [22.5, 23.1, 22.8]
  }
}
```

#### `GET /api/daily-alerts?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
Get alert counts grouped by hour

**Response:**
```json
{
  "success": true,
  "data": {
    "labels": ["00:00", "01:00", "02:00"],
    "values": [0, 1, 0]
  }
}
```

#### `GET /api/intrusions?date=YYYY-MM-DD`
Get intrusion events for a specific date

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "14:30:15",
      "event_type": "alert",
      "details": "System status: alert"
    }
  ]
}
```

#### `POST /api/control`
Control a device

**Request:**
```json
{
  "device": "system",
  "action": "ON"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Command sent to system"
}
```

#### `POST /api/security-toggle`
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

#### `GET /api/system-status`
Get current system status

**Response:**
```json
{
  "success": true,
  "status": {
    "alarm": "disarmed",
    "temperature": 22.5,
    "humidity": 65.0,
    "last_update": "2025-12-02T14:30:00"
  }
}
```

## 🌐 Deployment

### Option 1: Render.com (Recommended)

1. Push code to GitHub
2. Create account at [render.com](https://render.com)
3. Create new Web Service
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Add environment variables in Render dashboard
7. Deploy

Detailed instructions: See [DEPLOYMENT.md](DEPLOYMENT.md)

### Option 2: Heroku

```bash
heroku login
heroku create sentrix-alarm
git push heroku main
heroku config:set MQTT_USERNAME=your_username
heroku config:set MQTT_KEY=your_key
heroku config:set DATABASE_URL=your_database_url
```

### Option 3: Local Raspberry Pi

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv

# Create systemd service
sudo nano /etc/systemd/system/sentrix-alarm.service
```

Add:
```ini
[Unit]
Description=Sentrix Alarm Flask Web App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/flask_app
Environment="PATH=/home/pi/flask_app/venv/bin"
ExecStart=/home/pi/flask_app/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sentrix-alarm
sudo systemctl start sentrix-alarm
```

## 📁 Project Structure

```
flask_app/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── schema.sql                  # Database structure
├── sync_data.py               # Data synchronization script
├── test_setup.py              # Setup verification tool
├── Procfile                   # Deployment configuration
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── templates/                 # HTML templates
│   ├── base.html             # Base layout with navigation
│   ├── index.html            # Dashboard page
│   ├── status.html           # System status page
│   ├── controls.html         # Device control page
│   ├── chart.html            # Analytics charts page
│   └── about.html            # About page
│
├── README.md                  # This file
├── DEPLOYMENT.md              # Deployment guide
├── QUICKSTART.md              # Quick start guide
└── IMPLEMENTATION_SUMMARY.md  # Project summary
```

## 🛠️ Technologies

### Backend
- **Flask 3.0.0** - Web framework
- **Python 3.8+** - Programming language
- **PostgreSQL** - Database (Neon.tech)
- **Psycopg 3.2.2** - PostgreSQL adapter
- **Gunicorn 21.2.0** - WSGI HTTP server

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling (Custom gradient design)
- **JavaScript (ES6+)** - Interactivity
- **Chart.js** - Data visualization

### IoT & Cloud
- **Adafruit IO** - MQTT broker and data feeds
- **MQTT** - IoT messaging protocol
- **Raspberry Pi** - IoT hardware platform
- **DHT22** - Temperature/humidity sensor
- **PIR** - Motion sensor

### Development Tools
- **python-dotenv** - Environment management
- **Git** - Version control
- **Virtual Environment** - Dependency isolation

## 🧪 Testing

Run the setup verification script:

```bash
python test_setup.py
```

This will test:
- Environment variables configuration
- Database connection
- Adafruit IO connection
- Flask import

## 🔧 Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python -c "import psycopg; conn = psycopg.connect('YOUR_DATABASE_URL'); print('Connected!')"
```

### Adafruit IO Connection Issues

```bash
# Test Adafruit IO API
curl -H "X-AIO-Key: YOUR_KEY" https://io.adafruit.com/api/v2/YOUR_USERNAME/feeds
```

### Port Already in Use

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Module Not Found

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📊 Features Checklist

- ✅ Real-time sensor data monitoring
- ✅ Historical data visualization with Chart.js
- ✅ Security system control (arm/disarm)
- ✅ Device control interface
- ✅ Intrusion event logging
- ✅ Responsive design (mobile-friendly)
- ✅ RESTful API endpoints
- ✅ Cloud database integration
- ✅ MQTT connectivity
- ✅ Auto-refresh capabilities

## 👥 Team

- **Nathan Roos** - Developer
- **Louis Caron** - Developer
- **Alhickel Hichri** - Teacher/Supervisor

## 🎓 Course Information

- **Course**: 420-N55: IoT Design and Prototyping
- **Institution**: Champlain College Saint-Lambert
- **Semester**: Fall 2025

## 📄 License

This project is developed for educational purposes as part of the IoT Design and Prototyping course at Champlain College Saint-Lambert.

## 🙏 Acknowledgments

- Adafruit IO for providing free IoT platform services
- Neon.tech for PostgreSQL database hosting
- Chart.js for data visualization library
- Flask community for excellent documentation

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
3. Consult [QUICKSTART.md](QUICKSTART.md) for setup help
4. Contact the development team

## 🚀 Future Enhancements

- [ ] User authentication (Flask-Login)
- [ ] WebSocket for instant updates
- [ ] Mobile app (React Native)
- [ ] Email/SMS notifications
- [ ] Video streaming integration
- [ ] Voice control (Alexa/Google)
- [ ] Machine learning for anomaly detection
- [ ] Multi-user support with roles

---

**Built with ❤️ by Nathan Roos & Louis Caron**

*Champlain College Saint-Lambert - Fall 2025*
