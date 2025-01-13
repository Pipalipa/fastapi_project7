import subprocess
import os
import time

# Chemin pour accéder à api3.py et app3.py
scripts_directory = "./backend" 

# Obtenez les variables d'environnement actuelles
env = os.environ.copy()

env["PORT"] = "5000"

# Exécuter FastAPI avec Uvicorn
print("Lancement de FastAPI...")
subprocess.Popen(["uvicorn", "api3:app", "--host", "0.0.0.0", "--port", "5000"], env=env)

# Exécuter Streamlit
print("Lancement du dashboard Streamlit...")
subprocess.Popen(["streamlit", "run", f"./frontend/app3.py", "--server.port", "8000"], env=env)

time.sleep(5)

print("API FastAPI et dashboard Streamlit lancés !")
