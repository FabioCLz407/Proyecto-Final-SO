import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

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

        # Convertir las columnas relevantes a tipo numérico
        numeric_cols = ['streams', 'in_spotify_playlists', 'danceability_%', 'energy_%', 'valence_%']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')

        # Limitar la cantidad de datos a mostrar
        max_rows = len(data)
        limit = st.slider('Número de filas a mostrar', min_value=10, max_value=max_rows, value=min(50, max_rows))
        limited_data = data.head(limit)
        st.write(limited_data)

        # Función para graficar y mostrar gráficos en Streamlit
        def plot_and_show(data, x, y, title, xlabel, ylabel, plot_type='line', color='blue', add_regression=False):
            plt.figure(figsize=(18, 8))  # Ajustar tamaño de la figura
            if plot_type == 'line':
                sns.lineplot(x=x, y=y, data=data, color=color)
            elif plot_type == 'bar':
                sns.barplot(x=x, y=y, data=data, color=color)
            elif plot_type == 'pie':
                pie_data = data[[x, y]].groupby(x).sum()
                fig, ax = plt.subplots(1, 2, figsize=(18, 8))  # Crear figura y ejes para dos gráficos
                
                # Graficar torta
                pie_data.plot.pie(y=y, labels=pie_data.index, autopct='%1.1f%%', colors=sns.color_palette(color), ax=ax[1])
                ax[1].set_title(title)
                
                # Mostrar lista al lado de la torta
                ax[0].axis('off')
                pie_data.reset_index().rename(columns={x: 'Categoría', y: 'Valor'}).plot(kind='barh', x='Categoría', y='Valor', ax=ax[0], color=color)
                ax[0].set_title('Distribución de Valores')
                ax[0].invert_yaxis()
            elif plot_type == 'scatter':
                sns.scatterplot(x=x, y=y, data=data, color=color)
                
                if add_regression:
                    # Ajuste de regresión lineal
                    X = data[[x]].dropna()
                    Y = data[[y]].dropna()
                    
                    # Asegurarse de que X y Y tienen el mismo tamaño
                    common_indices = X.index.intersection(Y.index)
                    X = X.loc[common_indices]
                    Y = Y.loc[common_indices]
                    
                    if len(X) > 1:  # Asegurarse de que hay suficientes datos para ajustar el modelo
                        model = LinearRegression()
                        model.fit(X, Y)
                        predictions = model.predict(X)
                        r2 = r2_score(Y, predictions)
                        
                        # Graficar línea de regresión
                        sns.regplot(x=x, y=y, data=data, scatter=False, color='red')
                        
                        # Mostrar \( R^2 \)
                        plt.title(f'{title}\n$R^2 = {r2:.2f}$')
                    else:
                        plt.title(f'{title}\nNo hay suficientes datos para calcular R^2')
                else:
                    plt.title(title)
                    
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.grid(True)
            st.pyplot(plt.gcf())
            plt.close()

        # Gráfico de Streams a lo largo de las canciones (Barras)
        plot_and_show(limited_data, 'track_name', 'streams', 'Número de Streams por Canción', 'Canción', 'Número de Streams', 'bar', 'coral')

        # Gráfico de Popularidad en Playlists de Spotify (Barras)
        plot_and_show(limited_data, 'track_name', 'in_spotify_playlists', 'Popularidad en Playlists de Spotify', 'Canción', 'Número de Playlists', 'bar', 'orange')

        # Gráfico de Danceability de Spotify (Líneas)
        plot_and_show(limited_data, 'track_name', 'danceability_%', 'Danceability de Spotify por Canción', 'Canción', 'Danceability (%)', 'line', 'purple')

        # Gráfico de Energy de Spotify (Líneas)
        plot_and_show(limited_data, 'track_name', 'energy_%', 'Energía de Spotify por Canción', 'Canción', 'Energía (%)', 'line', 'blue')

        # Gráfico de Valence de Spotify (Líneas)
        plot_and_show(limited_data, 'track_name', 'valence_%', 'Valence de Spotify por Canción', 'Canción', 'Valence (%)', 'line', 'green')

        # Gráfico de distribución de Streams (Torta)
        st.subheader('Distribución de Streams')
        plot_and_show(limited_data, 'track_name', 'streams', 'Distribución de Streams', 'Canción', 'Número de Streams', 'pie', sns.color_palette("viridis"))

        # Gráfico de distribución de Popularidad en Playlists (Torta)
        st.subheader('Distribución de Popularidad en Playlists')
        plot_and_show(limited_data, 'track_name', 'in_spotify_playlists', 'Distribución de Popularidad en Playlists', 'Canción', 'Número de Playlists', 'pie', sns.color_palette("magma"))

        # Seleccionar columnas para la regresión lineal
        st.sidebar.subheader('Regresión Lineal')
        x_col = st.sidebar.selectbox('Selecciona la columna para el eje X', numeric_cols)
        y_col = st.sidebar.selectbox('Selecciona la columna para el eje Y', numeric_cols)

        # Gráfico de relación lineal entre columnas seleccionadas
        if x_col and y_col:
            st.subheader(f'Relación entre {x_col} y {y_col}')
            plot_and_show(limited_data, x_col, y_col, f'Relación entre {x_col} y {y_col}', x_col, y_col, 'scatter', 'cyan', True)

    except pd.errors.EmptyDataError:
        st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
