import os
import json
import sqlite3
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from functools import wraps
from flask import Flask, request, redirect, render_template, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '7b4e8d2c9a1f5e6a3d8b0c2e9f1a7d6e8b0a2f4c')

# Load the saved model, scaler, and state label encoder
MODEL_PATH = 'models/flood_model.pkl'
SCALER_PATH = 'models/scaler.save'
ENCODER_PATH = 'models/state_encoder.save'
DATABASE_PATH = 'data/flood_prediction.db'

if os.environ.get('VERCEL'):
    DATABASE_PATH = '/tmp/flood_prediction.db'
    if not os.path.exists(DATABASE_PATH):
        import shutil
        os.makedirs('/tmp', exist_ok=True)
        src_db = os.path.join(os.path.dirname(__file__), 'data', 'flood_prediction.db')
        if os.path.exists(src_db):
            try:
                shutil.copy2(src_db, DATABASE_PATH)
                print("Database copied to /tmp successfully.")
            except Exception as e:
                print(f"Error copying database: {e}")

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("Model and scaler successfully loaded.")
except Exception as e:
    print(f"Error loading assets: {e}")
    model = None
    scaler = None

try:
    state_encoder = joblib.load(ENCODER_PATH)
    print("State encoder loaded.")
except Exception:
    state_encoder = None

# List of states supported by the model
STATES = sorted([
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 
    'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu & Kashmir', 
    'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 
    'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 
    'Uttarakhand', 'West Bengal'
])

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash("Access denied: Unauthorized organization role.", "error")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Explainable AI (XAI) text generator
def generate_explanation(inputs, prediction, prob):
    explanations = []
    if prediction == 1:
        explanations.append("A localized flood warning is in effect.")
        if inputs['River_Water_Level'] > 8.0:
            explanations.append(f"River stage heights are dangerously high at {inputs['River_Water_Level']:.1f} meters (critical threshold is typically 7-8m).")
        if inputs['Water_Flow'] > 800:
            explanations.append(f"Surface discharge/water flow rate is extremely elevated at {inputs['Water_Flow']:.0f} cumecs.")
        if inputs['Soil_Moisture'] > 80:
            explanations.append(f"Soil moisture saturation is at {inputs['Soil_Moisture']:.0f}%, preventing further infiltration and inducing high surface runoff.")
        if inputs['Drainage_Capacity'] < 40:
            explanations.append(f"Regional drainage and runoff capacity is low/constrained at {inputs['Drainage_Capacity']:.0f}%, causing rapid street pooling.")
        if inputs['Seasonal_Rainfall'] > 1800:
            explanations.append(f"Accumulated seasonal monsoon rainfall of {inputs['Seasonal_Rainfall']:.0f}mm has overloaded natural water channels.")
        if not explanations:
            explanations.append("Elevated climate and precipitation indicators cumulatively exceed the local safety threshold.")
    else:
        explanations.append("No active flood hazard has been detected.")
        if inputs['Soil_Moisture'] < 60:
            explanations.append(f"Soil retention capacity is healthy with soil moisture at {inputs['Soil_Moisture']:.0f}%.")
        if inputs['River_Water_Level'] < 5.0:
            explanations.append(f"River levels are well within safe margins at {inputs['River_Water_Level']:.1f} meters.")
        if inputs['Drainage_Capacity'] > 60:
            explanations.append(f"Regional drainage and storage capacity is active at {inputs['Drainage_Capacity']:.0f}% to buffer runoff.")
    return " ".join(explanations)

# Route Handlers
@app.route('/')
def home():
    """Renders home.html (Landing page)"""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user account registration"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        user_name = request.form.get('User_Name')
        email = request.form.get('Email')
        password = request.form.get('Password')
        role = request.form.get('Role')
        phone = request.form.get('Phone_Number')
        org = request.form.get('Organization')
        
        if role == 'Normal User':
            org = 'General Public'
            
        if not user_name or not email or not password or not role or (role != 'Normal User' and not org):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('register'))
            
        if role not in ['Meteorologist', 'Disaster Management Officer', 'Local Authority', 'Normal User']:
            flash("Unauthorized registration role requested.", "error")
            return redirect(url_for('register'))
            
        conn = get_db_connection()
        user_exists = conn.execute('SELECT * FROM users WHERE Email = ?', (email,)).fetchone()
        
        if user_exists:
            flash("Email address is already registered.", "error")
            conn.close()
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (User_Name, Email, Password, Role, Phone_Number, Organization)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_name, email, hashed_password, role, phone, org))
        conn.commit()
        conn.close()
        
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication and session setup"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')
        remember = request.form.get('Remember')
        
        if not email or not password:
            flash("Please enter both email and password.", "error")
            return redirect(url_for('login'))
            
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE Email = ?', (email,)).fetchone()
        conn.close()
        
        if not user or not check_password_hash(user['Password'], password):
            flash("Invalid email or password.", "error")
            return redirect(url_for('login'))
            
        session.clear()
        session['user_id'] = user['User_ID']
        session['user_name'] = user['User_Name']
        session['role'] = user['Role']
        
        if remember:
            session.permanent = True
            app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7 # 7 days
        else:
            session.permanent = False
            
        flash("Logged in successfully.", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clears user session and logs out"""
    session.clear()
    flash("You have logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Renders user home portal with stats summaries"""
    conn = get_db_connection()
    user_id = session['user_id']
    user = conn.execute('SELECT * FROM users WHERE User_ID = ?', (user_id,)).fetchone()
    
    if session['role'] == 'Admin':
        stats = {
            'total_runs': conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
        }
    else:
        stats = {
            'total_runs': conn.execute('SELECT COUNT(*) FROM predictions WHERE User_ID = ?', (user_id,)).fetchone()[0]
        }
    conn.close()
    return render_template('dashboard.html', user=user, stats=stats)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handles view/update of account credentials and password"""
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = session['user_id']
        
        if action == 'update_profile':
            user_name = request.form.get('User_Name')
            phone = request.form.get('Phone_Number')
            org = request.form.get('Organization')
            
            if not user_name:
                flash("Name is required.", "error")
            else:
                conn.execute('''
                    UPDATE users 
                    SET User_Name = ?, Phone_Number = ?, Organization = ?, Updated_At = CURRENT_TIMESTAMP
                    WHERE User_ID = ?
                ''', (user_name, phone, org, user_id))
                conn.commit()
                session['user_name'] = user_name
                flash("Profile details updated successfully.", "success")
                
        elif action == 'update_password':
            curr_pw = request.form.get('Current_Password')
            new_pw = request.form.get('New_Password')
            
            user = conn.execute('SELECT * FROM users WHERE User_ID = ?', (user_id,)).fetchone()
            if not check_password_hash(user['Password'], curr_pw):
                flash("Current password is incorrect.", "error")
            elif len(new_pw) < 6:
                flash("New password must be at least 6 characters.", "error")
            else:
                conn.execute('''
                    UPDATE users 
                    SET Password = ?, Updated_At = CURRENT_TIMESTAMP
                    WHERE User_ID = ?
                ''', (generate_password_hash(new_pw), user_id))
                conn.commit()
                flash("Password updated successfully.", "success")
                
        conn.close()
        return redirect(url_for('profile'))
        
    user = conn.execute('SELECT * FROM users WHERE User_ID = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/history')
@login_required
def history():
    """Display predictions run history log based on role authorizations"""
    conn = get_db_connection()
    role = session['role']
    user_id = session['user_id']
    
    if role in ['Admin', 'Disaster Management Officer']:
        query = '''
            SELECT p.Prediction_ID, p.Prediction, p.Probability, p.Confidence, p.Prediction_Date,
                   w.Annual_Rainfall, w.Seasonal_Rainfall, w.Cloud_Cover, w.Humidity, w.Temperature,
                   w.River_Water_Level, w.Drainage_Capacity, w.Water_Flow, w.Reservoir_Level, w.Soil_Moisture,
                   w.Date, w.Time, w.Location, u.User_Name, u.Role
            FROM predictions p
            JOIN weather_data w ON p.Weather_Data_ID = w.Weather_Data_ID
            LEFT JOIN users u ON p.User_ID = u.User_ID
            ORDER BY p.Prediction_Date DESC
        '''
        predictions = conn.execute(query).fetchall()
    else:
        query = '''
            SELECT p.Prediction_ID, p.Prediction, p.Probability, p.Confidence, p.Prediction_Date,
                   w.Annual_Rainfall, w.Seasonal_Rainfall, w.Cloud_Cover, w.Humidity, w.Temperature,
                   w.River_Water_Level, w.Drainage_Capacity, w.Water_Flow, w.Reservoir_Level, w.Soil_Moisture,
                   w.Date, w.Time, w.Location, u.User_Name, u.Role
            FROM predictions p
            JOIN weather_data w ON p.Weather_Data_ID = w.Weather_Data_ID
            LEFT JOIN users u ON p.User_ID = u.User_ID
            WHERE p.User_ID = ?
            ORDER BY p.Prediction_Date DESC
        '''
        predictions = conn.execute(query, (user_id,)).fetchall()
        
    conn.close()
    return render_template('prediction_history.html', predictions=predictions)

@app.route('/manage-users', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def manage_users():
    """Admin-only panel to manage organization roles and delete accounts"""
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        target_user_id = request.form.get('user_id')
        
        if target_user_id == str(session['user_id']):
            flash("You cannot modify or delete your own admin account.", "error")
        else:
            if action == 'update_role':
                new_role = request.form.get('role')
                if new_role in ['Admin', 'Meteorologist', 'Disaster Management Officer', 'Local Authority']:
                    conn.execute('UPDATE users SET Role = ?, Updated_At = CURRENT_TIMESTAMP WHERE User_ID = ?', (new_role, target_user_id))
                    conn.commit()
                    flash(f"User role updated to {new_role}.", "success")
                else:
                    flash("Invalid role assignment.", "error")
            elif action == 'delete_user':
                conn.execute('DELETE FROM users WHERE User_ID = ?', (target_user_id,))
                conn.commit()
                flash("User profile successfully deleted from database.", "success")
                
        conn.close()
        return redirect(url_for('manage_users'))
        
    users = conn.execute('SELECT * FROM users ORDER BY Created_At DESC').fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)

@app.route('/model-dashboard')
@login_required
@role_required(['Admin'])
def model_dashboard():
    """Admin-only access to classifier comparisons and performance plots"""
    meta_path = 'models/model_meta.json'
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
    else:
        meta = {
            "best_model": "XGBoost",
            "test_metrics": {"Accuracy": 0.9773},
            "all_models_comparison": {
                "XGBoost": {"Accuracy": 0.9773},
                "Random Forest": {"Accuracy": 0.9770},
                "Decision Tree": {"Accuracy": 0.9481}
            }
        }
    return render_template('model_dashboard.html', meta=meta)

# Prediction Interfaces (RBAC Guarded)
@app.route('/Predict')
@login_required
@role_required(['Admin', 'Meteorologist', 'Local Authority', 'Normal User'])
def predict():
    """Renders early warning inputs interface"""
    return render_template('index.html', states=STATES)

@app.route('/chance')
@login_required
@role_required(['Admin', 'Meteorologist', 'Local Authority', 'Normal User'])
def chance():
    """Renders danger warnings result"""
    prob = request.args.get('prob', '100.0')
    return render_template('chance.html', prob=prob)

@app.route('/no_chance')
@login_required
@role_required(['Admin', 'Meteorologist', 'Local Authority', 'Normal User'])
def no_chance():
    """Renders safe status result"""
    prob = request.args.get('prob', '0.0')
    return render_template('no_chance.html', prob=prob)

@app.route('/api/predict', methods=['POST'])
@login_required
@role_required(['Admin', 'Meteorologist', 'Local Authority', 'Normal User'])
def api_predict():
    """Asynchronous AJAX endpoint for model run and DB persistent logging"""
    if model is None or scaler is None:
        return jsonify({"success": False, "error": "Machine learning pipeline is not loaded."}), 500
        
    try:
        data = request.get_json(force=True)
        inputs_dict = {
            'Annual_Rainfall': float(data.get('Annual_Rainfall')),
            'Seasonal_Rainfall': float(data.get('Seasonal_Rainfall')),
            'Cloud_Cover': float(data.get('Cloud_Cover')),
            'Humidity': float(data.get('Humidity')),
            'Temperature': float(data.get('Temperature')),
            'River_Water_Level': float(data.get('River_Water_Level')),
            'Drainage_Capacity': float(data.get('Drainage_Capacity')),
            'Water_Flow': float(data.get('Water_Flow')),
            'Reservoir_Level': float(data.get('Reservoir_Level')),
            'Soil_Moisture': float(data.get('Soil_Moisture'))
        }
        location = data.get('State', 'Custom Region')
    except (TypeError, ValueError, AttributeError) as e:
        return jsonify({"success": False, "error": f"Invalid input formats: {e}"}), 400

    features = [
        'Annual Rainfall', 'Seasonal Rainfall', 'Cloud Cover', 'Humidity', 
        'Temperature', 'River Water Level', 'Drainage Capacity', 'Water Flow', 
        'Reservoir Level', 'Soil Moisture'
    ]
    
    input_df = pd.DataFrame([[
        inputs_dict['Annual_Rainfall'],
        inputs_dict['Seasonal_Rainfall'],
        inputs_dict['Cloud_Cover'],
        inputs_dict['Humidity'],
        inputs_dict['Temperature'],
        inputs_dict['River_Water_Level'],
        inputs_dict['Drainage_Capacity'],
        inputs_dict['Water_Flow'],
        inputs_dict['Reservoir_Level'],
        inputs_dict['Soil_Moisture']
    ]], columns=features)
    
    try:
        input_scaled = scaler.transform(input_df)
        input_scaled_df = pd.DataFrame(input_scaled, columns=features)
        prediction = int(model.predict(input_scaled_df)[0])
        
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(input_scaled_df)[0]
            flood_probability = float(probabilities[1]) * 100
        else:
            flood_probability = 100.0 if prediction == 1 else 0.0
    except Exception as e:
        return jsonify({"success": False, "error": f"Model inference error: {e}"}), 500
        
    prob_val = round(flood_probability, 1)
    explanation = generate_explanation(inputs_dict, prediction, prob_val)
    confidence = "High" if prob_val > 85 or prob_val < 15 else "Medium"
    
    # Persistent SQL Database Logging
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        pred_status = "Flood Risk" if prediction == 1 else "Stable"
        
        # 1. Log weather parameters
        cursor.execute('''
            INSERT INTO weather_data (
                User_ID, Annual_Rainfall, Seasonal_Rainfall, Cloud_Cover, Humidity, Temperature,
                River_Water_Level, Drainage_Capacity, Water_Flow, Reservoir_Level, Soil_Moisture,
                Date, Time, Location, Prediction_Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            inputs_dict['Annual_Rainfall'],
            inputs_dict['Seasonal_Rainfall'],
            inputs_dict['Cloud_Cover'],
            inputs_dict['Humidity'],
            inputs_dict['Temperature'],
            inputs_dict['River_Water_Level'],
            inputs_dict['Drainage_Capacity'],
            inputs_dict['Water_Flow'],
            inputs_dict['Reservoir_Level'],
            inputs_dict['Soil_Moisture'],
            datetime.now().strftime('%Y-%m-%d'),
            datetime.now().strftime('%H:%M:%S'),
            location,
            pred_status
        ))
        weather_data_id = cursor.lastrowid
        
        # 2. Log predictions run record
        cursor.execute('''
            INSERT INTO predictions (
                User_ID, Weather_Data_ID, Prediction, Probability, Confidence
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            weather_data_id,
            prediction,
            prob_val,
            confidence
        ))
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"Database logging failure: {db_err}")

    return jsonify({
        "success": True,
        "prediction": prediction,
        "probability": prob_val,
        "explanation": explanation,
        "confidence": confidence,
        "model_name": "XGBoost"
    })

@app.route('/predict_submit', methods=['POST'])
@login_required
@role_required(['Admin', 'Meteorologist', 'Local Authority', 'Normal User'])
def predict_submit():
    """Traditional form submission endpoint with DB persistent logging"""
    if model is None or scaler is None:
        return "Error: Machine learning pipeline is not loaded.", 500
        
    try:
        annual_rainfall = float(request.form.get('Annual_Rainfall'))
        seasonal_rainfall = float(request.form.get('Seasonal_Rainfall'))
        cloud_cover = float(request.form.get('Cloud_Cover'))
        humidity = float(request.form.get('Humidity'))
        temperature = float(request.form.get('Temperature'))
        river_water_level = float(request.form.get('River_Water_Level'))
        drainage_capacity = float(request.form.get('Drainage_Capacity'))
        water_flow = float(request.form.get('Water_Flow'))
        reservoir_level = float(request.form.get('Reservoir_Level'))
        soil_moisture = float(request.form.get('Soil_Moisture'))
        location = request.form.get('State', 'Custom Region')
    except (TypeError, ValueError) as e:
        return redirect(url_for('predict'))
        
    features = [
        'Annual Rainfall', 'Seasonal Rainfall', 'Cloud Cover', 'Humidity', 
        'Temperature', 'River Water Level', 'Drainage Capacity', 'Water Flow', 
        'Reservoir Level', 'Soil Moisture'
    ]
    
    input_df = pd.DataFrame([[
        annual_rainfall,
        seasonal_rainfall,
        cloud_cover,
        humidity,
        temperature,
        river_water_level,
        drainage_capacity,
        water_flow,
        reservoir_level,
        soil_moisture
    ]], columns=features)
    
    try:
        input_scaled = scaler.transform(input_df)
        input_scaled_df = pd.DataFrame(input_scaled, columns=features)
        prediction = int(model.predict(input_scaled_df)[0])
        
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(input_scaled_df)[0]
            flood_probability = float(probabilities[1]) * 100
        else:
            flood_probability = 100.0 if prediction == 1 else 0.0
    except Exception as e:
        return redirect(url_for('predict'))
        
    prob_val = round(flood_probability, 1)
    confidence = "High" if prob_val > 85 or prob_val < 15 else "Medium"
    
    # Persistent SQL Database Logging
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        pred_status = "Flood Risk" if prediction == 1 else "Stable"
        
        # 1. Log weather parameters
        cursor.execute('''
            INSERT INTO weather_data (
                User_ID, Annual_Rainfall, Seasonal_Rainfall, Cloud_Cover, Humidity, Temperature,
                River_Water_Level, Drainage_Capacity, Water_Flow, Reservoir_Level, Soil_Moisture,
                Date, Time, Location, Prediction_Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            annual_rainfall,
            seasonal_rainfall,
            cloud_cover,
            humidity,
            temperature,
            river_water_level,
            drainage_capacity,
            water_flow,
            reservoir_level,
            soil_moisture,
            datetime.now().strftime('%Y-%m-%d'),
            datetime.now().strftime('%H:%M:%S'),
            location,
            pred_status
        ))
        weather_data_id = cursor.lastrowid
        
        # 2. Log predictions run record
        cursor.execute('''
            INSERT INTO predictions (
                User_ID, Weather_Data_ID, Prediction, Probability, Confidence
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            weather_data_id,
            prediction,
            prob_val,
            confidence
        ))
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"Database logging failure: {db_err}")

    if prediction == 1:
        return redirect(url_for('chance', prob=prob_val))
    else:
        return redirect(url_for('no_chance', prob=prob_val))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
