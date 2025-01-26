import tkinter as tk #Biblioteca usada para crear interfaz
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #Biblioteca usada para generar graficas
import sys
import os
import matplotlib.pyplot as plt
import numpy as np #Biblioteca usada para generar operaciones matematicas
import seaborn as sns # Visualizaciones adicionales
from sklearn.metrics import confusion_matrix # calculo matriz de confusion


# Agregar el directorio padre al sistema de búsqueda
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from grafica.mainV3 import obtener_datos_por_provincia, previsualizar_datos, obtener_predicciones # import parte alberto
from scrapping import scrapping, convert, clean_new, datos_combinados, logistic_regresion, visual

# from IA.main import visualizar_rendimiento_ia # import parte fernando

class VisualApp: # clase visual
    def __init__(self, root, model, hist, X_test, y_test): 

# -------------------------------------------------------------------
#  Estructura Ventana
# -------------------------------------------------------------------

        self.root = root
        self.root.title("Predicción y Visualización de Gráficas") # definimos titulo
        self.root.geometry("800x600") # definimos tamaño
        self.root.configure(bg="#1e1e1e")  # definimos fondo oscuro

        self.model = model
        self.hist = hist
        self.X_test = X_test
        self.y_test = y_test

# -------------------------------------------------------------------
#  Creación Componentes (Labels, Botones, Combobox y Tablas)
# -------------------------------------------------------------------

        self.title_label = tk.Label( # Label titulo
            root, text="Predicción de Precios de Combustibles", font=("Arial", 16), bg="#1e1e1e", fg="#ffffff"
        )
        self.title_label.pack(pady=10)

        # Labels provincia
        self.province_label = tk.Label(root, text="Nombre de la Provincia:", bg="#1e1e1e", fg="#ffffff")
        self.province_label.pack(pady=5)
        self.province_entry = tk.Entry(root, width=40, bg="#2e2e2e", fg="#ffffff", insertbackground="#ffffff")
        self.province_entry.pack(pady=5)


        self.button_frame = tk.Frame(root, bg="#1e1e1e")
        self.button_frame.pack(pady=10)

        # Centrar los botones dentro del frame
        self.button_frame.pack(anchor="center")

        # Botón 1
        self.boton_1 = tk.Button(
            self.button_frame, text="Scrapping", command=self.ejecutar_scrapping, bg="#3c3c3c", fg="#ffffff"
        )
        self.boton_1.pack(side=tk.LEFT, padx=5)

        # Botón 2
        self.boton_2 = tk.Button(
            self.button_frame, text="Convert", command=lambda: convert.convert("../ProyectoComputacion_I/Actividad/Output/", "../ProyectoComputacion_I/Actividad/Download/"), bg="#3c3c3c", fg="#ffffff"
        )
        self.boton_2.pack(side=tk.LEFT, padx=5)

        # Botón 3
        self.boton_3 = tk.Button(
            self.button_frame, text="Dar formato", command=lambda: clean_new.pre_clean(), bg="#3c3c3c", fg="#ffffff"
        )
        self.boton_3.pack(side=tk.LEFT, padx=5)

        # Botón 4
        self.boton_4 = tk.Button(
            self.button_frame, text="Combinar", command=lambda: datos_combinados.combinar(), bg="#3c3c3c", fg="#ffffff"
        )
        self.boton_4.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button( root, text="Cargar Datos", command=self.load_data, bg="#3c3c3c", fg="#ffffff")
        self.load_button.pack(pady=10)

        # Tabla para mostrar previsualización de datos
        self.tree = ttk.Treeview(root, columns=("Toma de datos", "Provincia"), show="headings")
        self.tree.heading("Toma de datos", text="Toma de Datos")
        self.tree.heading("Provincia", text="Provincia")
        self.tree.pack(pady=10)

        # ComboBox para seleccionar distribuidora
        self.distributor_label = tk.Label(root, text="Seleccionar Distribuidora:", bg="#1e1e1e", fg="#ffffff")
        self.distributor_label.pack(pady=5)
        self.distributor_combo = ttk.Combobox(root, state="readonly", width=37)
        self.distributor_combo.pack(pady=5)


        self.button_frame = tk.Frame(root, bg="#1e1e1e")
        self.button_frame.pack(pady=10)

        # Centrar los botones dentro del frame
        self.button_frame.pack(anchor="center")

        self.predict_distributor_button = tk.Button(
            self.button_frame, text="Generar Gráfica de Distribuidora", command=lambda: self.generate_distributor_graph, bg="#3c3c3c", fg="#ffffff"
        )
        self.predict_distributor_button.pack(side=tk.LEFT, padx=5)


        self.regresionLogistica = tk.Button(
            self.button_frame, text="Precio promedio", command=lambda: logistic_regresion.mostrar_graficas(),
            bg="#3c3c3c", fg="#ffffff"
        )
        self.regresionLogistica.pack(side=tk.LEFT, padx=5)


        self.precioMin = tk.Button(
            self.button_frame, text="Precio minimo", command=lambda: visual.precio_min(),
            bg="#3c3c3c", fg="#ffffff"
        )
        self.precioMin.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(root, text="", fg="#00ff00", bg="#1e1e1e", font=("Arial", 10))
        self.status_label.pack(pady=10)

        self.data = None

    def ejecutar_scrapping(self):
        # Llamar a la función de scrapping
        try:
            resultado = scrapping.descargar_archivo()
            if resultado:
                print(f"Archivo descargado: {resultado}")
                tk.messagebox.showinfo("Éxito", f"Archivo descargado: {resultado}")
            else:
                print("No se descargó ningún archivo.")
                tk.messagebox.showwarning("Advertencia", "No se descargó ningún archivo.")
        except Exception as e:
            print(f"Error al ejecutar el scrapping: {e}")
            tk.messagebox.showerror("Error", f"Error al ejecutar el scrapping: {e}")

    def load_data(self):
        """Cargar los datos de la provincia especificada."""
        province = self.province_entry.get().strip().upper() # tomamos la entrada de la pronvica elegida por el usuario
        if not province:
            messagebox.showerror("Error de entrada", "Por favor, proporciona el nombre de la provincia.") # excepcion controla no introducimos ninguan provincia
            return

        # Obtener datos por provincia
        directory = "../ProyectoComputacion_I/Actividad/Download/" # directorio database
        self.data = obtener_datos_por_provincia(directory, province) # pasamos por parametro el directorio y la provincia al metodo de clase mainV3

        if self.data.empty: # si el metodo obtener_datos_por_provincia nos devuelve vacio
            messagebox.showerror("Error", f"No se encontraron datos para la provincia: {province}.") # mostramos mensaje de error
            self.tree.delete(*self.tree.get_children())  # Limpiamos tabla
            self.distributor_combo['values'] = []  # Limpiamos combobx
            return

        # Mostramos datos obtenidos 
        self.show_preview(previsualizar_datos(self.data)) # rellenamos tabla
        self.populate_distributor_combo() # rellenamos combobox
        self.status_label.config(text="Datos cargados correctamente.") # mensaje de carga de datos generada correctamente

    def show_preview(self, preview): # Mostramos los datos en la tabla
        self.tree.delete(*self.tree.get_children()) # limpiamos la tabla actual
        for _, row in preview.iterrows(): # cargamos la tabla con los datos nuevos
            self.tree.insert("", "end", values=(row["Toma de datos"], row["Provincia"]))

    def populate_distributor_combo(self): # Llenamos el combobox 
        distributors = [ # Lista de distruidoras existentes
            'Precio gasolina 95 E5',
            'Precio gasolina 98 E5',
            'Precio gasóleo A'
        ]
        self.distributor_combo['values'] = distributors # rellanamos combobox con la lista
        if distributors: # distribuidora por defecto es 'Precio gasolina 95 E5' (la primera)
            self.distributor_combo.current(0)

    def generate_distributor_graph(self): # Generamos grafica para la distribuidora seleccionada en el combobox
        if self.data is None or self.data.empty: # Si no hay datos cargados mostramos este mensaje
            messagebox.showerror("Error", "Primero carga los datos de una provincia.")
            return

        distributor = self.distributor_combo.get()
        if not distributor: # Si no tenemos una distribuidora seleccionada mostramos este mensaje
            messagebox.showerror("Error", "Selecciona una distribuidora para generar la gráfica.")
            return

        try:
            self.status_label.config(text=f"Generando gráfica para {distributor}...") # mostramos que se esta generando x distribuidora
            self.root.update_idletasks() # actualizamos interfaz para procesar tareas pendientes (no es esencial)

            predicciones = obtener_predicciones(self.data, [distributor]) # Generamos la grafica

            if distributor in predicciones and not predicciones[distributor].empty: # comprobamos si la distribuidora seleccionada existe en predicciones (dicc dist)
                                                                                    # comprobamos si los datos de la distribuidora no estan vacios en el diccionario predicciones
                self.display_graph(predicciones[distributor], titulo=f"Predicción de {distributor}") # enseñamos grafica
                self.status_label.config(text="Gráfica generada correctamente.") # enseñamos label de generacion grafica correcta
            else:
                messagebox.showerror("Error", "No se pudieron generar predicciones para la distribuidora seleccionada.") # si la distribuidora no exite o no tiene  datos
        except Exception as e: # excepciones
            messagebox.showerror("Error", str(e))

    def display_graph(self, forecast, titulo): # mostramos grafica en una nueva ventana separada
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.configure(bg="#1e1e1e")

        # Crear la figura y graficar
        fig, ax = plt.subplots(figsize=(14, 4)) # creamos figura con dimensiones (6,4)
        ax.plot(forecast['Fecha'], forecast['Precio Estimado'], label='Precio Estimado', color='blue') # eje x es la fecha y eje y es el precio 
                                                                                                       # estamida de los datos atribuidos de la clase mainV3 
        ax.fill_between( # creamos una region sombreada establecida entre los limites inferior y superiores
            forecast['Fecha'], forecast['Límite Inferior'], forecast['Límite Superior'], 
            color='lightblue', alpha=0.4, label='Intervalo de Confianza'
        )
        # Detalles visuales
        ax.set_title(titulo, color='white')
        ax.set_xlabel('Fecha', color='white')
        ax.set_ylabel('Precio', color='white')
        ax.tick_params(colors='white')
        ax.legend()
        ax.grid(True)
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#2e2e2e')

       # creamos la ventana con la figura de la grafica
        canvas = FigureCanvasTkAgg(fig, master=ventana) 
        canvas.draw() 
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Boton para cerrar la ventana
        boton_cerrar = ttk.Button(ventana, text="Cerrar", command=ventana.destroy)
        boton_cerrar.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()

    # Simular un modelo y datos
    class MockModel:
        def predict(self, X_test):
            return np.random.rand(len(X_test), 7)  # Simular una predicción para 7 clases

    model = MockModel()
    hist = type('Hist', (object,), {"history": {
        "loss": [0.5, 0.4, 0.3],
        "val_loss": [0.6, 0.5, 0.4],
        "accuracy": [0.7, 0.8, 0.9],
        "val_accuracy": [0.65, 0.75, 0.85]
    }})

    X_test = np.random.rand(10, 3)
    y_test = np.random.randint(0, 7, size=(10,))

    app = VisualApp(root, model, hist, X_test, y_test)

    # Estilo oscuro para ttk widgets
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#2e2e2e", foreground="#ffffff", fieldbackground="#2e2e2e")
    style.configure("Treeview.Heading", background="#3c3c3c", foreground="#ffffff")
    style.configure("TButton", background="#3c3c3c", foreground="#ffffff")
    style.map("TButton", background=[("active", "#5c5c5c")])

    root.mainloop()
