import pandas as pd
import os



def convert_xlsTocsv(xls, csv):
    # Leer la hoja del archivo Excel
    df = pd.read_excel(xls)

    # Guardar como archivo CSV
    df.to_csv(csv, index=False)
    os.remove(xls)

    print(f"Archivo convertido y guardado como {csv}")

def convert(origen, destino):
      #listamos los archivos de origen "Download/"
      files = os.listdir(origen)
      if not files:
        print("No hay ficheros en la carpeta origen.")
        return

      for file in os.listdir(origen):
        if file.endswith('.xls'):  # Solo procesar archivos con extensión .xls
         nombre_archivo = file.replace('xls', 'csv')
         origen_carpeta = os.path.join(origen, file)
         destino_carpeta = os.path.join(destino, nombre_archivo)

         if(os.path.exists(destino_carpeta)):
            print("El fichero ya ha sido convertido a csv")
            os.remove(origen_carpeta)
         else:
            convert_xlsTocsv(origen_carpeta, destino_carpeta)
