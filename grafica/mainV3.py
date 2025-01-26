import pandas as pd
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
from prophet import Prophet
import locale
import logging

# Quitar los warnings de Prophet
logging.getLogger('cmdstanpy').disabled = True

# -------------------------------------------------------------------
# 1. CARGAMOS Y UNIFICAR LOS CSV (Restaurado de mainV3)
# -------------------------------------------------------------------

def cargar_datos_desde_csv(directorio_csv):
    """
    Leemos los ficheros que cumplan este patron:
       precios_carburantes_YYYY-MM-DD.csv
    """
    patron_busqueda = os.path.join(directorio_csv, "precios_carburantes_*.csv")
    archivos_csv = glob.glob(patron_busqueda)

    if not archivos_csv:
        print("No se encontraron archivos CSV en la carpeta especificada.")
        return pd.DataFrame()

    # Columnas que nos interesan del CSV
    columnas_interes = [
        'Toma de datos',
        'Provincia',
        'Precio gasolina 95 E5',
        'Precio gasolina 98 E5',
        'Precio gasóleo A'
    ]

    lista_df = []
    # Recorremos cada archivo CSV
    for archivo in archivos_csv:
        try:
            # Cargamos solo las columnas
            df_temp = pd.read_csv(
                archivo,
                usecols=columnas_interes,
                sep=',',
                decimal='.',
                encoding='utf-8'
            )
            lista_df.append(df_temp)
        except ValueError:
            print(f"No se ha podido leer las columnas: {archivo}")
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")

    # Unimos todos los DataFrames en uno solo
    if lista_df:
        df_concatenado = pd.concat(lista_df, ignore_index=True)
    else:
        df_concatenado = pd.DataFrame()

    # Convertimos la columna 'Toma de datos' a datetime
    if 'Toma de datos' in df_concatenado.columns:
        # Ajusta el formato del CSV (de '%d/%m/%Y' a '%Y-%m-%d')
        df_concatenado['Toma de datos'] = pd.to_datetime(
            df_concatenado['Toma de datos'],
            format='%Y-%m-%d',  # Se ajusta al formato de la fecha
            errors='coerce'
        )

    # Eliminamos filas con nulos en las columnas que nos interesan
    df_concatenado.dropna(
        subset=[
            'Toma de datos',
            'Provincia',
            'Precio gasolina 95 E5',
            'Precio gasolina 98 E5',
            'Precio gasóleo A'
        ],
        inplace=True
    )

    # Ordenamos por fecha
    df_concatenado.sort_values(by='Toma de datos', inplace=True)

    df_concatenado['Provincia'] = df_concatenado['Provincia'].str.upper()

    return df_concatenado



# -------------------------------------------------------------------
# 2. PREPARAR LOS DATOS PARA PROPHET (Restaurado de mainV3)
# -------------------------------------------------------------------

def preparar_datos_para_modelo(data, columna_precio):
    """
    Prepara el DataFrame para entrenar un modelo Prophet en la columna 'columna_precio'.
    Devuelve un DataFrame con ['ds', 'y'] (DATATIME) Y (FLOAT)
    """
    # Nos quedamos con la columna fecha y preio deseado
    df = data[['Toma de datos', columna_precio]].copy()

    # cambio las comas por puntos del csv
    df[columna_precio] = (
        df[columna_precio]
        .astype(str)
        .str.replace(',', '.', regex=True)
        .astype(float)
    )

    # Asignamos en Prophet las columnas 'ds' y 'y'
    df.rename(columns={'Toma de datos': 'ds', columna_precio: 'y'}, inplace=True)

    # Eliminamos duplicados y valores nulos
    df.drop_duplicates(subset=['ds'], inplace=True)
    df.dropna(subset=['ds', 'y'], inplace=True)

    return df


def entrenar_modelo(datos_modelo):
    """
    Entrena un modelo con crecimiento lineal
    """
    model = Prophet(growth='linear')
    model.fit(datos_modelo)
    return model


def predecir_precios(model, dias=15):
    """
    Generamos una predicción para los próximos '15' días.
    """
    # se empiezan a generar a partir de la ultima fecha del doc subido
    future = model.make_future_dataframe(periods=dias)
    forecast = model.predict(future)
    return forecast

# -------------------------------------------------------------------
# 3. GENERAR PREDICCIONES Y FILTRAR SÓLO LOS 15 DÍAS FUTUROS
# -------------------------------------------------------------------


def generar_predicciones_para_columnas(data, columnas_precio, dias=15):
    """
    Para cada columna de precio en 'columnas_precio', entrenamos el modelo y generamos una prediccion
    Devuelve:
      { 'NombreColumna': forecast_df, ... }
    Aqui 'forecast_df' tiene:
      ['Fecha', 'Precio Estimado', 'Límite Inferior', 'Límite Superior'].
   """
    predicciones_dict = {}

    for col in columnas_precio:
        # Se preparan los datos para Prophet
        df_modelo = preparar_datos_para_modelo(data, col)

        # Entrenamos el modelo con TODO el histórico (de la provincia filtrada)
        modelo = entrenar_modelo(df_modelo)

        # Predecimos para los días que hemos comentado antres
        forecast = predecir_precios(modelo, dias=dias)

        # Renombro las columnas para que se entiendan un poco más
        forecast.rename(columns={
            'ds': 'Fecha',
            'yhat': 'Precio Estimado',
            'yhat_lower': 'Límite Inferior',
            'yhat_upper': 'Límite Superior'
        }, inplace=True)

        # Ordenamos por Fecha
        forecast.sort_values(by='Fecha', inplace=True)

        # Filtrar únicamente las fechas posteriores a la última fecha histórica del csv subido
        ultima_fecha_historica = df_modelo['ds'].max()
        forecast = forecast[forecast['Fecha'] > ultima_fecha_historica]

        predicciones_dict[col] = forecast

    return predicciones_dict

# -------------------------------------------------------------------
# 4. VISUALIZAR RESULTADOS
# -------------------------------------------------------------------


def graficar_predicciones(forecast, titulo='Predicción de Precios'):
    """
    Con el DataFrame 'forecast' y las columnas:
    ['Fecha', 'Precio Estimado', 'Límite Inferior', 'Límite Superior'],
    crea lagrafica la predicción y su intervalo de confianza.
    """
    plt.figure(figsize=(10, 6))
    # Dibujamos la línea de 'Precio Estimado'
    plt.plot(forecast['Fecha'], forecast['Precio Estimado'], label='Precio Estimado')
    # Sombreamos el intervalo de confianza
    plt.fill_between(
        forecast['Fecha'],
        forecast['Límite Inferior'],
        forecast['Límite Superior'],
        color='lightblue',
        alpha=0.4,
        label='Intervalo de Confianza'
    )
    plt.xlabel('Fecha')
    plt.ylabel('Precio')
    plt.title(titulo)
    plt.legend()
    plt.grid(True)
    plt.show()

# -------------------------------------------------------------------
# 4. METODOS NUEVOS - RETORNAR DATOS
# -------------------------------------------------------------------

def obtener_datos_por_provincia(directorio_csv, provincia):
    """
    Filtrar y devolver los datos para una provincia especifica.
    """
    data = cargar_datos_desde_csv(directorio_csv)
    if data.empty:
        return pd.DataFrame()
    return data[data['Provincia'] == provincia.upper()]

def previsualizar_datos(data):
    """
    Devolver una vista previa de los datos cargados.
    """
    return data.head()

def obtener_predicciones(data, columnas_a_predecir, dias=15):
    """
    Generar y devolver predicciones para las columnas especificadas.
    """
    return generar_predicciones_para_columnas(data, columnas_a_predecir, dias)

# -------------------------------------------------------------------
# MAIN PARA USO EN LÍNEA DE COMANDOS
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Establecemos el español para cuando muestre el nombre del dia
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        pass

    # Cargamos los datos indicando donde se encuentran
    directorio = "../ProyectoComputacion_I/Actividad/Download"
    data_historica = cargar_datos_desde_csv(directorio)

    # Si no hay datos, saca este syso
    if data_historica.empty:
        print("No se han encontrado datos para realizar la prediccion")
    else:
        # Pedimos introducir el nombre de la provincia
        provincia_input = input("Introduce el nombre de la provincia: ")
        provincia_input = provincia_input.strip().upper()  # normalizar a mayúsculas

        # Filtramos por la provincia escrita
        data_provincia = data_historica[data_historica['Provincia'] == provincia_input]

        if data_provincia.empty:
            print(f"No se han encontrado datos para la provincia: {provincia_input}")
        else:
            print("Los datos cargados con éxito. Previsualización:")
            print(data_provincia.head())

            # Especifico las columnas que se quieren predecir
            columnas_a_predecir = [
                'Precio gasolina 95 E5',
                'Precio gasolina 98 E5',
                'Precio gasóleo A'
            ]

            # Generar predicciones para 15 días en esa provincia
            dias_a_predecir = 15
            # Generamos las predicciones para cada tipo de combustible
            dict_predicciones = generar_predicciones_para_columnas(
                data_provincia,
                columnas_a_predecir,
                dias=dias_a_predecir
            )

            # Se muestran los graficos y resultados
            for col, forecast_df in dict_predicciones.items():
                if forecast_df.empty:
                    print(f"\nNo hay predicciones para {col}, comprueba tus datos.")
                    continue

                print(f"\n=== Predicciones para {col} (próximos {dias_a_predecir} días) ===")
                #imprimimos en la consola
                for _, row in forecast_df.iterrows():
                    fecha = pd.to_datetime(row['Fecha'])
                    dia_semana = fecha.strftime('%A').capitalize()
                    # prophet utiliza un intervalo de confianza del 80% de no pasarse por encima ni debajo de esos limites
                    print(
                        f"{fecha.date()} ({dia_semana}): "
                        f"Precio Estimado = {round(row['Precio Estimado'], 2)}, "
                        f"Límite Inferior (valor más bajo) = {round(row['Límite Inferior'], 2)}, "
                        f"Límite Superior (valor más alto) = {round(row['Límite Superior'], 2)}"
                    )

                # Grafica de prediccion
                titulo_grafica = f"Predicción de {col} en {provincia_input.title()}"
                graficar_predicciones(forecast_df, titulo=titulo_grafica)
