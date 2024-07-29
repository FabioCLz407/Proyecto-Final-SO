import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt

class ETLGUI:
    def __init__(self, master):
        self.master = master
        master.title("Proceso ETL")
        master.geometry("600x400")

        # Configuración del grid
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(5, weight=1)

        # Botón para seleccionar carpeta
        self.folder_button = tk.Button(master, text="Seleccionar carpeta de datos", command=self.select_folder)
        self.folder_button.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        # Entrada para rango de columnas
        tk.Label(master, text="Rango de columnas (ej. A:S):").grid(row=1, column=0, sticky="w", padx=10)
        self.column_range = tk.Entry(master)
        self.column_range.grid(row=1, column=0, pady=5, padx=150, sticky="ew")
        self.column_range.insert(0, "A:S")  # Valor predeterminado

        # Entrada para fila inicial
        tk.Label(master, text="Fila inicial:").grid(row=2, column=0, sticky="w", padx=10)
        self.start_row = tk.Entry(master)
        self.start_row.grid(row=2, column=0, pady=5, padx=150, sticky="ew")
        self.start_row.insert(0, "13")  # Valor predeterminado

        # Botón para iniciar proceso
        self.process_button = tk.Button(master, text="Iniciar proceso ETL", command=self.start_etl)
        self.process_button.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        # Barra de progreso
        self.progress = ttk.Progressbar(master, length=400, mode='determinate')
        self.progress.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        # Área de texto para mostrar resultados
        self.result_text = tk.Text(master, height=10)
        self.result_text.grid(row=5, column=0, pady=10, padx=10, sticky="nsew")

        self.folder_path = ""

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.result_text.insert(tk.END, f"Carpeta seleccionada: {self.folder_path}\n")

    def start_etl(self):
        if not self.folder_path:
            self.result_text.insert(tk.END, "Por favor, seleccione una carpeta primero.\n")
            return

        col_range = self.column_range.get()
        start_row = int(self.start_row.get()) if self.start_row.get().isdigit() else 13

        try:
            # Obtener lista de archivos Excel en la carpeta, excluyendo Out.xlsx
            excel_files = [f for f in os.listdir(self.folder_path) if f.endswith('.xlsx') and f != 'Out.xlsx']

            # Inicializar DataFrame final
            final_df = pd.DataFrame()

            # Configurar barra de progreso
            self.progress['value'] = 0
            self.progress['maximum'] = len(excel_files)

            column_names = ['OFICINA', 'CODIGO', 'NOMBRE', 'LINEA', 'GRUPO', 'PNG', 'U', 'VALOR', 'U2', 'VALOR2', 'LV1', 'VALORC', 'LV2', 'COL14', 'COL15', 'COL16', 'ANIO', 'MES', 'DIA']

            for file in excel_files:
                file_path = os.path.join(self.folder_path, file)
                
                # Leer archivo Excel
                df = pd.read_excel(file_path, usecols=col_range, skiprows=start_row-1, header=None, engine='openpyxl')
                
                # Asegurar que tenemos el número correcto de columnas
                if len(df.columns) < len(column_names) - 3:  # -3 porque añadiremos ANIO, MES, DIA después
                    df = df.reindex(columns=range(len(column_names) - 3))
                elif len(df.columns) > len(column_names) - 3:
                    df = df.iloc[:, :(len(column_names) - 3)]
                
                # Extraer año, mes y día del nombre del archivo
                try:
                    date_parts = file.split('.')
                    year, month, day = date_parts[1], date_parts[2], date_parts[3]
                except IndexError:
                    year, month, day = "0000", "00", "00"
                    self.result_text.insert(tk.END, f"Advertencia: No se pudo extraer la fecha del archivo {file}. Se usaron valores predeterminados.\n")
                
                # Añadir columnas de fecha
                df['ANIO'] = year
                df['MES'] = month
                df['DIA'] = day
                
                # Asignar nombres de columnas
                df.columns = column_names
                
                # Asegurar que 'VALOR' contiene solo datos numéricos
                df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')

                # Reemplazar NaN por ceros (o cualquier otro valor que consideres apropiado)
                df = df.fillna(0)

                # Concatenar al DataFrame final
                final_df = pd.concat([final_df, df], ignore_index=True)
                
                # Actualizar barra de progreso
                self.progress['value'] += 1
                self.master.update_idletasks()

            # Exportar a Excel
            output_path = os.path.join(self.folder_path, 'Out.xlsx')
            final_df.to_excel(output_path, index=False, engine='openpyxl')

            self.result_text.insert(tk.END, f"Proceso ETL completado. Archivo guardado en: {output_path}\n")
            self.result_text.insert(tk.END, f"Dimensiones del DataFrame final: {final_df.shape}\n")
            self.result_text.insert(tk.END, f"Primeras filas del DataFrame:\n{final_df.head().to_string()}\n")

            # Generar reportes gráficos
            self.generate_reports(final_df)

        except Exception as e:
            self.result_text.insert(tk.END, f"Error durante el proceso ETL: {str(e)}\n")
            messagebox.showerror("Error", f"Se produjo un error durante el proceso ETL: {str(e)}")

    def generate_reports(self, df):
        reports_folder = os.path.join(self.folder_path, 'Reportes')
        os.makedirs(reports_folder, exist_ok=True)

        try:
            # Gráfico 1: Promedio de valores por oficina
            plt.figure(figsize=(12, 6))
            df.groupby('OFICINA')['VALOR'].mean().plot(kind='bar')
            plt.title('Promedio de Valores por Oficina')
            plt.xlabel('Oficina')
            plt.ylabel('Valor Promedio')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(reports_folder, 'promedio_por_oficina.png'))
            plt.close()

            # Gráfico 2: Distribución de valores promedio
            plt.figure(figsize=(10, 6))
            df.groupby('CODIGO')['VALOR'].mean().hist(bins=50)
            plt.title('Distribución de Valores Promedio')
            plt.xlabel('Valor Promedio')
            plt.ylabel('Frecuencia')
            plt.tight_layout()
            plt.savefig(os.path.join(reports_folder, 'distribucion_valores_promedio.png'))
            plt.close()

            # Gráfico 3: Evolución temporal de valores promedio
            if df['ANIO'].nunique() > 1 or df['MES'].nunique() > 1:
                plt.figure(figsize=(12, 6))
                df.groupby(['ANIO', 'MES'])['VALOR'].mean().plot(kind='line')
                plt.title('Evolución Temporal de Valores Promedio')
                plt.xlabel('Año-Mes')
                plt.ylabel('Valor Promedio')
                plt.tight_layout()
                plt.savefig(os.path.join(reports_folder, 'evolucion_temporal_promedio.png'))
                plt.close()

            # Gráfico 4: Gráfico de torta para distribución de valores promedio por LINEA
            plt.figure(figsize=(10, 8))
            valores_promedio_por_linea = df.groupby('LINEA')['VALOR'].mean()
            valores_promedio_por_linea.plot(kind='pie', autopct='%1.1f%%')
            plt.title('Distribución de Valores Promedio por Línea')
            plt.ylabel('')
            plt.tight_layout()
            plt.savefig(os.path.join(reports_folder, 'distribucion_promedio_por_linea.png'))
            plt.close()

            self.result_text.insert(tk.END, f"Reportes gráficos de promedios generados en: {reports_folder}\n")

        except Exception as e:
            self.result_text.insert(tk.END, f"Error al generar reportes gráficos: {str(e)}\n")
            messagebox.showerror("Error", f"Se produjo un error al generar reportes gráficos: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    etl_gui = ETLGUI(root)
    root.mainloop()
