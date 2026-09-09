# Version de chrome 152.0.7977.83
# Version de chromedriver 152.0.7977.82
# Version de selenium 4.48.0

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import csv
import time

ARCHIVO_DATOS = "datos_meteorologicos.csv"
RUTA_CHROMEDRIVER = r"C:\Program Files\chromedriver\chromedriver.exe"
URL_FORMULARIO_ALERTAS = "https://mantistcy.cl/clima/avisos.php" 

def configurar_driver():
    opciones = Options()
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    service = Service(RUTA_CHROMEDRIVER)
    driver = webdriver.Chrome(service=service, options=opciones)
    driver.maximize_window()
    return driver

def enviar_alerta_en_pagina( driver, estacion, region, variable, valor, limite ):

    mensaje_alerta = (
        f"ALERTA: La estación {estacion} "
        f"superó el umbral de {variable}. "
        f"Valor actual: {valor} "
        f"(Límite: {limite})."
    )

    try:
        print(
            f"Ingresando a la web para reportar "
            f"{estacion} - {region}")
        driver.get(URL_FORMULARIO_ALERTAS)
        espera = WebDriverWait(driver, 10)

#Regiones : 
        elemento_region = espera.until(
            EC.presence_of_element_located(
                (By.NAME, "region")
            )
        )

        menu_region = Select(elemento_region)
        print(
            f"Seleccionando región: {region}"
        )

        menu_region.select_by_visible_text(region)
        time.sleep(1)

#tipo de alerta : 

        elemento_tipo = espera.until(
            EC.presence_of_element_located(
                (By.NAME, "tipo_alerta")
            )
        )
        menu_tipo = Select(elemento_tipo)

        menu_tipo.select_by_visible_text(
            "Alerta Roja"
        )
        time.sleep(1)

#descripcion de la alerta :
        caja_texto = espera.until(
            EC.presence_of_element_located(
                (By.NAME, "descripcion")
            )
        )
        caja_texto.clear()

        caja_texto.send_keys(
            mensaje_alerta
        )
        time.sleep(1)
#aviso 
        boton_enviar = espera.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button[type='submit']"
                )
            )
        )
        boton_enviar.click()
        print( "Éxito: el robot llenó el formulario y publicó la alerta.\n")
        time.sleep(3)

    except Exception as e:
        print(
            f"ERROR EN LA WEB: "
            f"No se pudo registrar la alerta: {e}\n"
        )

def procesar_datos():
    driver = None
    try:
        driver = configurar_driver()
        print( "Iniciando revisión de umbrales ambientales...\n")

        with open(
            ARCHIVO_DATOS,
            mode="r",
            encoding="utf-8-sig"
        ) as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
#datos de csv : 
                estacion = fila.get(
                    "Estacion",
                    "Desconocida"
                ).strip()

                region = fila.get(
                    "Region",
                    "Desconocida"
                ).strip()

                try:

                    str_mp25 = (
                        fila.get("MP2.5", "0")
                        .replace("µg/m³", "")
                        .strip()
                    )

                    str_lluvia = (
                        fila.get("Lluvia", "0")
                        .replace("mm", "")
                        .strip()
                    )

                    valor_mp25 = (
                        float(str_mp25)
                        if str_mp25
                        else 0.0
                    )

                    valor_lluvia = (
                        float(str_lluvia)
                        if str_lluvia
                        else 0.0
                    )

                except ValueError:

                    print( f"No se pudieron convertir "
                           f"los datos de {estacion}"
                    )
                    continue
#datos leidos : 

                print( f"\nEstación: {estacion}")
                print( f"Región: {region}")
                print( f"MP2.5: {valor_mp25}" )
                print( f"Lluvia: {valor_lluvia}")

# Evaluar MP2.5
                if valor_mp25 > 50.0:
                    print( f" MP2.5 sobre el límite "
                           f"en {estacion}: "
                           f"{valor_mp25}" )

                    enviar_alerta_en_pagina(
                        driver,
                        estacion,
                        region,
                        "MP 2.5",
                        valor_mp25,
                        50.0
                    )

                else:

                    print( f"{estacion}: "
                           f"MP2.5 dentro del límite." )
# Evaluar lluvia
          
                if valor_lluvia > 20.0:
                    print(f" Lluvia extrema "
                          f"en {estacion}: "
                          f"{valor_lluvia} mm" )

                    enviar_alerta_en_pagina(
                        driver,
                        estacion,
                        region,
                        "Lluvia",
                        valor_lluvia,
                        20.0
                    )
                else:
                    print(f"{estacion}: "
                          f"Lluvia dentro del límite." )
    except FileNotFoundError:
        print(
            f"ERROR: Falta el archivo "
            f"'{ARCHIVO_DATOS}'."
        )
    finally:
        print(
            "\nFinalizando ejecución "
            "y cerrando navegador..."
        )
        if driver:
            driver.quit()
if __name__ == "__main__":

    procesar_datos()