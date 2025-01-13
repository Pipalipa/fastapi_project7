import evidently
import time 
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently import ColumnMapping
import pandas as pd 
import numpy as np

def generate_data_drift_report(input_file: str, output_file: str):
    df = pd.read_csv('df_train1_utf8.csv', sep = ",")

    application_train = df.sample(n=5000, replace=False)
    application_test = df.sample(n=5000, replace=False)

    # application_train = df.dropna(subset=['TARGET']).drop(columns=['SK_ID_CURR','TARGET','ACTIVE_AMT_CREDIT_SUM_OVERDUE_MEAN','ACTIVE_AMT_CREDIT_SUM_MEAN', 'ACTIVE_CNT_CREDIT_PROLONG_MEAN'])
    # application_test = df[df['TARGET'].isna()].drop(columns=['SK_ID_CURR','TARGET', 'ACTIVE_AMT_CREDIT_SUM_OVERDUE_MEAN','ACTIVE_AMT_CREDIT_SUM_MEAN', 'ACTIVE_CNT_CREDIT_PROLONG_MEAN'])
    numerical_columns = [col for col in application_train.columns if application_train[col].dtype in ['float64', 'int64']]

    categorical_columns = [col for col in application_train.columns if application_train[col].dtype == 'object']
        
    
    start_time = time.time()

    # Vérifiez que les deux DataFrames ont exactement les mêmes colonnes
    assert set(application_train.columns) == set(application_test.columns)

    # Si l'assertion est réussie, cela signifie que les colonnes correspondent
    print("Les colonnes correspondent!")

    # Création du column mapping
    column_mapping = ColumnMapping()

    column_mapping.numerical_features = numerical_columns
    column_mapping.categorical_features = categorical_columns

    # Créer le rapport de dérive des données
    data_drift_report = Report(metrics=[
        DataDriftPreset(num_stattest='ks', cat_stattest='psi', num_stattest_threshold=0.2, cat_stattest_threshold=0.2),
    ])

    print("Création du data_drift_report")

    data_drift_report.run(reference_data=application_train, current_data=application_test, column_mapping=column_mapping)

    print("Run du data_drift_report")

    elapsed_time_fit = time.time() - start_time
    print(elapsed_time_fit)

    # Sauvegarder le rapport en tant que fichier HTML
    data_drift_report.save_html('data_drift_report.html')

    data_drift_report.show()

if __name__ == "__main__":
    generate_data_drift_report("df_train1_utf8.csv", "data_drift_report.html")
