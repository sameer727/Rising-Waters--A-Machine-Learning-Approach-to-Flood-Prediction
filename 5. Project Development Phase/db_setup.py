import os
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_DIR = 'data'
DATABASE_PATH = os.path.join(DATABASE_DIR, 'flood_prediction.db')

def setup_database():
    # Ensure data directory exists
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        print(f"Created directory: {DATABASE_DIR}")

    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 1. Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        User_Name TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL,
        Role TEXT NOT NULL,
        Phone_Number TEXT,
        Organization TEXT,
        Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
        Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Create weather_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        Weather_Data_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        User_ID INTEGER,
        Annual_Rainfall REAL NOT NULL,
        Seasonal_Rainfall REAL NOT NULL,
        Cloud_Cover REAL NOT NULL,
        Humidity REAL NOT NULL,
        Temperature REAL NOT NULL,
        River_Water_Level REAL NOT NULL,
        Drainage_Capacity REAL NOT NULL,
        Water_Flow REAL NOT NULL,
        Reservoir_Level REAL NOT NULL,
        Soil_Moisture REAL NOT NULL,
        Date TEXT NOT NULL,
        Time TEXT NOT NULL,
        Location TEXT NOT NULL,
        Prediction_Status TEXT NOT NULL,
        FOREIGN KEY (User_ID) REFERENCES users(User_ID) ON DELETE SET NULL
    )
    ''')

    # 3. Create predictions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        Prediction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        User_ID INTEGER,
        Weather_Data_ID INTEGER,
        Prediction INTEGER NOT NULL,
        Probability REAL NOT NULL,
        Confidence TEXT NOT NULL,
        Prediction_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (User_ID) REFERENCES users(User_ID) ON DELETE SET NULL,
        FOREIGN KEY (Weather_Data_ID) REFERENCES weather_data(Weather_Data_ID) ON DELETE CASCADE
    )
    ''')

    # Seed a default Admin user if none exists
    cursor.execute("SELECT * FROM users WHERE Email = 'admin@flood.com'")
    admin_exists = cursor.fetchone()

    if not admin_exists:
        hashed_password = generate_password_hash('admin')
        cursor.execute('''
        INSERT INTO users (User_Name, Email, Password, Role, Phone_Number, Organization)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Admin', 'admin@flood.com', hashed_password, 'Admin', '+919999999999', 'Flood Response Authority'))
        print("Default admin user created successfully (admin@flood.com / admin).")
    else:
        print("Admin user already exists in database.")

    conn.commit()
    conn.close()
    print(f"Database setup complete. SQLite database saved to: {DATABASE_PATH}")

if __name__ == '__main__':
    setup_database()
