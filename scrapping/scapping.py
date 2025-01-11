from bs4 import BeautifulSoup
from datetime import datetime
import requests
import os
import schedule
import time

# URL de la página donde se encuentra el archivo
url_pagina = "https://sede.serviciosmin.gob.es/es-ES/datosabiertos/catalogo/precios-carburantes"  # Reemplaza con la URL de la página

# Función para extraer el enlace y descargar
def descargar_archivo():
    try:
        # Solicitar la página
        response = requests.get(url_pagina)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar el enlace al archivo (ajusta según el HTML inspeccionado)
            enlace_archivo = soup.find('a', href="https://geoportalgasolineras.es/resources/files/preciosEESS_es.xls")
            if enlace_archivo and 'href' in enlace_archivo.attrs:
                url_archivo = enlace_archivo['href']

                # Descarga el archivo
                fecha = datetime.now().strftime("%Y-%m-%d")
                archivo_destino = f"ProyectoComputacion_I/Actividad/Download/precios_carburantes_{fecha}.xls"

                if (os.path.exists(archivo_destino)):
                    print("El archivo ya está descargado")
                    return
                

                archivo_response = requests.get(url_archivo, allow_redirects=True)
                with open(archivo_destino, 'wb') as archivo:
                    archivo.write(archivo_response.content)
                print(f"Archivo descargado exitosamente: {archivo_destino}")
                return archivo_destino
            else:
                print("No se encontró el enlace al archivo.")
        else:
            print(f"Error al cargar la página: {response.status_code}")
    except Exception as e:
        print(f"Error durante la descarga: {e}")


# Programar la ejecución diaria a una hora específica
schedule.every().day.at("18:01").do(descargar_archivo)  
print("El programa está ejecutándose para descargar diariamente.")

# Cerrar la ejecución diaria a una hora específica
while True:
    schedule.run_pending()
    now = datetime.now()
    if now.strftime("%H:%M") == "18:02":
        print("Fin del programa.")
        break
    time.sleep(1)
