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
import json

URL_API_REST = "https://mantistcy.cl/clima/api_rest.php"
LINK_DATOS = "https://mantistcy.cl/clima/api_rest.php?seccion=todas"
RUTA_CHROMEDRIVER = r"C:\Program Files\chromedriver\chromedriver.exe"
ARCHIVO_SALIDA = "datos_consolidados.csv"

def configurar_driver():
    opciones = Options()
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option('useAutomationExtension', False)
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    service = Service(RUTA_CHROMEDRIVER)
    driver = webdriver.Chrome(service=service, options=opciones)
    # Inyecta un script JS antes de abrir la página para evitar la detección de Selenium
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
             get: () => undefined
            })
        '''
    })

    driver.maximize_window()
    return driver

def abrir_pagina_api(driver):
    try:
        driver.get(URL_API_REST)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Página cargada correctamente.")
        return True

    except TimeoutException:
        print("Error: No se pudo cargar la página.")
        return False

    except WebDriverException as e:
        print(f"Error de WebDriver: {e}")
        return False

    except Exception as e:
        print(f"Error inesperado: {e}")
        return False


def obtener_token(driver):
    try:
        ventana_original = driver.current_window_handle
        boton = driver.find_element(By.XPATH, "//div[1]/div/a")
        boton.click()
        time.sleep(1)
        if len(driver.window_handles) > 1:
            for ventana in driver.window_handles:
                if ventana != ventana_original:
                    driver.switch_to.window(ventana)
                    break
        token = None
        segundos = 0
        while token is None and segundos < 10:
            texto_pagina = driver.find_element(By.TAG_NAME, "body").text

            if '"token"' in texto_pagina:
                inicio = texto_pagina.find('"token"')
                inicio = texto_pagina.find('"', inicio + len('"token"') + 1) + 1
                fin = texto_pagina.find('"', inicio)
                token = texto_pagina[inicio:fin]
            elif "Token:" in texto_pagina:
                inicio = texto_pagina.find("Token:") + len("Token:")
                fin = texto_pagina.find("\n", inicio)
                fin = fin if fin != -1 else len(texto_pagina)
                token = texto_pagina[inicio:fin].strip()

            if token is None:
                time.sleep(1)
                segundos += 1

        if token:
            print("Token obtenido correctamente:", token[:25] + "...")
        else:
            print("No se pudo leer el token tras presionar el botón.")
        return token

    except TimeoutException:
        print("Error: El botón 'Obtener Token' no apareció a tiempo.")
        return None

    except WebDriverException as e:
        print(f"Error de WebDriver al obtener el token: {e}")
        return None

    except Exception as e:
        print(f"Error inesperado al obtener el token: {e}")
        return None


def armar_link_con_token(token):
    link_final = f"{LINK_DATOS}&token={token}"
    print("Link con token armado:", link_final)
    return link_final


def visualizar_datos_consolidados(driver, link_final):
    try:
        driver.get(link_final)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Datos consolidados cargados.")
        return True
    except TimeoutException:
        print("Error: Los datos consolidados no cargaron a tiempo.")
        return False
    except WebDriverException as e:
        print(f"Error de WebDriver al mostrar los datos consolidados: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al mostrar los datos consolidados: {e}")
        return False


def extraer_datos(driver):
    try:
        texto_pagina = driver.find_element(By.TAG_NAME, "body").text
        datos_json = json.loads(texto_pagina)
        print("Datos extraídos correctamente.")
        return datos_json
 
    except WebDriverException as e:
        print(f"Error de WebDriver al extraer los datos: {e}")
        return None
    except ValueError as e:
        print(f"La respuesta no se pudo interpretar como JSON: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al extraer los datos: {e}")
        return None
 
 
def guardar_csv(datos_json):
    if not datos_json:
        print("No hay datos para guardar.")
        return False
 
    contenido = datos_json.get("data", datos_json)
    filas = []
 
    for categoria, valor in contenido.items():
        if isinstance(valor, list):
            for item in valor:
                if isinstance(item, dict):
                    fila = {"categoria": categoria}
                    fila.update(item)
                    filas.append(fila)
 
    if not filas:
        print("No se encontraron listas de datos para exportar a CSV.")
        return False
 
    columnas = ["categoria"]
    for fila in filas:
        for clave in fila:
            if clave not in columnas:
                columnas.append(clave)
    try:
        with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=columnas)
            escritor.writeheader()
            escritor.writerows(filas)
        print("Archivo guardado correctamente en:", ARCHIVO_SALIDA)
        return True
    except Exception as e:
        print(f"Error al guardar el CSV: {e}")
        return False
 
 
if __name__ == "__main__":
    try:
        driver = configurar_driver()
        carga_exitosa = abrir_pagina_api(driver)
        if carga_exitosa:
            token = obtener_token(driver)
            if token:
                link_final = armar_link_con_token(token)
                mostrado = visualizar_datos_consolidados(driver, link_final)
                if mostrado:
                    datos = extraer_datos(driver)
                    if datos:
                        guardado_exitoso = guardar_csv(datos)
                        if guardado_exitoso:
                            print("Los datos se guardaron correctamente.")
                        else:
                            print("La extracción se realizó, pero no se pudo guardar.")
                    else:
                        print("No se puede continuar porque no se obtuvieron datos.")
            else:
                print("No se puede continuar porque no se obtuvo el token.")
        else:
            print("No se puede continuar porque la página no cargó.")

    except Exception as error:
        print(f"Error general de ejecución: {error}")
    finally:
        print("\nCerrando el navegador...")
        driver.quit()