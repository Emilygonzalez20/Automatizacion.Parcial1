#Version de chrome 152.0.7977.83
#Version de cromedriver 152.0.7977.82
#Version de selenium 4.48.0

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
RUTA_CHROMEDRIVER = "C:/Users/tatia/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
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

def enviar_alerta_en_pagina(driver, estacion, variable, valor, limite):
    
    mensaje_alerta = f" ALERTA: La estación {estacion} superó el umbral de {variable}. Valor actual: {valor} (Límite: {limite})."
    
    try:
        print(f" Ingresando a la web para reportar la estación {estacion}...")
        driver.get(URL_FORMULARIO_ALERTAS)
        
        espera = WebDriverWait(driver, 10)
        
        # 1. Seleccionar Región (Usando NAME)
        elemento_region = espera.until(EC.presence_of_element_located((By.NAME, "region")))
        menu_region = Select(elemento_region)
        menu_region.select_by_value("O'Higgins") 
        time.sleep(1) 

        # 2. Seleccionar Tipo de Alerta 
        elemento_tipo = espera.until(EC.presence_of_element_located((By.NAME, "tipo_alerta")))
        menu_tipo = Select(elemento_tipo)
        menu_tipo.select_by_value("Alerta Roja") # Seleccionamos alerta roja por superar umbral
        time.sleep(1)
        
        # 3. Escribir en la Descripción 
        caja_texto = espera.until(EC.presence_of_element_located((By.NAME, "descripcion")))
        caja_texto.clear()
        caja_texto.send_keys(mensaje_alerta)
        time.sleep(1)
        
        # 4. Clic en Publicar Aviso
        boton_enviar = espera.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        boton_enviar.click()
        
        print(f" Exito: El robot llenó el formulario y publicó la alerta en la web.\n")
        time.sleep(3) 
        
    except Exception as e:
        print(f" ERROR EN LA WEB: El robot no pudo interactuar con los elementos: {e}\n")

def procesar_datos():
    try:
        driver = configurar_driver()
        print("Iniciando revisión de umbrales ambientales...\n")

        with open(ARCHIVO_DATOS, mode='r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            
            for fila in lector:
                estacion = fila.get("Estacion", "Desconocida")
                try:
                    str_mp25 = fila.get("MP2.5", "0").replace("µg/m³", "").strip()
                    str_lluvia = fila.get("Lluvia", "0").replace("mm", "").strip()
                    valor_mp25 = float(str_mp25) if str_mp25 else 0.0
                    valor_lluvia = float(str_lluvia) if str_lluvia else 0.0
                except ValueError:
                    continue

                # Evaluar el MP 2.5
                if valor_mp25 > 50.0:
                    print(f" Detectado MP 2.5 alto en {estacion}. Activando robot web...")
                    enviar_alerta_en_pagina(driver, estacion, "MP 2.5", valor_mp25, 50.0)
                else:
                    print(f" {estacion}: MP 2.5 dentro del límite.")

                # Evaluar Lluvia
                if valor_lluvia > 20.0:
                    print(f" Detectada lluvia extrema en {estacion}. Activando robot web...")
                    enviar_alerta_en_pagina(driver, estacion, "Lluvia", valor_lluvia, 20.0)
                else:
                    print(f" {estacion}: Lluvia dentro del límite.")
                    
    except FileNotFoundError:
        print(f" Error: Falta el archivo '{ARCHIVO_DATOS}'. Ejecute el Proceso 3 primero.")
    finally:
        print("Finalizando ejecución y cerrando navegador...")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    procesar_datos()