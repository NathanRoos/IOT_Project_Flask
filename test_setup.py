"""
Test Script
Verify Flask app configuration and connections
"""

import os
import sys
from dotenv import load_dotenv

def test_env_variables():
    """Test if all required environment variables are set"""
    print("Testing environment variables...")
    load_dotenv()
    
    required_vars = [
        'MQTT_USERNAME',
        'MQTT_KEY',
        'DATABASE_URL'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            print(f"  ❌ {var} is not set")
        else:
            print(f"  ✓ {var} is set")
    
    if missing:
        print(f"\n⚠️  Missing variables: {', '.join(missing)}")
        print("Please update your .env file")
        return False
    
    print("\n✅ All environment variables are set!\n")
    return True

def test_database():
    """Test database connection"""
    print("Testing database connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"  ✓ Connected to: {version[0][:50]}...")
        cursor.close()
        conn.close()
        print("✅ Database connection successful!\n")
        return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}\n")
        return False

def test_adafruit_io():
    """Test Adafruit IO connection"""
    print("Testing Adafruit IO connection...")
    try:
        import requests
        username = os.getenv('MQTT_USERNAME')
        key = os.getenv('MQTT_KEY')
        
        headers = {'X-AIO-Key': key}
        response = requests.get(
            f'https://io.adafruit.com/api/v2/{username}/feeds',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            feeds = response.json()
            print(f"  ✓ Connected to Adafruit IO")
            print(f"  ✓ Found {len(feeds)} feeds")
            print("✅ Adafruit IO connection successful!\n")
            return True
        else:
            print(f"  ❌ Failed with status code: {response.status_code}\n")
            return False
    except Exception as e:
        print(f"  ❌ Adafruit IO connection failed: {e}\n")
        return False

def test_flask_import():
    """Test if Flask can be imported"""
    print("Testing Flask import...")
    try:
        from app import app
        print("  ✓ Flask app imported successfully")
        print("✅ Flask is working!\n")
        return True
    except Exception as e:
        print(f"  ❌ Failed to import Flask app: {e}\n")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("DomSafe Flask App - Configuration Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Environment Variables", test_env_variables()))
    results.append(("Database Connection", test_database()))
    results.append(("Adafruit IO Connection", test_adafruit_io()))
    results.append(("Flask Import", test_flask_import()))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("🎉 All tests passed! Your Flask app is ready to run.")
        print("\nNext steps:")
        print("1. Run the app: python app.py")
        print("2. Open browser: http://localhost:5000")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
