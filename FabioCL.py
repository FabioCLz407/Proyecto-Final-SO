import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de Streamlit
st.title('Análisis de Datos de Salud y Economía')

# Cargar el archivo CSV usando el cargador de archivos de Streamlit
archivo_csv = st.file_uploader("Sube tu archivo CSV", type="csv")

if archivo_csv:
    try:
        # Cargar los datos
        data = pd.read_csv(archivo_csv)

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
            plt.grid(True)
            st.pyplot(plt.gcf())
            plt.close()

        # Gráfico de Expectativa de Vida a lo largo de los años (Líneas)
        plot_and_show(data, 'Year', 'Life expectancy ', 'Life Expectancy Over the Years', 'Year', 'Life Expectancy', 'line', 'teal')

        # Gráfico de Mortalidad Adulta a lo largo de los años (Barras)
        plot_and_show(data, 'Year', 'Adult Mortality', 'Adult Mortality Over the Years', 'Year', 'Adult Mortality', 'bar', 'coral')

        # Gráfico de Muertes Infantiles a lo largo de los años (Líneas)
        plot_and_show(data, 'Year', 'infant deaths', 'Infant Deaths Over the Years', 'Year', 'Infant Deaths', 'line', 'green')

        # Gráfico de Consumo de Alcohol a lo largo de los años (Barras)
        plot_and_show(data, 'Year', 'Alcohol', 'Alcohol Consumption Over the Years', 'Year', 'Alcohol Consumption', 'bar', 'orange')

        # Gráfico de PIB a lo largo de los años (Líneas)
        plot_and_show(data, 'Year', 'GDP', 'GDP Over the Years', 'Year', 'GDP', 'line', 'purple')

        # Gráfico de Escolaridad a lo largo de los años (Barras)
        plot_and_show(data, 'Year', 'Schooling', 'Schooling Over the Years', 'Year', 'Schooling', 'bar', 'blue')

    except pd.errors.EmptyDataError:
        st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")