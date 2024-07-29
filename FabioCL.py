import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Configuración de Streamlit
st.title('Análisis de Datos de Spotify 2023 con Random Forest')

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

        # Seleccionar las características y la variable objetivo
        features = data[['released_year', 'released_month', 'released_day', 'in_spotify_playlists', 
                         'in_spotify_charts', 'streams', 'in_apple_playlists', 'bpm', 'key', 'mode', 
                         'danceability_%', 'valence_%', 'energy_%', 'acousticness_%', 'instrumentalness_%', 
                         'liveness_%', 'speechiness_%']]
        target = data['streams']

        # Dividir los datos en conjunto de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

        # Entrenar el modelo de Random Forest
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Realizar predicciones
        predictions = model.predict(X_test)

        # Calcular el error cuadrático medio
        mse = mean_squared_error(y_test, predictions)
        st.write(f"Error cuadrático medio (MSE): {mse}")

        # Importancia de las características
        feature_importances = model.feature_importances_
        features_names = features.columns
        importance_df = pd.DataFrame({'Feature': features_names, 'Importance': feature_importances})
        importance_df = importance_df.sort_values(by='Importance', ascending=False)

        # Visualización de la importancia de las características
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=importance_df)
        plt.title('Importancia de las características')
        st.pyplot(plt.gcf())
        plt.close()

        # Visualización de las predicciones vs valores reales
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, predictions, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
        plt.xlabel('Valores reales')
        plt.ylabel('Predicciones')
        plt.title('Predicciones vs Valores reales')
        st.pyplot(plt.gcf())
        plt.close()

    except pd.errors.EmptyDataError:
        st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
