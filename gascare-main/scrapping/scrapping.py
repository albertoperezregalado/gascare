import requests
from datetime import datetime
import os

# URL directa del archivo
url_archivo = "https://geoportalgasolineras.es/geoportal/resources/files/preciosEESS_es.xls"

def descargar_archivo():
    try:
        # Generar nombre para el archivo de salida
        fecha = datetime.now().strftime("%Y-%m-%d")
        archivo_destino = f"../ProyectoComputacion_I/Actividad/Output/precios_carburantes_{fecha}.xls"

        # Verificar si el archivo ya fue descargado hoy
        if os.path.exists(archivo_destino):
            print("El archivo ya está descargado.")
            return

        # Hacer la petición GET directamente a la URL del archivo
        response = requests.get(url_archivo, allow_redirects=True)
        if response.status_code == 200:
            with open(archivo_destino, 'wb') as f:
                f.write(response.content)
            print(f"Archivo descargado exitosamente: {archivo_destino}")
            return archivo_destino
        else:
            print(f"Error al intentar descargar el archivo: Código {response.status_code}")
    except Exception as e:
        print(f"Error durante la descarga: {e}")

# Programar la ejecución diaria a una hora específica (18:59 en este ejemplo)
#schedule.every().day.at("19:16").do(descargar_archivo)

print("El programa está ejecutándose para descargar diariamente.")

'''
# Bucle principal que mantiene el script en ejecución
while True:
    schedule.run_pending()
    now = datetime.now()
    # Una vez que sea la hora exacta (18:59), terminamos el programa.
    if now.strftime("%H:%M") == "19:16":
        print("Fin del programa.")
        break
    time.sleep(1)
    
'''
