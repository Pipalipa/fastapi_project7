import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_streamlit_app():
    subprocess.Popen(["streamlit", "run", "frontend/app3.py"])

    time.sleep(15)
    
    # Configurer le WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        # Lancer Streamlit
        driver.get("http://localhost:8501")  # Port Streamlit par défaut

        # Attendez que la page se charge et vérifiez le titre
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )

        # Vérifier le titre
        assert "Tableau de bord de prédiction d'approbation de crédit" in driver.title
    finally:
        driver.quit()
