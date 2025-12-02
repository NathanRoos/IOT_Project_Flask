"""
Data Sync Script
Synchronizes local CSV log files with cloud PostgreSQL database
"""

import csv
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class DataSync:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.logs_dir = Path(__file__).resolve().parents[1] / 'backend' / 'logs'
        
    def get_db_connection(self):
        """Create database connection"""
        try:
            conn = psycopg2.connect(self.db_url, sslmode='require')
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def sync_sensor_data(self, date_str):
        """Sync sensor data from CSV to database"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        synced_count = 0
        
        # Sync temperature data
        temp_file = self.logs_dir / f"{date_str}_temperature.csv"
        if temp_file.exists():
            with open(temp_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        timestamp = datetime.strptime(f"{date_str} {row['timestamp']}", "%Y-%m-%d %H:%M:%S")
                        value = float(row['message'])
                        
                        cursor.execute("""
                            INSERT INTO sensor_data (timestamp, sensor_type, value, unit)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (timestamp, 'temperature', value, '°C'))
                        synced_count += cursor.rowcount
                    except Exception as e:
                        print(f"Error syncing temperature row: {e}")
        
        # You can add more sensors here (humidity, light, etc.)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Synced {synced_count} sensor readings for {date_str}")
        return True
    
    def sync_security_events(self, date_str):
        """Sync security events from CSV to database"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        synced_count = 0
        
        # Sync alarm status changes
        alarm_file = self.logs_dir / f"{date_str}_alarm-status.csv"
        if alarm_file.exists():
            with open(alarm_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        timestamp = datetime.strptime(f"{date_str} {row['timestamp']}", "%Y-%m-%d %H:%M:%S")
                        status = row['message']
                        
                        # Log state changes as security events
                        event_type = 'state_change'
                        if status == 'alert':
                            event_type = 'alert'
                        
                        cursor.execute("""
                            INSERT INTO security_events (timestamp, event_type, details)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (timestamp, event_type, f"System {status}"))
                        synced_count += cursor.rowcount
                    except Exception as e:
                        print(f"Error syncing security event: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Synced {synced_count} security events for {date_str}")
        return True
    
    def sync_today(self):
        """Sync today's data"""
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"Syncing data for {today}...")
        self.sync_sensor_data(today)
        self.sync_security_events(today)
    
    def sync_date_range(self, start_date, end_date):
        """Sync data for a date range"""
        from datetime import timedelta
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            print(f"\nSyncing data for {date_str}...")
            self.sync_sensor_data(date_str)
            self.sync_security_events(date_str)
            current += timedelta(days=1)

def main():
    """Main function"""
    import sys
    
    sync = DataSync()
    
    if len(sys.argv) == 1:
        # No arguments - sync today
        sync.sync_today()
    elif len(sys.argv) == 2:
        # Single date argument
        date = sys.argv[1]
        print(f"Syncing data for {date}...")
        sync.sync_sensor_data(date)
        sync.sync_security_events(date)
    elif len(sys.argv) == 3:
        # Date range
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        print(f"Syncing data from {start_date} to {end_date}...")
        sync.sync_date_range(start_date, end_date)
    else:
        print("Usage:")
        print("  python sync_data.py                    # Sync today's data")
        print("  python sync_data.py 2025-12-01         # Sync specific date")
        print("  python sync_data.py 2025-12-01 2025-12-07  # Sync date range")

if __name__ == '__main__':
    main()
