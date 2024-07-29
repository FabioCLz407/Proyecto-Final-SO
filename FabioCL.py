import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de Streamlit
st.title('Análisis de Datos de Spotify 2023')

# Cargar el archivo CSV usando el cargador de archivos de Streamlit
archivo_csv = st.file_uploader("Sube tu archivo CSV", type="csv")

if archivo_csv:
    try:
        # Cargar los datos con encoding y manejo de errores
        data = pd.read_csv(archivo_csv, encoding='latin1', on_bad_lines='skip')

        # Limpiar los nombres de las columnas
        data.columns = data.columns.str.strip()

        # Mostrar las primeras filas del dataset
        st.write(data.head())

        # Función para graficar y mostrar gráficos en Streamlit
        def plot_and_show(data, x, y, title, xlabel, ylabel, plot_type='line', color='blue'):
            plt.figure(figsize=(10, 6))
            if plot_type == 'line':
                sns.lineplot(x=x, y=y, data=data, color=color)
            elif plot_type == 'bar':
                sns.barplot(x=x, y=y, data=data, color=color)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.xticks(rotation=90)
            plt.grid(True)
            st.pyplot(plt.gcf())
            plt.close()

        # Gráfico de Streams a lo largo de las canciones (Barras)
        plot_and_show(data, 'track_name', 'streams', 'Spotify Streams per Track', 'Track', 'Streams', 'bar', 'coral')

        # Gráfico de Popularidad de YouTube a lo largo de las canciones (Barras)
        plot_and_show(data, 'track_name', 'in_spotify_playlists', 'Popularity in Spotify Playlists', 'Track', 'Playlists', 'bar', 'orange')

        # Gráfico de Danceability de Spotify a lo largo de las canciones (Líneas)
        plot_and_show(data, 'track_name', 'danceability_%', 'Spotify Danceability per Track', 'Track', 'Danceability (%)', 'line', 'purple')

        # Gráfico de Energy de Spotify a lo largo de las canciones (Líneas)
        plot_and_show(data, 'track_name', 'energy_%', 'Spotify Energy per Track', 'Track', 'Energy (%)', 'line', 'blue')

        # Gráfico de Valence de Spotify a lo largo de las canciones (Líneas)
        plot_and_show(data, 'track_name', 'valence_%', 'Spotify Valence per Track', 'Track', 'Valence (%)', 'line', 'green')

    except pd.errors.EmptyDataError:
        st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
