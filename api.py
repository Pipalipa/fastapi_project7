from fastapi import FastAPI, HTTPException, Query
import joblib
import pandas as pd
import numpy as np

app = FastAPI()

# Load the model
model = joblib.load("XGB_classifier_model.joblib")

# Load the dataset
data = pd.read_csv("df_train1.csv")
data['SK_ID_CURR'] = data['SK_ID_CURR'].astype(str)

@app.get("/")
def read_root():
    return {"message": "Credit Approval Prediction API"}

@app.post("/predict/")
def predict(sk_id_curr: str = Query(..., description="The customer ID")):
    """
    Predict credit approval based on the customer ID.
    """
    # Check if the customer ID exists
    if sk_id_curr not in data['SK_ID_CURR'].values:
        raise HTTPException(status_code=404, detail="Customer ID not found")

    # Get the sample features
    sample = data[data['SK_ID_CURR'] == sk_id_curr].copy()
    sample_features = sample.drop(columns=['SK_ID_CURR'])

    # Ensure alignment with model features
    required_features = model.feature_names_in_
    missing_features = [feature for feature in required_features if feature not in sample_features.columns]
    if missing_features:
        raise HTTPException(status_code=500, detail=f"Dataset missing required features: {missing_features}")

    sample_features = sample_features[required_features]

    # Convert features to the required dtype
    sample_features = sample_features.astype(np.float32)

    # Predict probabilities
    try:
        prediction = model.predict_proba(sample_features)
        proba_default = float(prediction[0][1])  # Convert to Python float
        proba_approved = float(prediction[0][0])  # Convert to Python float
        return {
            "probability_of_default": proba_default,
            "credit_decision": "Refused" if proba_default >= 0.5 else "Approved",
            "full_probabilities": {
                "approved": proba_approved,
                "refused": proba_default,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
