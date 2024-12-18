import os
import joblib
import pandas as pd
import streamlit as st
import shap

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Load the model
model_path = os.path.join(current_directory, "model.pkl")
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
                prediction = model.predict_proba(sample_features)
                
                # Print out the full prediction for diagnostics
                st.write("Full Prediction Output:", prediction)
                
                # Get the probability for the positive class (index 1)
                proba = prediction[0][1]  # Probability of the positive class

                # Check the range of probabilities
                if proba < 0 or proba > 1:
                    st.error("The predicted probability is out of range.")
                else:
                    # Display results
                    st.write("### Prediction Results")
                    st.write(f"**Probability of Default:** {proba * 100:.4f}%")  # Display with more precision
                    st.write(f"**Credit Decision:** {'Refused' if proba >= 0.5 else 'Approved'}")
                
        else:
            st.warning(f"Customer ID {sk_id_curr} does not exist in the dataset.")
            # Display the available SK_ID_CURR values for debugging
            st.write("### Available Customer IDs in the dataset:")
            st.write(data['SK_ID_CURR'].tail(10))  # Show first 10 IDs, you can adjust this
    else:
        st.warning("Invalid input: Please provide a numeric Customer ID (SK_ID_CURR).")
