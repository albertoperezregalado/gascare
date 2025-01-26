import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import tkinter as tk
from tkinter import ttk, messagebox
import datetime


# Entrenamiento del modelo de regresión lineal
def train_model():
    # Cargar los datos
    file_path = '../ProyectoComputacion_I/Actividad/Combined/datos_combinados.csv'
    datos_combinados = pd.read_csv(file_path, encoding='utf-8')

    # Preprocesamiento
    datos_combinados['Precio'] = datos_combinados['Precio'].str.replace(',', '.')
    datos_combinados['Precio'] = pd.to_numeric(datos_combinados['Precio'], errors='coerce')
    datos_combinados_cleaned = datos_combinados.dropna(
        subset=['Precio', 'Provincia', 'Distribuidora', 'Dia semana', 'Tipo combustible'])

    # Codificar variables categóricas
    datos_combinados_cleaned['Provincia_encoded'] = datos_combinados_cleaned['Provincia'].astype('category').cat.codes
    datos_combinados_cleaned['Distribuidora_encoded'] = datos_combinados_cleaned['Distribuidora'].astype(
        'category').cat.codes
    datos_combinados_cleaned['Dia_encoded'] = datos_combinados_cleaned['Dia semana'].astype('category').cat.codes
    datos_combinados_cleaned['Combustible_encoded'] = datos_combinados_cleaned['Tipo combustible'].astype(
        'category').cat.codes

    # Características y etiquetas
    X = datos_combinados_cleaned[['Provincia_encoded', 'Combustible_encoded', 'Dia_encoded']]
    y = datos_combinados_cleaned['Precio']

    # Dividir datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Entrenar modelo
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Obtener lista de provincias únicas, combustibles y días codificados
    provinces = datos_combinados_cleaned['Provincia'].astype('category').cat.categories.tolist()
    fuels = datos_combinados_cleaned['Tipo combustible'].astype('category').cat.categories.tolist()
    days_mapping = dict(enumerate(datos_combinados_cleaned['Dia semana'].astype('category').cat.categories))
    days_mapping_reverse = {v: k for k, v in days_mapping.items()}  # Para codificar el día actual

    return model, provinces, fuels, days_mapping_reverse


# Predicción basada en la provincia, el tipo de combustible y el día actual
def predict_price(model, provinces, fuels, days_mapping_reverse, province_dropdown, fuel_dropdown):
    province = province_dropdown.get()
    fuel = fuel_dropdown.get()

    if not province or not fuel:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una provincia y un tipo de combustible.")
        return

    # Obtener el día actual de la semana en español
    days_in_spanish = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    current_day = days_in_spanish[datetime.datetime.now().weekday()]
    day_encoded = days_mapping_reverse.get(current_day, None)

    if day_encoded is None:
        messagebox.showerror("Error", f"El día '{current_day}' no está mapeado en los datos.")
        return

    try:
        province_index = provinces.index(province)
        fuel_index = fuels.index(fuel)
        prediction = model.predict([[province_index, fuel_index, day_encoded]])

        messagebox.showinfo(
            "Predicción",
            f"El precio promedio estimado en {province} para {fuel} hoy ({current_day}) es: {prediction[0]:.2f} €"
        )
    except ValueError:
        messagebox.showerror("Error", "Entrada no válida seleccionada.")


def mostrar_graficas():
    # Configurar la GUI
    model, provinces, fuels, days_mapping_reverse = train_model()

    root = tk.Tk()
    root.title("Predicción de Precios por Provincia y Combustible")

    # Etiqueta y menú desplegable para seleccionar la provincia
    tk.Label(root, text="Provincia:").grid(row=0, column=0, padx=10, pady=10)
    province_var = tk.StringVar()
    province_dropdown = ttk.Combobox(root, textvariable=province_var, values=provinces, state="readonly")
    province_dropdown.grid(row=0, column=1, padx=10, pady=10)

    a = province_dropdown.get()
    # Etiqueta y menú desplegable para seleccionar el tipo de combustible
    tk.Label(root, text="Tipo de Combustible:").grid(row=1, column=0, padx=10, pady=10)
    fuel_var = tk.StringVar()
    fuel_dropdown = ttk.Combobox(root, textvariable=fuel_var, values=fuels, state="readonly")
    fuel_dropdown.grid(row=1, column=1, padx=10, pady=10)

    # Botón para predecir
    predict_button = ttk.Button(root, text="Predecir Precio",
                                command=lambda: predict_price(model, provinces, fuels, days_mapping_reverse, province_dropdown, fuel_dropdown))
    predict_button.grid(row=2, column=0, columnspan=2, pady=20)

    # Iniciar la GUI
    root.mainloop()
