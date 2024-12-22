from fastapi import FastAPI, HTTPException, Query
import joblib
import pandas as pd
import numpy as np
import shap
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import ColumnDriftMetric
from evidently import ColumnMapping
import os

app = FastAPI()

# Charger le modèle
model = joblib.load("XGB_classifier_model.joblib")

# Charger des données
data = pd.read_csv("df_train1.csv")
data['SK_ID_CURR'] = data['SK_ID_CURR'].astype(str)

@app.get("/")
def read_root():
    return {"message": "API de prédiction d'approbation de crédit"}

@app.post("/predict/")
def predict(sk_id_curr: str = Query(..., description="L'identifiant client"),
            top_n: int = Query(10, description="Nombre de features principales à afficher")):
    """
    Prédire l'approbation du crédit en fonction de l'ID client et afficher les N principales features.
    """
    # Vérifiez si l'identifiant client existe
    if sk_id_curr not in data['SK_ID_CURR'].values:
        raise HTTPException(status_code=404, detail="Numéro client introuvable")

    # Obtenez les exemples des features
    sample = data[data['SK_ID_CURR'] == sk_id_curr].copy()
    sample_features = sample.drop(columns=['SK_ID_CURR', 'TARGET'])

    # Assurer l'alignement avec les features du modèle 
    required_features = model.feature_names_in_
    missing_features = [feature for feature in required_features if feature not in sample_features.columns]
    if missing_features:
        raise HTTPException(status_code=500, detail=f"Ensemble de données manquant les fonctionnalités requises: {missing_features}")

    sample_features = sample_features[required_features]
    sample_features = sample_features.astype(np.float32)

    # Prédire les probabilités
    try:
        prediction = model.predict_proba(sample_features)
        proba_default = float(prediction[0][1])
        proba_approved = float(prediction[0][0])

        # Calculer les valeurs SHAP
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(sample_features)
        shap_contributions = shap_values.values[0].tolist()
        feature_names = sample_features.columns.tolist()

        # Trier les valeurs SHAP et les noms des features par contribution
        sorted_indices = np.argsort(-np.abs(shap_contributions))
        sorted_shap_values = [shap_contributions[i] for i in sorted_indices]
        sorted_feature_names = [feature_names[i] for i in sorted_indices]

        # N meilleures features
        top_features = sorted_shap_values[:top_n]
        top_feature_names = sorted_feature_names[:top_n]

        return {
            "probabilité_de_défaut": proba_default,
            "shap_values": top_features,
            "feature_noms": top_feature_names,
            "credit_decision": "Refusé" if proba_default >= 0.5 else "Approuvée",
            "full_probabilities": {
                "Approuvée": proba_approved,
                "refusé": proba_default,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"La prédiction a échoué: {str(e)}")
    
@app.get("/data-drift-report/")
async def generate_drift_report():
    """
    Générer un rapport de dérive de données à l'aide d'Evidently.
    """
    try:
        # Exemple de train et données de test
        reference_data = data.sample(n=5000, replace=False)
        current_data = data.sample(n=5000, replace=False)

        # Identifier les caractéristiques numériques et catégorielles
        categorical_columns = [
            col for col in reference_data.columns if set(reference_data[col].unique()).issubset({0, 1, np.nan})
        ]
        numerical_columns = [col for col in reference_data.columns if col not in categorical_columns]

        # Mappage de colonnes
        column_mapping = ColumnMapping()
        column_mapping.numerical_features = numerical_columns
        column_mapping.categorical_features = categorical_columns

        print(f"Numerical columns: {numerical_columns}")
        print(f"Categorical columns: {categorical_columns}")

        # Créer Evidently rapport
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)

        report_path = "data_drift_report.html"
        # report.save_html(report_path)

        return {"message": "Data drift report généré avec succès.", "report_path": report_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du rapport: {str(e)}")
