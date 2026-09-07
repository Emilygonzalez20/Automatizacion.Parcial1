#Version de chrome 152.0.7977.83
#Version de cromedriver 152.0.7977.82
#Version de selenium 4.48.0 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv


URL_PRINCIPAL = "https://mantistcy.cl/clima/"
RUTA_CHROMEDRIVER = r"C:\Program Files\chromedriver\chromedriver.exe"
ARCHIVO_SALIDA = "datos_meteorologicos.csv"

def configurar_driver():
    opciones = Options()
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    opciones.add_argument('--disable-blink-features=AutomationControlled')


    service = Service(RUTA_CHROMEDRIVER)
    driver = webdriver.Chrome(service=service, options=opciones)
    #Inyecta un script JS antes de abrir pagina para evitar la dección de Selenium
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
            EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        print("Página principal cargada correctamente.")
        return True
    
    except TimeoutException:
        print("Error: No se pudo cargar la página principal.")
        return False
    
    except WebDriverException as e:
        print(f"Error de WebDriver: {e}")
        return False
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False


def extraer_datos(driver):
    datos = []
    
    #Filtra las tarjetas que contienen datos meteorologicos usando xpath y el texto que contienen
    tarjetas = driver.find_elements(
        By.XPATH, 
        "//div[contains(@class, 'card') and .//*[contains(text(), 'Temp')]]"
    )

    for tarjeta in tarjetas:
        try:
            # Título de la estación
            estacion = tarjeta.find_element(
                By.XPATH, ".//*[contains(text(), 'ESTACIÓN')]/following-sibling::*[1] | .//*[contains(text(), 'Estación')]"
                ).text

            ciudad = tarjeta.find_element(By.XPATH, ".//h5").text.strip()
            
            # Localizar el elemento que contiene o acompaña a cada variable
            temp = tarjeta.find_element(
                By.XPATH, 
                ".//*[contains(text(), 'Temp')]/following-sibling::*[1] | .//*[contains(text(), '°C')]"
            ).text
            
            humedad = tarjeta.find_element(
                By.XPATH, 
                ".//*[contains(text(), 'Humedad')]/following-sibling::*[1] | .//*[contains(text(), '%')]"
            ).text
            
            mp = tarjeta.find_element(
                By.XPATH, 
                ".//*[contains(text(), 'MP')]/following-sibling::*[1] | .//*[contains(text(), 'µg/m³')]"
            ).text
            
            lluvia = tarjeta.find_element(
                By.XPATH, 
                ".//*[contains(text(), 'Lluvia')]/following-sibling::*[1] | .//*[contains(text(), 'mm')]"
            ).text

            registro = {
                "Estacion": estacion,
                "Ciudad": ciudad,
                "Temperatura": temp,
                "Humedad": humedad,
                "MP2.5": mp,
                "Lluvia": lluvia
            }
            datos.append(registro)

        except Exception as err:
            print(f"Error al leer nodos de la tarjeta: {err}")

    return datos

def guardar_csv(datos):
    if not datos:
        print("No hay datos para guardar.")
        return False
    try:
        with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8-sig") as archivo:
            campos = ["Estacion", "Ciudad", "Temperatura", "Humedad", "MP2.5", "Lluvia"]
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(datos)
            print("Archivo guardado correctamente en:", ARCHIVO_SALIDA)
            return True
    except Exception as error:
        print("Error al guardar el CSV:", error)
        return False


if __name__ == "__main__":
    try:
        driver = configurar_driver()
        carga_exitosa = abrir_pagina_principal(driver)
        if carga_exitosa:

            datos = extraer_datos(driver)
            if len(datos) > 0:
                print("Datos obtenidos:", datos)

                guardado_exitoso = guardar_csv(datos)

                if guardado_exitoso:
                    print("Los datos se guardaron correctamente.")
                else:
                    print("La extracción se realizó, pero no se pudo guardar.")

        else:
            print("No se puede continuar porque la página no cargó.")

    except Exception as error:

        print(f"Error general de ejecución: {error}")

    finally:
        print("\nCerrando el navegador en 3 segundos...")
        time.sleep(3)
        driver.quit()