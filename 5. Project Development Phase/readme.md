# 🌊 ML-Based Flood Prediction & Early Warning System

A production-ready Web Application and Machine Learning pipeline designed to predict flood risks and provide early warnings based on meteorological and hydrological data. Built with Python, Flask, and XGBoost, the application is optimized for Serverless deployment on Vercel and version-tracked on GitHub.

---

## 🚀 Live Demo & Deployment
This project is fully structured and configured for automatic deployment on **Vercel** via GitHub integration.
- **Model Size**: Optimized down to **~483KB** (480x reduction) to fit within Vercel's Serverless Function size limits.
- **Database**: Configured with an ephemeral `/tmp/flood_prediction.db` SQLite fallback for serverless execution.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.12+ / Flask (Jinja2 Templates)
- **Database**: SQLite (Local & Serverless Ephemeral)
- **Machine Learning**: 
  - Model: XGBoost Classifier
  - Processing: Pandas, NumPy, Scikit-Learn
  - Feature Scaling: StandardScaler
- **Frontend**: Vanilla HTML5, CSS3, and JS (Custom UI with interactive prediction forms and data dashboards)

---

## 📈 Machine Learning Pipeline

The application features a training and evaluation pipeline (`train.py`) that compares multiple classifiers:
1. **Decision Tree Classifier** (Accuracy: ~94.98%)
2. **Random Forest Classifier** (Accuracy: ~97.60%)
3. **XGBoost Classifier** (Accuracy: ~97.14%)

### Model Selection
For local development, the best model is Random Forest. However, due to Vercel's strict **250MB** uncompressed size limit, the Random Forest model's size (234MB) is prohibitive.
We selected **XGBoost** as the production classifier, reducing model file size to **483KB** (a 480x reduction) while retaining **97.14%** accuracy.

---

## 🖥️ Application Features

### 🔐 User Authentication & RBAC
- Role-Based Access Control (RBAC) supporting **Admin**, **Meteorologist**, **Local Authority**, and **Normal User**.
- Secure password hashing using `werkzeug.security`.

### 🔮 Interactive Predictions
- Input weather parameters (Rainfall, Temperature, Soil Moisture, River Levels, etc.).
- Real-time model inference showing prediction status, probability, confidence level, and Explainable AI (XAI) text outputs explaining why the prediction was made.

### 📊 Admin Portal & History Logs
- View past weather predictions logged in the database.
- Admin-only access to model performance comparisons, including ROC curves and feature importances.

---

## 📥 Local Setup & Installation

### 1. Clone & Set Up Environment
```bash
# Clone the repository
git clone https://github.com/sameer727/Flood-Prediction.git
cd Flood-Prediction

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database & Train Model
```bash
# Run database setup to seed default admin (admin@flood.com / admin)
python db_setup.py

# Retrain the model and generate production model files
python train.py
```

### 3. Run Locally
```bash
python app.py
```
Visit the app at `http://127.0.0.1:5001`.

---

## 📄 License
This project is open-source and available under the MIT License.
