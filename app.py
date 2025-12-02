from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

app = Flask(__name__)

# Configuration
ADAFRUIT_USERNAME = os.getenv('MQTT_USERNAME')
ADAFRUIT_KEY = os.getenv('MQTT_KEY')
ADAFRUIT_IO_URL = f'https://io.adafruit.com/api/v2/{ADAFRUIT_USERNAME}'

# Database configuration (Neon.tech PostgreSQL)
DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
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
    """Get historical sensor data from database for a specific date"""
    date = request.args.get('date')
    sensor = request.args.get('sensor', 'temperature')

    if not date:
        return jsonify({'success': False, 'error': 'Date parameter required'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Query historical data for the specified date and sensor
        query = """
            SELECT timestamp, value 
            FROM sensor_data 
            WHERE DATE(timestamp) = %s AND sensor_type = %s
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (date, sensor))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        # Format data for Chart.js
        data = {
            'labels': [row['timestamp'].strftime('%H:%M:%S') for row in results],
            'values': [float(row['value']) for row in results]
        }

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/daily-averages')
def get_daily_averages():
    """Get daily average sensor data for a date range"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sensor = request.args.get('sensor', 'temperature')

    if not start_date or not end_date:
        return jsonify({'success': False, 'error': 'Start and end dates required'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Query daily averages
        query = """
            SELECT DATE(timestamp) as date, AVG(value) as avg_value
            FROM sensor_data 
            WHERE DATE(timestamp) BETWEEN %s AND %s AND sensor_type = %s
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) ASC
        """
        cursor.execute(query, (start_date, end_date, sensor))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        # Format data for Chart.js
        data = {
            'labels': [row['date'].strftime('%Y-%m-%d') for row in results],
            'values': [float(row['avg_value']) for row in results]
        }

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/daily-alerts')
def get_daily_alerts():
    """Get daily alert counts for a date range"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({'success': False, 'error': 'Start and end dates required'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Query daily alert counts
        query = """
            SELECT DATE(timestamp) as date, COUNT(*) as alert_count
            FROM security_events 
            WHERE DATE(timestamp) BETWEEN %s AND %s AND event_type IN ('alert', 'intrusion')
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) ASC
        """
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        # Format data for Chart.js
        data = {
            'labels': [row['date'].strftime('%Y-%m-%d') for row in results],
            'values': [int(row['alert_count']) for row in results]
        }

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/intrusions')
def get_intrusions():
    """Get intrusion events for a specific date"""
    date = request.args.get('date')

    if not date:
        return jsonify({'success': False, 'error': 'Date parameter required'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(row_factory=dict_row)

        # Query intrusion events
        query = """
            SELECT timestamp, event_type, details 
            FROM security_events 
            WHERE DATE(timestamp) = %s AND event_type IN ('alert', 'intrusion')
            ORDER BY timestamp DESC
        """
        cursor.execute(query, (date,))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        intrusions = [{
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'event_type': row['event_type'],
            'details': row.get('details', '')
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