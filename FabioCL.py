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

    # Convertir columnas a numéricas si es necesario
    limited_data['streams'] = pd.to_numeric(limited_data['streams'], errors='coerce')
    limited_data['in_spotify_playlists'] = pd.to_numeric(limited_data['in_spotify_playlists'], errors='coerce')
    limited_data['danceability_%'] = pd.to_numeric(limited_data['danceability_%'], errors='coerce')
    limited_data['energy_%'] = pd.to_numeric(limited_data['energy_%'], errors='coerce')
    limited_data['valence_%'] = pd.to_numeric(limited_data['valence_%'], errors='coerce')

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
    plot_and_show(limited_data, 'track_name', 'streams', 'Distribución de Streams por Canción', 'Canción', 'Streams', 'bar', 'coral', description='Este gráfico muestra la distribución del número de streams para cada canción. Las canciones con más streams están representadas con barras más altas.')

    # Gráfico de Popularidad en Playlists a lo largo de las canciones (Barras)
    plot_and_show(limited_data, 'track_name', 'in_spotify_playlists', 'Distribución de Popularidad en Playlists', 'Canción', 'Número de Playlists', 'bar', 'orange', description='Este gráfico muestra el número de playlists de Spotify en las que cada canción aparece. Las canciones más populares en playlists tienen barras más altas.')

    # Gráfico de Danceability de Spotify a lo largo de las canciones (Líneas)
    plot_and_show(limited_data, 'track_name', 'danceability_%', 'Distribución de Danceability por Canción', 'Canción', 'Danceability (%)', 'line', 'purple', description='Este gráfico muestra el porcentaje de danceability para cada canción. Las canciones con mayor danceability tienen valores más altos.')

    # Gráfico de Energy de Spotify a lo largo de las canciones (Líneas)
    plot_and_show(limited_data, 'track_name', 'energy_%', 'Distribución de Energy por Canción', 'Canción', 'Energy (%)', 'line', 'blue', description='Este gráfico muestra el porcentaje de energía para cada canción. Las canciones con mayor energía tienen valores más altos.')

    # Gráfico de Valence de Spotify a lo largo de las canciones (Líneas)
    plot_and_show(limited_data, 'track_name', 'valence_%', 'Distribución de Valence por Canción', 'Canción', 'Valence (%)', 'line', 'green', description='Este gráfico muestra el porcentaje de valence para cada canción. Las canciones con mayor valence tienen valores más altos.')

    # Gráfico de torta para Popularidad en Playlists
    plot_and_show(limited_data, 'track_name', 'in_spotify_playlists', 'Distribución de Popularidad en Playlists', 'Canción', 'Número de Playlists', 'pie', sns.color_palette("plasma"), description='Este gráfico de torta muestra la proporción de cada canción en las playlists de Spotify. Las canciones más representadas en playlists tienen porciones más grandes.')

    # Regresión Lineal entre "streams" y "in_spotify_playlists"
    st.subheader('Regresión Lineal entre Streams y Popularidad en Playlists')
    st.write("A continuación, se muestra una regresión lineal que analiza la relación entre el número de streams y el número de playlists en las que aparece cada canción.")

    if pd.api.types.is_numeric_dtype(limited_data['streams']) and pd.api.types.is_numeric_dtype(limited_data['in_spotify_playlists']):
        plot_and_show(limited_data, 'in_spotify_playlists', 'streams', 'Regresión Lineal entre Popularidad en Playlists y Streams', 'Número de Playlists', 'Streams', 'scatter', 'blue', add_regression=True, description='Este gráfico muestra la relación entre el número de playlists en las que aparece cada canción y el número de streams. La línea roja representa la regresión lineal, y el valor $R^2$ indica qué tan bien se ajusta el modelo a los datos.')
    else:
        st.error("Las columnas 'streams' y 'in_spotify_playlists' deben contener datos numéricos.")

except requests.RequestException as e:
    st.error(f"Ocurrió un error al cargar el archivo: {e}")
except pd.errors.EmptyDataError:
    st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el archivo: {e}")
