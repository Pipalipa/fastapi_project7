import os
import pandas as pd
import streamlit as st
import requests
import logging
import matplotlib.pyplot as plt
from fastapi import FastAPI

app = FastAPI()


def main():
    st.set_page_config(page_title="Tableau de bord de prédiction d'approbation de crédit")
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Title Streamlit 
    st.title("Tableau de bord de prédiction d'approbation de crédit")

    # Saisie de l'ID client
    sk_id_curr = st.text_input("Entrez l' ID de client  (SK_ID_CURR):")
    top_n = st.slider("Sélectionnez le nombre de features principales à afficher", 1, 20, 10)  # Ajouter un curseur pour sélectionner les N principales fonctionnalités

    # Bouton Exécuter la prédiction
    if st.button("Exécuter la Prédiction"):
        if sk_id_curr:
            try:
                # Appeler l'API avec top_n comme paramètre de requête
                api_url = "http://127.0.0.1:8000/predict/"
                response = requests.post(api_url, params={"sk_id_curr": sk_id_curr, "top_n": top_n}, timeout=30)  # Augmenter timeout

                logging.debug(f"Réponse de l'API: {response.status_code}")
                logging.debug(f"Contenu de la réponse API: {response.text}")

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Décision de crédit: {result['credit_decision']}")
                    st.write("Probabilité de défaut:", result["probabilité_de_défaut"])
                    st.write("Probabilités complètes:", result["full_probabilities"])

                    # Afficher les valeurs SHAP
                    st.subheader("SHAP Values")
                    shap_values = result.get("shap_values", [])
                    feature_names = result.get("feature_noms", [])

                    logging.debug(f"SHAP values: {shap_values}")
                    logging.debug(f"Noms des Features: {feature_names}")

                    if shap_values and feature_names:
                        # Créer un dataframe trié pour l'affichage
                        shap_df = pd.DataFrame({"Feature": feature_names, "SHAP Value": shap_values})
                        shap_df = shap_df.sort_values(by="SHAP Value", key=abs, ascending=False)

                        # Plot valeurs SHAP
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.barh(shap_df['Feature'], shap_df['SHAP Value'], color='skyblue')
                        ax.set_xlabel("SHAP Value")
                        ax.set_title("SHAP Values")

                        plt.xticks(rotation=45, ha="right")
                        st.pyplot(fig)  # Afficher le plot dans Streamlit
                    else:
                        st.write("Aucune valeur SHAP renvoyée.")
                else:
                    st.error(f"Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Une erreur s'est produite lors de la requête API: {str(e)}")
            except Exception as e:
                st.error(f"Une erreur inattendue s'est produite: {str(e)}")
        else:
            st.error("Veuillez saisir un numéro de client valide.")

    if st.button("Générer un rapport de dérive des données"):
        api_url = "http://127.0.0.1:8000/data-drift-report/"
        response = requests.get(api_url)

        if response.status_code == 200:
            result = response.json()
            st.success(result["message"])

            # Afficher le rapport in Streamlit
            report_path = result["report_path"]
            st.write(f"Report Path: {report_path}")  # Debugging chemin du fichier

            if os.path.exists(report_path):
                st.write(f"Report file exists at: {report_path}")  # Confirmer l'existence du fichier
                try:
                    # Ouvrir et lire le rapport HTML
                    with open(report_path, "r", encoding="utf-8") as f:
                        report_html = f.read()
                        st.components.v1.html(report_html, height=1500)  # Afficher le contenu HTML
                except Exception as e:
                    st.error(f"An error occurred while reading the report: {str(e)}")
            else:
                st.error("Le fichier du rapport n'a pas été trouvé.")
        else:
            st.error(f"Erreur: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
        
if __name__ == "__main__":
    main()