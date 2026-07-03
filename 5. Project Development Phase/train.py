import os
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

from preprocess import clean_and_preprocess

# Load and Preprocess Data
def load_and_prepare_data():
    csv_path = 'data/flood_dataset.csv'
    excel_path = 'data/flood dataset.xlsx'
    
    # Read CSV if exists, fallback to Excel
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"Loaded raw dataset from CSV: '{csv_path}' of shape {df.shape}")
    else:
        df = pd.read_excel(excel_path)
        print(f"Loaded raw dataset from Excel: '{excel_path}' of shape {df.shape}")
        
    # Run preprocessing (imputation + IQR capping + Label Encoding for State if present)
    df_clean, le = clean_and_preprocess(df, is_train=True)
    
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    # Save the State LabelEncoder if present
    if le is not None:
        joblib.dump(le, 'models/state_encoder.save')
        print("LabelEncoder for State fitted and saved as 'models/state_encoder.save'.")
    
    # Re-order columns to a fixed sequence: the 10 numerical features from the Kaggle dataset
    feature_cols = [
        'Annual Rainfall', 'Seasonal Rainfall', 'Cloud Cover', 'Humidity', 
        'Temperature', 'River Water Level', 'Drainage Capacity', 'Water Flow', 
        'Reservoir Level', 'Soil Moisture'
    ]
    X = df_clean[feature_cols]
    y = df_clean['Target']
    
    print("Features sequence:", list(X.columns))
    print("Class Balance:\n", y.value_counts(normalize=True))
    
    # Split into training and testing sets (75/25 split)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    print(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    
    # Scaling X
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert scaled arrays back to DataFrames with column names
    X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=X.columns)
    X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=X.columns)
    
    # Save the StandardScaler
    joblib.dump(scaler, 'models/scaler.save')
    print("StandardScaler fitted and saved as 'models/scaler.save'.")
    
    return X_train_scaled_df, X_test_scaled_df, y_train, y_test

# Model Training Functions
def decisiontree(X_train, X_test, y_train, y_test):
    print("\n--- Training Decision Tree Classifier ---")
    model = DecisionTreeClassifier(class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print("Confusion Matrix:\n", cm)
    return model, accuracy

def randomForest(X_train, X_test, y_train, y_test):
    print("\n--- Training Random Forest Classifier ---")
    # Using n_jobs=-1 and limit estimators to 50 for large datasets
    model = RandomForestClassifier(n_estimators=50, class_weight='balanced', n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print("Confusion Matrix:\n", cm)
    return model, accuracy

def KNN(X_train, X_test, y_train, y_test):
    print("\n--- Training K-Nearest Neighbors Classifier (K=5) ---")
    model = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print("Confusion Matrix:\n", cm)
    return model, accuracy

def xgBoostModel(X_train, X_test, y_train, y_test):
    print("\n--- Training XGBoost Classifier ---")
    # Compute class imbalance ratio to weight positive class
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos = neg_count / pos_count
    print(f"Negative: {neg_count}, Positive: {pos_count}, Scale Pos Weight: {scale_pos:.4f}")
    
    # Using n_jobs=-1 for high-speed multi-core training and class balancing
    model = XGBClassifier(
        eval_metric='logloss',
        n_jobs=-1,
        scale_pos_weight=scale_pos,
        max_depth=6,
        learning_rate=0.1,
        n_estimators=100,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    cr = classification_report(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print("Confusion Matrix:\n", cm)
    print("Classification Report:\n", cr)
    return model, accuracy

# Compare all models
def compareModel(X_train, X_test, y_train, y_test):
    results = {}
    
    # 1. Decision Tree
    dt_model, dt_acc = decisiontree(X_train, X_test, y_train, y_test)
    results['Decision Tree'] = (dt_model, dt_acc)
    
    # 2. Random Forest
    rf_model, rf_acc = randomForest(X_train, X_test, y_train, y_test)
    results['Random Forest'] = (rf_model, rf_acc)
    
    # 3. KNN (Skip for large datasets due to O(N) complexity)
    if len(X_train) < 50000:
        knn_model, knn_acc = KNN(X_train, X_test, y_train, y_test)
        results['KNN'] = (knn_model, knn_acc)
    else:
        print("\n--- Skipping KNN Classifier (Disabled for large datasets due to prediction time) ---")
    
    # 4. XGBoost
    xgb_model, xgb_acc = xgBoostModel(X_train, X_test, y_train, y_test)
    results['XGBoost'] = (xgb_model, xgb_acc)
    
    print("\n=======================================================")
    print("MODEL COMPARISON SUMMARY")
    print("=======================================================")
    for model_name, (_, acc) in results.items():
        print(f"{model_name:<20} Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print("=======================================================")
    
    # Find best model
    best_model_name = max(results, key=lambda k: results[k][1])
    
    # Save XGBoost as the final model for Vercel deployment (compact size: ~500KB vs 230MB RF)
    selected_model_name = 'XGBoost' if 'XGBoost' in results else best_model_name
    best_model, best_acc = results[selected_model_name]
    
    print(f"\nSelecting {selected_model_name} as the final model (Accuracy: {best_acc*100:.2f}%).")
    
    # Save the selected model
    joblib.dump(best_model, 'models/flood_model.pkl')
    print(f"Final model saved as 'models/flood_model.pkl' (Model Type: {selected_model_name}).")
    
    # Save metadata as model_meta.json
    import json
    meta = {
        "best_model": best_model_name,
        "features_sequence": [
            'Annual Rainfall', 'Seasonal Rainfall', 'Cloud Cover', 'Humidity', 
            'Temperature', 'River Water Level', 'Drainage Capacity', 'Water Flow', 
            'Reservoir Level', 'Soil Moisture'
        ],
        "test_metrics": {
            "Accuracy": float(best_acc)
        },
        "all_models_comparison": {
            name: {
                "Accuracy": float(acc)
            } for name, (_, acc) in results.items()
        }
    }
    with open('models/model_meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=4)
    print("Model metadata saved as 'models/model_meta.json'.")
    
    # Generate ROC Curve
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from sklearn.metrics import roc_curve, auc
        
        if hasattr(best_model, "predict_proba"):
            y_proba = best_model.predict_proba(X_test)[:, 1]
        else:
            y_proba = best_model.predict(X_test)
            
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, color='#2563eb', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='#64748b', lw=1.5, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig('models/roc_curve.png', dpi=140)
        plt.savefig('static/roc_curve.png', dpi=140)
        plt.close()
        print("ROC Curve saved to 'models/roc_curve.png'.")
    except Exception as e:
        print(f"Error generating ROC curve: {e}")
        
    # Generate Feature Importance plot
    try:
        if hasattr(best_model, "feature_importances_"):
            importances = best_model.feature_importances_
            indices = np.argsort(importances)[::-1]
            features = [
                'Annual Rainfall', 'Seasonal Rainfall', 'Cloud Cover', 'Humidity', 
                'Temperature', 'River Water Level', 'Drainage Capacity', 'Water Flow', 
                'Reservoir Level', 'Soil Moisture'
            ]
            
            plt.figure(figsize=(8, 5))
            plt.bar(range(len(features)), importances[indices], color='#3b82f6', align="center")
            plt.xticks(range(len(features)), [features[i] for i in indices], rotation=45, ha='right')
            plt.title("Feature Importances (Best Model)")
            plt.xlabel("Features")
            plt.ylabel("Importance Score")
            plt.tight_layout()
            plt.savefig('models/feature_importance.png', dpi=140)
            plt.savefig('static/feature_importance.png', dpi=140)
            plt.close()
            print("Feature Importance saved to 'models/feature_importance.png'.")
    except Exception as e:
        print(f"Error generating Feature Importance plot: {e}")

if __name__ == '__main__':
    X_train, X_test, y_train, y_test = load_and_prepare_data()
    compareModel(X_train, X_test, y_train, y_test)

