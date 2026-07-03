import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def clean_and_preprocess(df, is_train=True, label_encoder=None):
    """
    Cleans and preprocesses the flood dataset.
    - Handles missing values by filling them with column medians.
    - Detects and caps outliers using the IQR method.
    - Label encodes the categorical 'State' column if present.
    """
    df_clean = df.copy()
    
    # 1. Identify independent numerical features
    num_cols = [
        'Annual Rainfall', 'Seasonal Rainfall', 'Cloud Cover', 'Humidity', 
        'Temperature', 'River Water Level', 'Drainage Capacity', 'Water Flow', 
        'Reservoir Level', 'Soil Moisture'
    ]
    
    # 2. Handle missing values for numerical features
    for col in num_cols:
        if col in df_clean.columns:
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)
            
    # 3. Detect and treat outliers using IQR-based capping
    for col in num_cols:
        if col in df_clean.columns:
            q1 = df_clean[col].quantile(0.25)
            q3 = df_clean[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Capping: replace extreme values
            df_clean[col] = np.where(df_clean[col] < lower_bound, lower_bound, df_clean[col])
            df_clean[col] = np.where(df_clean[col] > upper_bound, upper_bound, df_clean[col])
            
    # 4. Handle Categorical Values (State column)
    if 'State' in df_clean.columns:
        if is_train:
            le = LabelEncoder()
            df_clean['State'] = le.fit_transform(df_clean['State'])
            return df_clean, le
        else:
            if label_encoder is not None:
                df_clean['State'] = label_encoder.transform(df_clean['State'])
            return df_clean
            
    if is_train:
        return df_clean, None
    return df_clean
