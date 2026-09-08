# Version de chrome 152.0.7977.83
# Version de chromedriver 152.0.7977.82
# Version de selenium 4.48.0

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv

URL_PRINCIPAL = "https://mantistcy.cl/clima/"
RUTA_CHROMEDRIVER = ("C:/Users/tatia/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
ARCHIVO_SALIDA = "datos_meteorologicos.csv"

def configurar_driver():
    opciones = Options()
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    opciones.add_argument('--disable-blink-features=AutomationControlled')

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

def abrir_pagina_principal(driver):
    try:
        driver.get(URL_PRINCIPAL)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )
        print("Página principal cargada correctamente.")
        return True

    except Exception as e:
        print(f"Error al cargar la página: {e}")
        return False

def obtener_region(ciudad):
    mapa_regiones = {
        "Arica": "Arica y Parinacota",
        "Antofagasta": "Antofagasta",
        "Copiapó": "Atacama",
        "Concón": "Valparaíso",
        "Viña del Mar": "Valparaíso",
        "Valparaíso": "Valparaíso",
        "Santiago": "Metropolitana",
        "Puente Alto": "Metropolitana",
        "San José de Maipo": "Metropolitana",
        "Litueche": "O'Higgins",
        "Concepción": "Biobío",
        "Temuco": "La Araucanía",
        "Puerto Montt": "Los Lagos",
        "Coyhaique": "Aysén",
        "Punta Arenas": "Magallanes"
    }
    return mapa_regiones.get(ciudad, "Desconocida")

def extraer_datos(driver):
    datos = []
    tarjetas = driver.find_elements(
        By.XPATH,
        "//div[contains(@class, 'card') and .//*[contains(text(), 'Temp')]]"
    )
    print(f"Tarjetas encontradas: {len(tarjetas)}")

    for tarjeta in tarjetas:

        try:
            encabezado = tarjeta.find_element(
                By.XPATH,
                ".//h5"
            ).text.strip()

            ciudad = encabezado

            region = obtener_region(ciudad)

            temp = tarjeta.find_element(
                By.XPATH,
                ".//*[contains(text(), '°C')]"
            ).text.strip()

            humedad = tarjeta.find_element(
                By.XPATH,
                ".//*[contains(text(), '%')]"
            ).text.strip()

            mp = tarjeta.find_element(
                By.XPATH,
                ".//*[contains(text(), 'µg/m³')]"
            ).text.strip()

            lluvia = tarjeta.find_element(
                By.XPATH,
                ".//*[contains(text(), 'mm')]"
            ).text.strip()

            registro = {
                "Estacion": ciudad,
                "Region": region,
                "Temperatura": temp,
                "Humedad": humedad,
                "MP2.5": mp,
                "Lluvia": lluvia
            }
            datos.append(registro)
            print(
                f"{ciudad} | "
                f"{region} | "
                f"MP2.5: {mp} | "
                f"Lluvia: {lluvia}"
            )
        except Exception as err:
            print(f"Error al leer una tarjeta: {err}" )
    return datos

def guardar_csv(datos):

    if not datos:
        print("No se encontraron datos para guardar.")
        return False
    try:
        with open(
            ARCHIVO_SALIDA,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as archivo:
            campos = [
                "Estacion",
                "Region",
                "Temperatura",
                "Humedad",
                "MP2.5",
                "Lluvia"
            ]
            escritor = csv.DictWriter(
                archivo,
                fieldnames=campos
            )
            escritor.writeheader()
            escritor.writerows(datos)

        print( "Archivo guardado correctamente en:",
                ARCHIVO_SALIDA )
        return True

    except Exception as error:

        print( "Error al guardar el CSV:", error )
        return False
    
if __name__ == "__main__":

    driver = None
    try:
        driver = configurar_driver()
        if abrir_pagina_principal(driver):
            datos = extraer_datos(driver)
            if datos:
                guardar_csv(datos)
    finally:
        time.sleep(3)
        if driver:
            driver.quit()