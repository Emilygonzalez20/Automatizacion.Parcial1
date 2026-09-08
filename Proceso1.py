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
import json


URL_API_REST = "https://mantistcy.cl/clima/api_rest.php"
LINK_DATOS = "https://mantistcy.cl/clima/api_rest.php?seccion=todas"
RUTA_CHROMEDRIVER = ("C:/Users/tatia/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")


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

def abrir_pagina_api(driver):
    try:
        driver.get(URL_API_REST)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Página de API REST cargada correctamente.")
        return True

    except TimeoutException:
        print("Error: No se pudo cargar la página de API REST.")
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
        print("Datos consolidados cargados. Puedes revisarlos en la ventana del navegador.")
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

def verificar_estado_sistema(driver, link_final):
    try:
        driver.get(link_final)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        texto_respuesta = driver.find_element(By.TAG_NAME, "body").text
        
        try:
            payload = json.loads(texto_respuesta)
            
            # Verificación de claves típicas de estado
            if "error" in payload:
                print(f"[FALLO] La API devolvió un error: {payload['error']}")
                return False
            else:
                print("[ÉXITO] Sincronización activa y datos recibidos.")
                return True
                
        except json.JSONDecodeError:
            if "error" in texto_respuesta.lower() or "unauthorized" in texto_respuesta.lower():
                print("[FALLO] Respuesta no autorizada o con errores de conexión.")
                return False
            
            print("[ÉXITO] Respuesta recibida y verificada en el cuerpo del documento.")
            return True

    except TimeoutException:
        print("Error: Los datos consolidados no cargaron dentro del tiempo límite.")
        return False
    except Exception as e:
        print(f"Error verificando estado: {e}")
        return False

if __name__ == "__main__":
    try:
        driver = configurar_driver()
        carga_exitosa = abrir_pagina_api(driver)

        if carga_exitosa:
            token = obtener_token(driver)

            if token:
                link_final = armar_link_con_token(token)
                mostrado = verificar_estado_sistema(driver, link_final)
                if mostrado:
                    time.sleep(30)
            else:
                print("No se puede continuar porque no se obtuvo el token.")
        else:
            print("No se puede continuar porque la página no cargó.")

    except Exception as error:
        print(f"Error general de ejecución: {error}")

    finally:
        print("\nCerrando el navegador...")
        driver.quit()