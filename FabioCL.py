import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np
import requests
from io import StringIO

# Configuración de Streamlit
st.title('Análisis de Datos de Spotify 2023')

# URL del archivo CSV en Google Drive
url = 'https://drive.google.com/uc?id=18EWnM90OV5zUTzJRvUtXnM7qrFibKAxO'

@st.cache_data
def load_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Lanza un error si la solicitud falla
    data = pd.read_csv(StringIO(response.text), encoding='latin1', on_bad_lines='skip')
    return data

# Cargar los datos desde la URL
try:
    data = load_data(url)

    # Limpiar los nombres de las columnas
    data.columns = data.columns.str.strip()

    # Limitar el número de filas para evitar sobrecarga
    st.sidebar.header('Opciones de Datos')
    num_rows = st.sidebar.slider('Número de filas para mostrar', min_value=10, max_value=100, value=30)
    
    limited_data = data.head(num_rows)

    # Mostrar el limitador de datos debajo del título
    st.write(f"Mostrando las primeras {num_rows} filas del dataset:")
    st.write(limited_data)

    # Función para graficar y mostrar gráficos en Streamlit
    def plot_and_show(data, x, y, title, xlabel, ylabel, plot_type='line', color='blue', add_regression=False, description=''):
        plt.figure(figsize=(12, 8))
        if plot_type == 'line':
            sns.lineplot(x=x, y=y, data=data, color=color)
        elif plot_type == 'bar':
            sns.barplot(x=x, y=y, data=data, color=color)
        elif plot_type == 'scatter':
            sns.scatterplot(x=x, y=y, data=data, color=color)
            if add_regression:
                x_values = data[x].values.reshape(-1, 1)
                y_values = data[y].values
                model = LinearRegression()
                model.fit(x_values, y_values)
                y_pred = model.predict(x_values)
                r2 = r2_score(y_values, y_pred)
                plt.plot(data[x], y_pred, color='red')
                plt.text(0.05, 0.95, f'$R^2$: {r2:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        elif plot_type == 'pie':
            data_to_plot = data.groupby(x)[y].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            wedges, texts, autotexts = ax.pie(data_to_plot[y], labels=data_to_plot[x], autopct='%1.1f%%', colors=color)
            ax.legend(wedges, data_to_plot[x], title=x, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            plt.title(title)
            plt.axis('equal')
            st.pyplot(fig)
            return
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=90)
        plt.grid(True)
        st.pyplot(plt.gcf())
        plt.close()

        # Añadir descripción
        st.write(description)

    # Gráfico de Streams a lo largo de las canciones (Barras)
    plot_and_show(limited_data, 'track_name', 'streams', 'Distribución de Streams por Canción', 'Canción', 'Streams', 'bar', 'coral')

    # Gráfico de Popularidad de YouTube a lo largo de las canciones (Barras)
    plot_and_show(limited_data, 'track_name', 'in_spotify_playlists', 'Distribución de Popularidad en Playlists', 'Canción', 'Número de Playlists', 'bar', 'orange')

    # Gráfico de Danceability de Spotify a lo largo de las canciones (Líneas)
    plot_and_show(limited_data, 'track_name', 'danceability_%', 'Distribución de Danceability por Canción', 'Canción', 'Danceability (%)', 'line', 'purple')

    # Gráfico de Energy de Spotify a lo largo de las canciones (Líneas)
    plot_and_show(limited_data, 'track_name', 'energy_%', 'Distribución de Energy por Canción', 'Canción', 'Energy (%)', 'line', 'blue')

    # Gráfico de Valence de Spotify a lo largo de las canciones (Líneas)
    plot_and_show(limited_data, 'track_name', 'valence_%', 'Distribución de Valence por Canción', 'Canción', 'Valence (%)', 'line', 'green')

    # Gráfico de torta para Popularidad en Playlists
    plot_and_show(limited_data, 'track_name', 'in_spotify_playlists', 'Distribución de Popularidad en Playlists', 'Canción', 'Número de Playlists', 'pie', sns.color_palette("plasma"))

    # Gráfico de regresión lineal personalizada
    st.subheader('Regresión Lineal Personalizada')
    st.write("Selecciona dos columnas numéricas para realizar una regresión lineal y ver la relación entre ellas.")

    columnas = limited_data.select_dtypes(include=[np.number]).columns.tolist()
    x_col = st.selectbox('Selecciona la columna X', columnas)
    y_col = st.selectbox('Selecciona la columna Y', columnas)

    if st.button('Generar Regresión Lineal'):
        if pd.api.types.is_numeric_dtype(limited_data[x_col]) and pd.api.types.is_numeric_dtype(limited_data[y_col]):
            st.write(f'Regresión lineal entre {x_col} y {y_col}')
            plot_and_show(limited_data, x_col, y_col, f'Relación entre {x_col} y {y_col}', x_col, y_col, 'scatter', 'blue', add_regression=True, description=f'Relación de regresión lineal entre {x_col} y {y_col}.')
        else:
            st.error("Ambas columnas seleccionadas deben contener datos numéricos.")
except requests.RequestException as e:
    st.error(f"Ocurrió un error al cargar el archivo: {e}")
except pd.errors.EmptyDataError:
    st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el archivo: {e}")
