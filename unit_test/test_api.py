import os
import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient
import json
import pytest
import sys

import warnings

warnings.simplefilter("ignore", DeprecationWarning)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api3 import app

@pytest.fixture
def current_dir():
    # Détermine le chemin du répertoire courant
    return os.path.dirname(os.path.abspath(__file__))

#Créer un ID client de test pour FastAPI
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_chargement_modele(current_dir):
    # Charger le modèle
    model_path = os.path.join(current_dir, "..", "Best_model", "XGB_classifier_model.joblib")
    model = joblib.load(model_path)
    #test fail
    # model = None
    # Vérifie que le modèle a été chargé correctement
    assert model is not None, "Erreur dans le chargement du modèle."
    pass

def test_chargement_csv(current_dir):
    # Charger des données
    csv_path = os.path.join(current_dir, "..", "Data", "df_train1_utf8.csv")
    data = pd.read_csv(csv_path)
    #test fail
    # data = None
    assert data is not None, "Erreur dans le chargement du .csv"
    pass

def test_prediction(current_dir, client):
    import os
    import pandas as pd
    # Détermine le chemin du fichier CSV contenant les données de test
    csv_path = os.path.join(current_dir, "..", "Data", "df_train1_utf8.csv")
    # Chargement des données
    data = pd.read_csv(csv_path)
    # Sample SK_ID_CURR for testing
    # sk_id_curr = data.iloc[0]['SK_ID_CURR']
    sk_id_curr = "100002" 
    top_n = 10 
    # Crée une requête de test pour la prédiction en utilisant l'échantillon sélectionné
    response = client.post("/predict", params={"sk_id_curr": sk_id_curr, "top_n": top_n})
    # Imprimer le corps de la réponse debugging
    print(response.json())
    assert 'probabilité_de_défaut' in response.json(), f"La réponse ne contient pas 'probabilité_de_défaut'. Réponse: {response.json()}"
