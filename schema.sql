-- Database Schema for IoT Home Security System

-- Table for sensor data (temperature, humidity, light, etc.)
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sensor_type VARCHAR(50) NOT NULL,
    value DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries by date and sensor type
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX idx_sensor_data_sensor_type ON sensor_data(sensor_type);
CREATE INDEX idx_sensor_data_date ON sensor_data(DATE(timestamp));

-- Table for security events (alerts, intrusions, system state changes)
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL,
    details TEXT,
    image_path VARCHAR(255),
    video_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries by date and event type
CREATE INDEX idx_security_events_timestamp ON security_events(timestamp);
CREATE INDEX idx_security_events_event_type ON security_events(event_type);
CREATE INDEX idx_security_events_date ON security_events(DATE(timestamp));

-- Table for device control logs
CREATE TABLE IF NOT EXISTS device_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX idx_device_logs_timestamp ON device_logs(timestamp);
CREATE INDEX idx_device_logs_device_name ON device_logs(device_name);

-- Table for system status
CREATE TABLE IF NOT EXISTS system_status (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alarm_status VARCHAR(50),
    last_armed TIMESTAMP,
    last_disarmed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View for daily sensor statistics
CREATE OR REPLACE VIEW daily_sensor_stats AS
SELECT 
    DATE(timestamp) as date,
    sensor_type,
    MIN(value) as min_value,
    MAX(value) as max_value,
    AVG(value) as avg_value,
    COUNT(*) as reading_count
FROM sensor_data
GROUP BY DATE(timestamp), sensor_type
ORDER BY date DESC, sensor_type;

-- View for daily security summary
CREATE OR REPLACE VIEW daily_security_summary AS
SELECT 
    DATE(timestamp) as date,
    event_type,
    COUNT(*) as event_count
FROM security_events
GROUP BY DATE(timestamp), event_type
ORDER BY date DESC, event_type;

-- Example queries for testing:

-- Insert sample sensor data
-- INSERT INTO sensor_data (sensor_type, value, unit) VALUES 
-- ('temperature', 22.5, '°C'),
-- ('humidity', 65.0, '%'),
-- ('light', 450, 'lux');

-- Insert sample security event
-- INSERT INTO security_events (event_type, details) VALUES 
-- ('alert', 'Motion detected in living room');

-- Query sensor data for a specific date
-- SELECT * FROM sensor_data 
-- WHERE DATE(timestamp) = '2025-12-01' 
-- AND sensor_type = 'temperature'
-- ORDER BY timestamp ASC;

-- Query intrusions for a specific date
-- SELECT * FROM security_events 
-- WHERE DATE(timestamp) = '2025-12-01' 
-- AND event_type IN ('alert', 'intrusion')
-- ORDER BY timestamp DESC;
