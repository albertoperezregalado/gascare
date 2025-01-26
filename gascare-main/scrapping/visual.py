import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import os

from matplotlib import pyplot as plt


def crear_csv():
    # Cargar el archivo combinado directamente
    combined_data_path = "../ProyectoComputacion_I/Actividad/Combined/datos_combinados.csv"
    if os.path.exists(combined_data_path):
        combined_data = pd.read_csv(combined_data_path)
    else:
        print("El archivo combinado no existe. Por favor, genera el archivo primero.")
        exit()
    # Reemplazar comas por puntos en la columna 'Precio' y convertir a numérico
    combined_data['Precio'] = combined_data['Precio'].str.replace(',', '.', regex=False)
    combined_data['Precio'] = pd.to_numeric(combined_data['Precio'], errors='coerce')
    # Eliminar filas con valores nulos en las columnas necesarias
    required_columns = ['Provincia', 'Distribuidora', 'Tipo combustible', 'Dia semana', 'Precio']
    combined_data = combined_data.dropna(subset=required_columns)
    # Agrupar por provincia, distribuidora, tipo de combustible y día de la semana, y calcular el precio mínimo
    cheapest_prices = combined_data.groupby(
        ['Provincia', 'Distribuidora', 'Tipo combustible', 'Dia semana']
    )['Precio'].min().reset_index()

    return cheapest_prices


# Cargar los datos
def load_data():
    return crear_csv()



# Buscar el precio más barato
def encontrar_precio_mas_barato():
    # Obtener los valores ingresados por el usuario
    provincia = provincia_entry.get()
    tipo_combustible = tipo_combustible_dropdown.get()

    if not provincia or not tipo_combustible:
        messagebox.showwarning("Advertencia", "Por favor, ingrese todos los datos.")
        return

    # Filtrar los datos según la entrada del usuario
    result = data[
        (data['Provincia'].str.upper() == provincia.upper()) &
        (data['Tipo combustible'].str.upper() == tipo_combustible.upper())
        ]
    print(result)

    if result.empty:
        messagebox.showinfo("No se encontraron datos. ")
    else:
        cheapest = result.loc[result['Precio'].idxmin()]
        messagebox.showinfo(
            "Resultado",
            f"El precio más barato en {provincia} para {tipo_combustible} es:\n"
            f"Distribuidora: {cheapest['Distribuidora']}\n"
            f"Día de la semana: {cheapest['Dia semana']}\n"
            f"Precio: {cheapest['Precio']:.2f} €"
        )
    mostrar_graficas()

def mostrar_graficas():
    # Convertir la columna 'Precio' a numérica
    data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce')
    # Solicitar al usuario la provincia
    provincia = provincia_entry.get()
    # Filtrar los datos por la provincia especificada
    filtered_data = data[data['Provincia'].str.lower() == provincia.lower()]
    if filtered_data.empty:
        print(f"No se encontraron datos para la provincia: {provincia}")
    else:
        # 1. Gráfico de barras: Precio promedio por tipo de combustible
        avg_price_by_distrib = (filtered_data.groupby('Distribuidora')['Precio'].mean().sort_values().tail(10))
        plt.figure(figsize=(10, 6))
        avg_price_by_distrib.plot(kind='bar')
        plt.title(f"Precio Promedio por Distribuidora en {provincia}")
        plt.xlabel("Distribuidora")
        plt.ylabel("Precio Promedio (€)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # 2. Gráfico de barras apilado: Precio promedio por día de la semana y tipo de combustible
        avg_price_by_day_fuel = filtered_data.groupby(['Dia semana', 'Tipo combustible'])['Precio'].mean().unstack()

        avg_price_by_day_fuel.plot(kind='bar', stacked=True, figsize=(12, 8))
        plt.title(f"Precio Promedio por Día de la Semana y Tipo de Combustible en {provincia}")
        plt.xlabel("Día de la Semana")
        plt.ylabel("Precio Promedio (€)")
        plt.legend(title="Tipo de Combustible", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()


        # 4. Gráfico de línea: Tendencia de precios por día de la semana
        avg_price_by_day = filtered_data.groupby('Dia semana')['Precio'].mean().reindex(
            ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        )

        plt.figure(figsize=(10, 6))
        avg_price_by_day.plot(kind='line', marker='o')
        plt.title(f"Tendencia de Precios por Día de la Semana en {provincia}")
        plt.xlabel("Día de la Semana")
        plt.ylabel("Precio Promedio (€)")
        plt.grid()
        plt.tight_layout()
        plt.show()



def precio_min():
    global data, provincia_entry, tipo_combustible_dropdown
    # Cargar los datos al inicio
    data = load_data()
    # Obtener la lista de tipos de combustible únicos
    tipo_combustible = sorted(data['Tipo combustible'].unique())
    # Crear la interfaz gráfica
    root = tk.Tk()
    root.title("Consulta de Precios de Combustibles")
    # Etiqueta y campo de texto para la provincia
    tk.Label(root, text="Provincia:").grid(row=0, column=0, padx=10, pady=10)
    provincia_var = tk.StringVar()
    provincia_entry = ttk.Entry(root, textvariable=provincia_var)
    provincia_entry.grid(row=0, column=1, padx=10, pady=10)
    # Etiqueta y menú desplegable para el tipo de combustible
    tk.Label(root, text="Tipo de Combustible:").grid(row=1, column=0, padx=10, pady=10)
    tipo_combustible_var = tk.StringVar()
    tipo_combustible_dropdown = ttk.Combobox(root, textvariable=tipo_combustible_var, values=tipo_combustible,
                                             state="readonly")
    tipo_combustible_dropdown.grid(row=1, column=1, padx=10, pady=10)
    # Botón para buscar
    search_button = ttk.Button(root, text="Buscar Precio", command=encontrar_precio_mas_barato)
    search_button.grid(row=2, column=0, columnspan=2, pady=20)
    # Iniciar el bucle de la aplicación
    root.mainloop()

