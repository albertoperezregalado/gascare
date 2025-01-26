import pandas as pd
import os
from io import StringIO

def clean(csv):
    """
    Procesa un archivo CSV para limpiar y transformar los datos en un formato más manejable.
    
    Args:
        csv (str): Nombre del archivo CSV a procesar.
    """
    # Define las rutas de entrada y salida del archivo.
    path_entrada = os.path.join("ProyectoComputacion_I/Actividad/Output", csv)
    path_salida =  os.path.join("ProyectoComputacion_I/Actividad/Input_20241227", csv)

    # Comprueba si el archivo ya ha sido procesado.
    if (os.path.exists(path_salida)):
        print(f"Ya está procesado el fichero {path_entrada}")
        return
    
    # Intenta cargar el archivo CSV ignorando las primeras tres filas.
    try:
        df = pd.read_csv(path_entrada, sep=',', skiprows=3)
    except:
        print(f"Error en cargar el archivo {path_entrada}")
        return
    print(df)

    # Filtra el DataFrame para conservar solo las columnas relevantes.
    df_clean = df[['Provincia', 'Toma de datos', 'Precio gasolina 95 E5', 'Precio gasolina 95 E10', 'Precio gasolina 95 E5 Premium', 'Precio gasolina 98 E5',
                    'Precio gasolina 98 E10', 'Precio gasóleo A', 'Precio gasóleo Premium', 'Precio gasóleo B', 'Precio gasóleo C', 'Precio bioetanol', 
                    'Precio biodiésel', 'Rótulo']]
    print(df_clean.head())

    # Extrae y formatea las fechas de la columna "Toma de datos".
    df_clean['Toma de datos'] = df_clean['Toma de datos'].str.split(' ').str[0]
    fechas = df_clean['Toma de datos']
    df_clean['Toma de datos'] = pd.to_datetime(df_clean['Toma de datos'], format='%d/%m/%Y', errors='coerce')
    df_clean['Toma de datos'] = df_clean['Toma de datos'].dt.date
 
    print(df_clean['Toma de datos'].head())
    print(fechas.head())

    # Genera una nueva columna con el día de la semana basado en la fecha.
    fechas_clean = []
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    for fecha in fechas:
        strF = str(fecha)
        strF = strF.split(' ')[0]
        dia = pd.to_datetime(strF, dayfirst=True).dayofweek
        fechas_clean.append(dias_semana[dia])

    df_clean['Dia semana'] = fechas_clean
    print(df_clean.head())

    """Reestructura el DataFrame de formato ancho a formato largo.
    #df_melted = pd.melt(
        df_clean,
        id_vars=['Provincia', 'Toma de datos', 'Rótulo', 'Dia semana'],
        value_vars=['Precio gasolina 95 E5', 'Precio gasolina 95 E5 Premium', 'Precio gasolina 98 E5', 'Precio gasóleo A', 'Precio gasóleo Premium', 'Precio bioetanol', 'Precio biodiésel'],
        var_name='Tipo combustible',
        value_name='Precio'
    )
    print(df_melted.head())

    # Limpia los nombres de las columnas y renombra "Rótulo" a "Distribuidora".
    df_melted['Tipo combustible'] = df_melted['Tipo combustible'].str.replace('Precio ', '')
    df_melted = df_melted.rename(columns={'Rótulo': 'Distribuidora'})

    print(df_melted.head())*/
"""
    # Guarda el DataFrame transformado en un nuevo archivo CSV.
    with open(path_salida, 'w', newline='', encoding='utf-8', errors='replace') as file:
        df_clean.to_csv(file, index=False)

def main():
    """
    Procesa todos los archivos CSV en la carpeta de salida.
    """
    for file in os.listdir("C:/Users/diogo/Documents/Universidad/Ingenieria3/Proyecto Computacion I/proyecto/ProyectoComputacion_I/Actividad/Output/"):
        clean(file)

if __name__ == "__main__":
    main()