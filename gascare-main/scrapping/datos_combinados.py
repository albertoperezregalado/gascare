import pandas as pd
import os


def combinar():
    # Directorios de entrada y salida
    input_dir = "../ProyectoComputacion_I/Actividad/new"
    output_dir = "../ProyectoComputacion_I/Actividad/Combined"
    # Verificar si el directorio de salida existe, si no, crearlo
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Obtener la lista de todos los archivos CSV en el directorio
    all_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.csv')]
    # Crear un DataFrame vacío para almacenar los datos combinados
    combined_data = pd.DataFrame()
    # Leer cada archivo y concatenarlo al DataFrame combinado
    for file in all_files:
        data = pd.read_csv(file)
        combined_data = pd.concat([combined_data, data], ignore_index=True)
    # Ordenar los registros por 'Provincia', 'Toma de datos' y 'Distribuidora'
    combined_data = combined_data.sort_values(by=['Provincia', 'Toma de datos', 'Distribuidora'], ascending=True)
    # Guardar el DataFrame combinado en el directorio "Combined"
    output_file = os.path.join(output_dir, "datos_combinados.csv")
    combined_data.to_csv(output_file, index=False)
    print(f"El DataFrame combinado y ordenado se ha guardado en {output_file}")

