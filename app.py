from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
import traceback

load_dotenv()

app = Flask(__name__)

# Configuration
ADAFRUIT_USERNAME = os.getenv('MQTT_USERNAME')
ADAFRUIT_KEY = os.getenv('MQTT_KEY')
ADAFRUIT_IO_URL = f'https://io.adafruit.com/api/v2/{ADAFRUIT_USERNAME}'

# Database configuration (Neon.tech PostgreSQL)
DATABASE_URL = os.getenv('DATABASE_URL')

print(f"=== APP STARTUP ===")
print(f"DATABASE_URL configured: {DATABASE_URL is not None}")
print(f"ADAFRUIT configured: {ADAFRUIT_USERNAME is not None}")


def get_db_connection():
    """Create a database connection"""
    try:
        print(f"Attempting database connection...")
        conn = psycopg.connect(DATABASE_URL)
        print(f"✓ Database connected successfully")
        return conn
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        traceback.print_exc()
        return None


def get_adafruit_feed_data(feed_key):
    """Fetch latest data from Adafruit IO feed"""
    try:
        headers = {'X-AIO-Key': ADAFRUIT_KEY}
        response = requests.get(
            f'{ADAFRUIT_IO_URL}/feeds/{feed_key}/data/last',
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching Adafruit data: {e}")
        return None


def send_adafruit_command(feed_key, value):
    """Send command to Adafruit IO feed"""
    try:
        headers = {
            'X-AIO-Key': ADAFRUIT_KEY,
            'Content-Type': 'application/json'
        }
        data = {'value': str(value)}
        response = requests.post(
            f'{ADAFRUIT_IO_URL}/feeds/{feed_key}/data',
            headers=headers,
            json=data,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending command: {e}")
        return False


@app.route('/')
def index():
    """Home page / Main Dashboard"""
    return render_template('index.html')


@app.route('/chart')
def chart():
    """Chart page for historical data"""
    return render_template('chart.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/status')
def status():
    """System Status page"""
    return render_template('status.html')

@app.route('/controls')
def controls():
    """Device Controls page"""
    return render_template('controls.html')

# API Endpoints

@app.route('/api/live-data')
def get_live_data():
    """Get live data from Adafruit IO for multiple sensors"""
    try:
        # Fetch data from Adafruit IO feeds
        alarm_status = get_adafruit_feed_data('status')
        temperature = get_adafruit_feed_data('temperature')
        humidity = get_adafruit_feed_data('humidity')

        return jsonify({
            'success': True,
            'data': {
                'alarm_status': alarm_status.get('value') if alarm_status else 'unknown',
                'temperature': float(temperature.get('value')) if temperature else None,
                'humidity': float(humidity.get('value')) if humidity else None,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/historical-data')
def get_historical_data():
    """Get historical sensor data from database for a specific date (returns all records for today)"""
    date = request.args.get('date')
    sensor = request.args.get('sensor', 'temperature')

    print(f"\n=== HISTORICAL DATA REQUEST ===")
    print(f"Date: {date}")
    print(f"Sensor: {sensor}")

    if not date:
        return jsonify({'success': False, 'error': 'Date parameter required'}), 400

    # Validate sensor type
    if sensor not in ['temperature', 'humidity']:
        return jsonify({'success': False, 'error': 'Invalid sensor type'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            print("✗ Database connection failed")
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Since we only have TIME column, fetch all records and return them
        # This will show the pattern for a typical day
        query = f"""
            SELECT time, value 
            FROM {sensor} 
            ORDER BY time ASC
        """

        print(f"Executing query: {query}")

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"✓ Query executed successfully")
        print(f"Rows returned: {len(results)}")

        cursor.close()
        conn.close()

        # Format data for Chart.js
        data = {
            'labels': [row['time'].strftime('%H:%M:%S') for row in results],
            'values': [float(row['value']) for row in results]
        }

        print(f"✓ Response data formatted")
        return jsonify({'success': True, 'data': data})

    except Exception as e:
        print(f"✗ ERROR in historical-data: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/daily-averages')
def get_daily_averages():
    """Get all sensor data points with exact timestamps"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sensor = request.args.get('sensor', 'temperature')

    print(f"\n=== DAILY DATA REQUEST ===")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"Sensor: {sensor}")

    if not start_date or not end_date:
        return jsonify({'success': False, 'error': 'Start and end dates required'}), 400

    # Validate sensor type
    if sensor not in ['temperature', 'humidity']:
        return jsonify({'success': False, 'error': 'Invalid sensor type'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            print("✗ Database connection failed")
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Get all data points with their exact time
        query = f"""
            SELECT time, value
            FROM {sensor} 
            ORDER BY time ASC
        """

        print(f"Executing query: {query}")

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"✓ Query executed successfully")
        print(f"Rows returned: {len(results)}")

        if results:
            print(f"Sample row: {results[0]}")

        cursor.close()
        conn.close()

        # Format data for Chart.js - showing all data points with exact times
        data = {
            'labels': [row['time'].strftime('%H:%M:%S') for row in results],
            'values': [float(row['value']) for row in results]
        }

        print(f"✓ Response data formatted: {len(data['labels'])} data points")
        return jsonify({'success': True, 'data': data})

    except Exception as e:
        print(f"✗ ERROR in daily-data: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/daily-alerts')
def get_daily_alerts():
    """Get alert counts grouped by hour"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    print(f"\n=== DAILY ALERTS REQUEST ===")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")

    if not start_date or not end_date:
        return jsonify({'success': False, 'error': 'Start and end dates required'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            print("✗ Database connection failed")
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Since we only have TIME, group by hour to show alert pattern
        query = """
            SELECT 
                EXTRACT(HOUR FROM time) as hour,
                COUNT(*) as alert_count
            FROM status 
            WHERE value = 'alert' OR value = 'armed'
            GROUP BY EXTRACT(HOUR FROM time)
            ORDER BY hour ASC
        """

        print(f"Executing query: {query}")

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"✓ Query executed successfully")
        print(f"Rows returned: {len(results)}")

        if results:
            print(f"Sample row: {results[0]}")

        cursor.close()
        conn.close()

        # Format data for Chart.js - showing hourly alert counts
        data = {
            'labels': [f"{int(row['hour']):02d}:00" for row in results],
            'values': [int(row['alert_count']) for row in results]
        }

        print(f"✓ Response data formatted: {len(data['labels'])} data points")
        return jsonify({'success': True, 'data': data})

    except Exception as e:
        print(f"✗ ERROR in daily-alerts: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/intrusions')
def get_intrusions():
    """Get intrusion/alert events"""
    date = request.args.get('date')

    if not date:
        return jsonify({'success': False, 'error': 'Date parameter required'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Query alert events from status table (all records since we don't have dates)
        query = """
            SELECT time, value 
            FROM status 
            WHERE value = 'alert'
            ORDER BY time DESC
            LIMIT 50
        """
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        intrusions = [{
            'timestamp': row['time'].strftime('%H:%M:%S'),
            'event_type': 'alert' if row['value'] == 'alert' else 'armed',
            'details': f"System status: {row['value']}"
        } for row in results]

        return jsonify({'success': True, 'data': intrusions})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/control', methods=['POST'])
def control_device():
    """Control devices via Adafruit IO"""
    data = request.get_json()

    if not data or 'device' not in data or 'action' not in data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400

    device = data['device']
    action = data['action']

    # Map device names to Adafruit IO feed names
    device_feeds = {
        'system': 'system',
        'screen': 'screen',
        'light': 'light',
        'buzzer': 'buzzer',
        'clock': 'clock',
        'dht': 'dht'
    }

    if device not in device_feeds:
        return jsonify({'success': False, 'error': 'Unknown device'}), 400

    feed_key = device_feeds[device]

    # Send command to Adafruit IO
    success = send_adafruit_command(feed_key, action)

    if success:
        return jsonify({'success': True, 'message': f'Command sent to {device}'})
    else:
        return jsonify({'success': False, 'error': 'Failed to send command'}), 500


@app.route('/api/security-toggle', methods=['POST'])
def toggle_security():
    """Enable/disable security system"""
    data = request.get_json()

    if not data or 'enabled' not in data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400

    enabled = data['enabled']
    value = 'armed' if enabled else 'disarmed'

    success = send_adafruit_command('status', value)

    if success:
        return jsonify({'success': True, 'message': f'Security system {"enabled" if enabled else "disabled"}'})
    else:
        return jsonify({'success': False, 'error': 'Failed to toggle security system'}), 500


@app.route('/api/system-status')
def get_system_status():
    """Get current system status"""
    try:
        alarm_status = get_adafruit_feed_data('status')
        temperature = get_adafruit_feed_data('temperature')
        humidity = get_adafruit_feed_data('humidity')

        return jsonify({
            'success': True,
            'status': {
                'alarm': alarm_status.get('value') if alarm_status else 'unknown',
                'temperature': float(temperature.get('value')) if temperature else None,
                'humidity': float(humidity.get('value')) if humidity else None,
                'last_update': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)