import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mainV3 import obtener_datos_por_provincia, previsualizar_datos, obtener_predicciones, graficar_predicciones
import matplotlib.pyplot as plt

class VisualApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Predicción de Precios de Combustibles")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")  # Fondo oscuro

        # Título
        self.title_label = tk.Label(
            root, text="Predicción de Precios de Combustibles", font=("Arial", 16), bg="#1e1e1e", fg="#ffffff"
        )
        self.title_label.pack(pady=10)

        # Entrada para la provincia
        self.province_label = tk.Label(root, text="Nombre de la Provincia:", bg="#1e1e1e", fg="#ffffff")
        self.province_label.pack(pady=5)
        self.province_entry = tk.Entry(root, width=40, bg="#2e2e2e", fg="#ffffff", insertbackground="#ffffff")
        self.province_entry.pack(pady=5)

        # Botón para cargar datos
        self.load_button = tk.Button(
            root, text="Cargar Datos", command=self.load_data, bg="#3c3c3c", fg="#ffffff"
        )
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

        # Botón para generar gráfica de distribuidora
        self.predict_distributor_button = tk.Button(
            root, text="Generar Gráfica de Distribuidora", command=self.generate_distributor_graph, bg="#3c3c3c", fg="#ffffff"
        )
        self.predict_distributor_button.pack(pady=10)

        # Estado
        self.status_label = tk.Label(root, text="", fg="#00ff00", bg="#1e1e1e", font=("Arial", 10))
        self.status_label.pack(pady=10)

        self.data = None

    def load_data(self):
        """Cargar los datos de la provincia especificada."""
        province = self.province_entry.get().strip().upper()
        if not province:
            messagebox.showerror("Error de entrada", "Por favor, proporciona el nombre de la provincia.")
            return

        # Obtener datos por provincia
        directory = "ProyectoComputacion_I/Actividad/Download/"
        self.data = obtener_datos_por_provincia(directory, province)

        if self.data.empty:
            messagebox.showerror("Error", f"No se encontraron datos para la provincia: {province}.")
            self.tree.delete(*self.tree.get_children())  # Limpiar la tabla
            self.distributor_combo['values'] = []  # Limpiar el ComboBox
            return

        # Mostrar previsualización de datos
        self.show_preview(previsualizar_datos(self.data))
        self.populate_distributor_combo()
        self.status_label.config(text="Datos cargados correctamente.")

    def show_preview(self, preview):
        """Mostrar previsualización de los datos en la tabla."""
        self.tree.delete(*self.tree.get_children())
        for _, row in preview.iterrows():
            self.tree.insert("", "end", values=(row["Toma de datos"], row["Provincia"]))

    def populate_distributor_combo(self):
        """Llenar el ComboBox con las distribuidoras disponibles."""
        distributors = [
            'Precio gasolina 95 E5',
            'Precio gasolina 98 E5',
            'Precio gasóleo A'
        ]
        self.distributor_combo['values'] = distributors
        if distributors:
            self.distributor_combo.current(0)

    def generate_distributor_graph(self):
        """Generar gráfica para la distribuidora seleccionada y mostrarla en el panel."""
        if self.data is None or self.data.empty:
            messagebox.showerror("Error", "Primero carga los datos de una provincia.")
            return

        distributor = self.distributor_combo.get()
        if not distributor:
            messagebox.showerror("Error", "Selecciona una distribuidora para generar la gráfica.")
            return

        try:
            self.status_label.config(text=f"Generando gráfica para {distributor}...")
            self.root.update_idletasks()

            # Generar y graficar predicción
            predicciones = obtener_predicciones(self.data, [distributor])

            if distributor in predicciones and not predicciones[distributor].empty:
                self.display_graph(predicciones[distributor], titulo=f"Predicción de {distributor}")
                self.status_label.config(text="Gráfica generada correctamente.")
            else:
                messagebox.showerror("Error", "No se pudieron generar predicciones para la distribuidora seleccionada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_graph(self, forecast, titulo):
        """Mostrar la gráfica en una nueva ventana separada."""
        # Crear una nueva ventana
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.configure(bg="#1e1e1e")

        # Crear la figura y graficar
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(forecast['Fecha'], forecast['Precio Estimado'], label='Precio Estimado', color='blue')
        ax.fill_between(
            forecast['Fecha'], forecast['Límite Inferior'], forecast['Límite Superior'],
            color='lightblue', alpha=0.4, label='Intervalo de Confianza'
        )
        ax.set_title(titulo, color='white')
        ax.set_xlabel('Fecha', color='white')
        ax.set_ylabel('Precio', color='white')
        ax.tick_params(colors='white')
        ax.legend()
        ax.grid(True)
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#2e2e2e')

        # Integrar la figura en la ventana
        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Botón para cerrar la ventana
        boton_cerrar = ttk.Button(ventana, text="Cerrar", command=ventana.destroy)
        boton_cerrar.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualApp(root)

    # Estilo oscuro para ttk widgets
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#2e2e2e", foreground="#ffffff", fieldbackground="#2e2e2e")
    style.configure("Treeview.Heading", background="#3c3c3c", foreground="#ffffff")

    root.mainloop()
