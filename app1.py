import os
import joblib
import pandas as pd
import streamlit as st

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Load the model
model_path = os.path.join(current_directory, "XGB_classifier_model.joblib")
model = joblib.load(model_path)

# Load the dataset
data_path = os.path.join(current_directory, "df_train1.csv")
data = pd.read_csv(data_path)

# Ensure SK_ID_CURR is treated as a string
data['SK_ID_CURR'] = data['SK_ID_CURR'].astype(str)

# Streamlit title
st.title("Credit Approval Prediction Dashboard")

# Input for Customer ID
sk_id_curr = st.text_input("Enter Customer ID (SK_ID_CURR):")

# Run Prediction button
if st.button("Run Prediction"):
    # Check if the entered ID is valid (numeric and exists in the dataset)
    if sk_id_curr.isdigit():
        # Check if the customer ID exists in the dataset
        if sk_id_curr in data['SK_ID_CURR'].values:
            # Filter the data for the given SK_ID_CURR
            sample = data[data['SK_ID_CURR'] == sk_id_curr].copy()
            
            # Drop SK_ID_CURR column for prediction
            sample_features = sample.drop(columns=['SK_ID_CURR'])

            # Check for feature alignment with the model
            required_features = model.feature_names_in_
            if not all(feature in sample_features.columns for feature in required_features):
                st.error("The dataset is missing some features required by the model.")
            else:
                # Ensure column order matches the model's requirements
                sample_features = sample_features[required_features]

                # Predict probabilities directly with raw features
                try:
                    prediction = model.predict_proba(sample_features)
                    
                    # Probability of the positive class (index 1)
                    proba = prediction[0][1]

                    # Display results
                    st.write("### Prediction Results")
                    st.write(f"**Probability of Default:** {proba * 100:.2f}%")
                    st.write(f"**Credit Decision:** {'Refused' if proba >= 0.5 else 'Approved'}")
                    
                    # Display full prediction probabilities for transparency
                    st.write("### Full Probability Distribution")
                    st.write(f"Probability of 'Approved': {prediction[0][0] * 100:.2f}%")
                    st.write(f"Probability of 'Refused': {prediction[0][1] * 100:.2f}%")
                except Exception as e:
                    st.error(f"An error occurred during prediction: {e}")
        else:
            st.warning(f"Customer ID {sk_id_curr} does not exist in the dataset.")
    else:
        st.warning("Invalid input: Please provide a numeric Customer ID (SK_ID_CURR).")
