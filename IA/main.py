import glob

import numpy as np
import pandas as pd
import os

from keras import Sequential
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.layers import Dense
from keras.optimizers import Adam
from keras.utils import to_categorical
from matplotlib import pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from sklearn.utils import compute_class_weight
import seaborn as sns


def crear_columnas_desplazadas(df, columnas_originales, velas_desplazadas_p):
    nuevos_datos = df.copy()  # Copiamos el DataFrame original para no modificarlo directamente

    nuevas_columnas = []

    for columna in columnas_originales:
        for hora in range(1, (velas_desplazadas_p + 1)):
            nombre_columna_nueva = f'{columna}shift{hora}'  # Nombre de la nueva columna
            # Usamos un desplazamiento hacia adelante (hacia las filas siguientes)
            columna_desplazada = df[columna].shift(-hora)
            columna_desplazada.name = nombre_columna_nueva  # Cambiamos el nombre de la columna
            nuevas_columnas.append(columna_desplazada)

    nuevos_datos = pd.concat([nuevos_datos] + nuevas_columnas, axis=1)
    nuevos_datos = nuevos_datos.dropna().reset_index(drop=True)

    return nuevos_datos


def crear_columnas_desplazadas_por_provincia(df, columnas_originales, velas_desplazadas_p):
    # Lista para almacenar los DataFrames procesados por provincia
    nuevos_datos_por_provincia = []

    # Agrupar por provincia
    provincias = df["Provincia"].unique()  # Obtener las provincias únicas

    for provincia in provincias:
        # Filtrar el DataFrame solo para la provincia actual
        df_provincia = df[df["Provincia"] == provincia].copy()

        # Aplicar la función de desplazamiento solo a los datos de esta provincia
        nuevos_datos_provincia = crear_columnas_desplazadas(df_provincia, columnas_originales, velas_desplazadas_p)

        # Añadir la provincia de vuelta al DataFrame procesado
        nuevos_datos_provincia["Provincia"] = provincia

        # Agregar el DataFrame de la provincia procesada a la lista
        nuevos_datos_por_provincia.append(nuevos_datos_provincia)

    # Concatenar todos los DataFrames procesados por provincia
    df_resultado = pd.concat(nuevos_datos_por_provincia, ignore_index=True)

    return df_resultado


def trata_de_datos(df):
    # Filtrar columnas relevantes
    df = df.loc[:,
         ["Provincia", "Toma de datos", "Precio gasolina 95 E5", "Precio gasolina 98 E5", "Precio gasóleo A"]].copy()

    # Convertir la columna 'Toma de datos' a datetime y extraer día de la semana
    df["Toma de datos"] = pd.to_datetime(df["Toma de datos"], format="%Y-%m-%d")  #QUITAR HORAS Y MINUTOS Y VER QUE TAL
    df["Día semana"] = df["Toma de datos"].dt.day_name()  # Días de la semana en texto

    #albacete_data = df[df["Provincia"] == "ALBACETE"]
    #print(albacete_data["Toma de datos"].dt.day_name().value_counts())

    # Reemplazar comas por puntos y convertir precios a numéricos
    df["Precio gasolina 95 E5"] = df["Precio gasolina 95 E5"].str.replace(",", ".").astype(float)
    df["Precio gasolina 98 E5"] = df["Precio gasolina 98 E5"].str.replace(",", ".").astype(float)
    df["Precio gasóleo A"] = df["Precio gasóleo A"].str.replace(",", ".").astype(float)

    # Calcular la media diaria por provincia y día de la semana
    media_semanal = (
        df.groupby(["Provincia", "Día semana"], as_index=False)
        .agg({
            "Precio gasolina 95 E5": "mean",
            "Precio gasolina 98 E5": "mean",
            "Precio gasóleo A": "mean"
        })
        .rename(columns={
            "Precio gasolina 95 E5": "Gasolina 95 (media)",
            "Precio gasolina 98 E5": "Gasolina 98 (media)",
            "Precio gasóleo A": "Gasóleo A (media)"
        })
    )
    return pd.DataFrame(media_semanal)


def creacion_csv():
    # Ruta a la carpeta que contiene los archivos CSV
    global data_combinada
    carpeta_csv_entrenamiento = "ProyectoComputacion_I/Actividad/Download/"  # Cambia esta ruta según corresponda
    archivos_csv_entrenamiento = glob.glob(os.path.join(carpeta_csv_entrenamiento, '*.csv'))
    # Lista para almacenar los DataFrames
    dataframes = []
    # Leer cada archivo CSV con manejo de errores y filas malformadas
    for archivo_csv in archivos_csv_entrenamiento:
        df = pd.read_csv(archivo_csv, sep=",", skip_blank_lines=True, encoding="utf-8", on_bad_lines="skip")
        dataframes.append(df)

        # Combinar todos los DataFrames en uno solo
        data_combinada = pd.concat(dataframes, ignore_index=True)

    return data_combinada


def sumar_columnas_shift(df):
    # Filtrar las columnas que contienen 'shift_' y las relacionadas con "Gasolina 95", "Gasolina 98" o "Gasóleo A"
    # suma todas las medias de los dias para luego poder poder predecir que dias es mas barato

    for i in range(1, 7):
        columnas_a_sumar = [col for col in df.columns if f'shift{i}' in col and
                            ('Gasolina 95 (media)' in col or 'Gasolina 98 (media)' in col or 'Gasóleo A (media)' in col)]

        # Crear una nueva columna que será la suma de las columnas seleccionadas
        df[f'Suma_Gasolina_Gasoleo_shift_{i}'] = df[columnas_a_sumar].sum(axis=1)

    # Filtrar las columnas originales de Gasolina y Gasóleo sin el sufijo 'shift{i}'
    columnas_a_sumar_originales = [col for col in df.columns if
                                   ('Gasolina 95 (media)' in col or 'Gasolina 98 (media)' in col or 'Gasóleo A (media)' in col) and
                                   f'shift' not in col]

    df['Suma_Gasolina_Gasoleo'] = df[columnas_a_sumar_originales].sum(axis=1)

    return df


def columnas_deseadas_v2(todas_col):
    # Todas las columnas que contengan estas palabras seran eliminadas
    #,
    columnas_a_dropear = [
        'Suma_Gasolina_Gasoleo',
        'Provincia_',
        'Día semana'
    ]

    col = []
    for a in todas_col:
        # Comprobar si alguna de las palabras no deseadas está en el nombre de la columna
        if any(palabra.lower() in a.lower() for palabra in columnas_a_dropear):
            col.append(a)

    return col


def crear_columna_objetivo(df):
    # Crear la columna 'objetivo' en base a las sumas de las columnas 'Suma_Gasolina_Gasoleo_shift_*'
    def calcular_objetivo(row):
        # Lista de columnas a comparar
        columnas = [
            'Suma_Gasolina_Gasoleo_shift_1',
            'Suma_Gasolina_Gasoleo_shift_2',
            'Suma_Gasolina_Gasoleo_shift_3',
            'Suma_Gasolina_Gasoleo_shift_4',
            'Suma_Gasolina_Gasoleo_shift_5',
            'Suma_Gasolina_Gasoleo_shift_6',
            'Suma_Gasolina_Gasoleo'
        ]

        # Obtener el índice de la columna con el valor mínimo
        min_value_index = row[columnas].idxmin()  # Esto ya estaba bien

        # Asignar el valor correspondiente basado en la columna con el valor mínimo
        if min_value_index == 'Suma_Gasolina_Gasoleo_shift_1':
            return 0
        elif min_value_index == 'Suma_Gasolina_Gasoleo_shift_5':
            return 1
        elif min_value_index == 'Suma_Gasolina_Gasoleo_shift_6':
            return 2
        elif min_value_index == 'Suma_Gasolina_Gasoleo_shift_4':
            return 3
        elif min_value_index == 'Suma_Gasolina_Gasoleo_shift_2':
            return 4
        elif min_value_index == 'Suma_Gasolina_Gasoleo_shift_3':
            return 5
        else:
            return 6

    df['objetivo'] = df.apply(calcular_objetivo, axis=1)

    # Eliminar las columnas que ya no son necesarias
    columnas = columnas_deseadas_v2(df.columns)

    # Dropear las columnas
    df = df.drop(columns=columnas)
    return df


df = creacion_csv()
resultado = trata_de_datos(df)

resultado = crear_columna_objetivo(
    sumar_columnas_shift(crear_columnas_desplazadas_por_provincia(resultado, resultado.columns, 6)))

print(resultado.columns)
X = resultado.iloc[:, :-1]
y = resultado['objetivo']

#Columnas que son strings que la ia NO ACEPTA se transforma a numeros codificandolas
columnas_a_codificar = [col for col in X.columns if
                        'Provincia' in col or 'Día semana' in col or 'Provincia_shift' or 'Día semana_shift' in col]

label_encoders = {}
for column in columnas_a_codificar:
    label_encoders[column] = LabelEncoder()
    X[column] = label_encoders[column].fit_transform(X[column])

#******************


split_limit = int(len(X) * 0.9)
X_train, X_test = X[:split_limit], X[split_limit:]
y_train, y_test = y[:split_limit], y[split_limit:]

y_train_one_hot = to_categorical(y_train, num_classes=7)
y_test_one_hot = to_categorical(y_test, num_classes=7)

# Crear el modelo de red neuronal
model = Sequential()
model.add(Dense(128, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(128, activation='relu'))
model.add(Dense(7, activation='softmax'))  # output layer


model.compile(optimizer=Adam(learning_rate=0.0001), loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False),
              metrics=['accuracy'])

# Entrenar el modelo
early_stopping = EarlyStopping(monitor='val_loss', patience=100, restore_best_weights=True)


print(model.summary())

hist = model.fit(X_train, y_train_one_hot, epochs=10000, validation_data=(X_test, y_test_one_hot),
                 callbacks=[early_stopping])
model.save("modelo.h5")


def visualizar_rendimiento_ia():
    figuras = []

    # Gráfica de pérdida
    fig1 = plt.figure()
    plt.plot(hist.history['loss'], label='Pérdida Entrenamiento')
    plt.plot(hist.history['val_loss'], label='Pérdida Validación')
    plt.xlabel('Épocas')
    plt.ylabel('Pérdida')
    plt.legend()
    plt.title('Pérdida durante el entrenamiento y validación')
    figuras.append(fig1)

    # Gráfica de precisión
    fig2 = plt.figure()
    plt.plot(hist.history['accuracy'], label='Precisión Entrenamiento')
    plt.plot(hist.history['val_accuracy'], label='Precisión Validación')
    plt.xlabel('Épocas')
    plt.ylabel('Precisión')
    plt.legend()
    plt.title('Precisión durante el entrenamiento y validación')
    figuras.append(fig2)

    # Matriz de confusión
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)

    labels = [0, 1, 2, 3, 4, 5, 6]
    target_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    cm = confusion_matrix(y_test, y_pred_classes, labels=labels)
    fig3 = plt.figure(figsize=(10, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
    plt.ylabel('Valor Verdadero')
    plt.xlabel('Predicción')
    plt.title('Matriz de Confusión')
    figuras.append(fig3)

    return figuras


def guardar_graficas(figuras, carpeta="graficas_guardadas"):
    """
    Guarda las figuras proporcionadas en una carpeta específica como archivos PNG.
    """
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    for i, figura in enumerate(figuras):
        archivo = os.path.join(carpeta, f"grafica_{i + 1}.png")
        figura.savefig(archivo, format='png')
        plt.close(figura)  # Cerrar la figura después de guardarla
        print(f"Gráfica guardada en: {archivo}")


# Generar y guardar las gráficas
figuras_guardar = visualizar_rendimiento_ia()

guardar_graficas(figuras_guardar)

# Crear copias de las gráficas para visualización
figuras_visualizacion = visualizar_rendimiento_ia()