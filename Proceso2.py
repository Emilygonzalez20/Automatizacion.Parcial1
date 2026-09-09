#Version de chrome 152.0.7977.83
#Version de cromedriver 152.0.7977.82
#Version de selenium 4.48.0 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

URL_PRINCIPAL = "https://mantistcy.cl/clima/"
RUTA_CHROMEDRIVER = r"C:\Program Files\chromedriver\chromedriver.exe"
CARPETA_DESCARGA = os.path.join(os.getcwd(),"telemetria_descargada")


def configurar_driver():

    os.makedirs(CARPETA_DESCARGA, exist_ok=True)

    opciones = Options()
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    preferencias = {
        "download.default_directory": CARPETA_DESCARGA,
        "download.prompt_for_download": False
    }
    opciones.add_experimental_option("prefs",preferencias)

    service = Service(RUTA_CHROMEDRIVER)
    driver = webdriver.Chrome(service=service, options=opciones)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''

            Object.defineProperty(navigator, 'webdriver', {

                get: () => undefined

            })
        '''
    })
    driver.maximize_window()
    return driver

def main():
    driver = configurar_driver()

    try:
        print("Abriendo página...")
        driver.get(URL_PRINCIPAL)
        time.sleep(5)

        # Busca enlaces relacionados con la descarga
        enlaces = driver.find_elements(
            By.XPATH,
            "//a[contains(translate(., 'TELEMETRÍAÁÉÍÓÚ', 'telemetríaáéíóú'), 'telemetría') or contains(translate(., 'DESCARGA', 'descarga'), 'descarga')]"
        )

        if len(enlaces) > 0:

            print("Haciendo clic en el enlace...")

            enlaces[0].click()

            time.sleep(5)

            archivos = os.listdir(CARPETA_DESCARGA)

            if len(archivos) > 0:
                print("Archivo descargado correctamente.")
                print("Archivos:", archivos)

            else:
                print("No se encontró ningún archivo.")

        else:
            print("No se encontró un enlace de descarga.")

    except Exception as error:
        print("Ocurrió un error:", error)

    finally:
        driver.quit()
        print("Navegador cerrado.")


if __name__ == "__main__":
    main()