import pandas as pd
import os
from io import StringIO
import chardet


def clean(csv):
    path_entrada = os.path.join("../ProyectoComputacion_I/Actividad/Download", csv)
    path_salida = os.path.join("../ProyectoComputacion_I/Actividad/new", csv)

    if (os.path.exists(path_salida)):
        print(f"Ya está procesado el fichero {path_entrada}")
        return

    try:
        df = pd.read_csv(path_entrada, sep=',')
    except:
        print(f"Error en cargar el arcivo {path_entrada}")
        return

    df_clean = df[['Provincia', 'Toma de datos', 'Precio gasolina 95 E5', 'Precio gasolina 95 E10',
                   'Precio gasolina 95 E5 Premium', 'Precio gasolina 98 E5',
                   'Precio gasolina 98 E10', 'Precio gasóleo A', 'Precio gasóleo Premium', 'Precio gasóleo B',
                   'Precio gasóleo C', 'Precio bioetanol',
                   'Precio biodiésel', 'Rótulo']].copy()

    df_clean['Toma de datos'] = df_clean['Toma de datos'].str.split(' ').str[0]
    fechas = df_clean['Toma de datos']
    df_clean['Toma de datos'] = pd.to_datetime(df_clean['Toma de datos'], format='%d/%m/%Y', errors='coerce')
    df_clean['Toma de datos'] = df_clean['Toma de datos'].dt.date


    fechas_clean = []
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    for fecha in fechas:
        strF = str(fecha)
        strF = strF.split(' ')[0]
        dia = pd.to_datetime(strF, dayfirst=True).dayofweek
        fechas_clean.append(dias_semana[dia])

    df_clean['Dia semana'] = fechas_clean

    df_melted = pd.melt(
        df_clean,
        id_vars=['Provincia', 'Toma de datos', 'Rótulo', 'Dia semana'],
        value_vars=['Precio gasolina 95 E5', 'Precio gasolina 95 E5 Premium', 'Precio gasolina 98 E5',
                    'Precio gasóleo A', 'Precio gasóleo Premium', 'Precio bioetanol', 'Precio biodiésel'],
        var_name='Tipo combustible',
        value_name='Precio'
    )

    df_melted['Tipo combustible'] = df_melted['Tipo combustible'].str.replace('Precio ', '')
    df_melted = df_melted.rename(columns={'Rótulo': 'Distribuidora'})

    with open(path_salida, 'w', newline='', encoding='utf-8', errors='replace') as file:
        df_melted.to_csv(file, index=False)


def pre_clean():
    for file in os.listdir("../ProyectoComputacion_I/Actividad/Download/"):
        if "2024" in file:
            clean(file)
