import tkinter as tk
from tkinter import messagebox
from scapping import descargar_archivo
from convert import convert
from clean_pc import main as clean_main

class VisualApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gas Station Price Data Pipeline")

        # Buttons for each step
        self.scrap_button = tk.Button(root, text="1. Scrape Data", command=self.scrape_data)
        self.scrap_button.pack(pady=10)

        self.convert_button = tk.Button(root, text="2. Convert Data", command=self.convert_data, state=tk.DISABLED)
        self.convert_button.pack(pady=10)

        self.clean_button = tk.Button(root, text="3. Clean Data", command=self.clean_data, state=tk.DISABLED)
        self.clean_button.pack(pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=10)

        self.output_label = tk.Label(root, text="Output Messages Will Appear Here", wraplength=400, justify="center")
        self.output_label.pack(pady=20)

    def scrape_data(self):
        try:
            output = descargar_archivo()
            self.output_label.config(text="Scraping Completed: File Downloaded.")
            self.convert_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Scraping Failed: {e}")

    def convert_data(self):
        try:
            convert("ProyectoComputacion_I/Actividad/Download/", "ProyectoComputacion_I/Actividad/Output/")
            self.output_label.config(text="Conversion Completed: File Converted to CSV.")
            self.clean_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Conversion Failed: {e}")

    def clean_data(self):
        try:
            clean_main()
            self.output_label.config(text="Cleaning Completed: Data Processed and Saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Cleaning Failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualApp(root)
    root.mainloop()
