import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def train_predictor_model(df):
    """
    Trains a Random Forest model based on historical race data.
    Features: GridPosition
    Target: FinishPosition (1 if Winner, 0 otherwise)
    """
    # Feature selection: Using GridPosition as the primary predictor
    X = df[['GridPosition']] 
    
    # Target variable: Boolean check for race winner
    y = (df['FinishPosition'] == '1').astype(int) 
    
    # Initializing Random Forest Classifier with 100 decision trees
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    return model

def calculate_probabilities(model, drivers_df):
    """
    Predicts winning probabilities for current race drivers.
    """
    X_test = drivers_df[['GridPosition']]
    
    # Get probability estimates for the 'Winner' class (index 1)
    probs = model.predict_proba(X_test)[:, 1] 
    
    # Normalize probabilities to ensure the total sum equals 100%
    if probs.sum() > 0:
        normalized_probs = probs / probs.sum()
    else:
        normalized_probs = probs # Fallback if all probabilities are zero
        
    return normalized_probs