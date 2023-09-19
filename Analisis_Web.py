import streamlit as st
import time
import os
import numpy as np
import pandas as pd
from datetime import datetime
import re


file_buffer = st.sidebar.file_uploader("Upload a file")

if file_buffer is not None:

    df_xlsx_file = pd.read_excel(file_buffer, engine='openpyxl')

    # Obtiene los nombres de las columnas que contienen la palabra 'Gasbag'
    columnas_gasbag = [columna for columna in df_xlsx_file.columns if 'Gasbag' in columna]

    # Imprime los nombres de las columnas que cumplen con el criterio
    max = 0
    for columna in columnas_gasbag:
        partes = columna.split('/')
        numero = re.search(r'\d+', partes[0])
        numero = numero.group()
        if max < int(numero):
            max = int(numero)

    vector = np.arange(1, max+1)

    gasbag_analized = st.sidebar.selectbox('Gasbag to analyze',  vector)

    # Seleccionar columnas que contienen 'Gasbag' en el nombre
    
    
    columnas_gasbag = df_xlsx_file.columns[df_xlsx_file.columns.str.contains('Gasbag ' + str(gasbag_analized) + ' ')]
    nombres_columnas = ['Tiempo'] + list(columnas_gasbag)

    # Crea un nuevo DataFrame con las columnas seleccionadas
    nuevo_df = df_xlsx_file[nombres_columnas]

    # Asegúrate de que la columna 'Tiempo' esté en un formato de fecha y hora
    nuevo_df['Tiempo'] = pd.to_datetime(nuevo_df['Tiempo'])

    # Ordena el DataFrame por la columna 'Tiempo'
    nuevo_df_ordenado = nuevo_df.sort_values(by='Tiempo')

    # Define las fechas y horas de inicio y fin del período deseado
    fecha_inicio = '2023-09-05 08:00:00'
    fecha_fin = '2023-09-05 10:00:00'

    # Filtra el DataFrame por fecha y hora
    df_filtrado = nuevo_df_ordenado[(nuevo_df_ordenado['Tiempo'] >= fecha_inicio) & (nuevo_df_ordenado['Tiempo'] <= fecha_fin)]

    # Selecciona la columna 'Tiempo' y obtén las fechas únicas
    fechas_unicas = nuevo_df_ordenado['Tiempo'].dt.date.unique()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        selected_date_from = st.selectbox('Date from',  fechas_unicas)
    with col2:
        selected_date_to = st.selectbox('Date to',  fechas_unicas)

    # Filtra las filas correspondientes al día específico
    filas_dia_from = nuevo_df_ordenado[nuevo_df_ordenado['Tiempo'].dt.date == selected_date_from]
    filas_dia_to = nuevo_df_ordenado[nuevo_df_ordenado['Tiempo'].dt.date == selected_date_from]

    # Extrae las horas de las filas del día específico
    horas_unicas_from = filas_dia_from['Tiempo'].dt.hour
    horas_unicas_to = filas_dia_to['Tiempo'].dt.hour

    col3, col4 = st.sidebar.columns(2)
    with col3:
        selected_hour_from = st.selectbox('Hour from',  horas_unicas_from)
    with col4:
        selected_hour_to = st.selectbox('Hour to',  horas_unicas_to)

    # FILTRAMOS DATASET CON FECHAS Y HORAS

    # Convierte las fechas y horas a objetos datetime
    fecha_inicio_dt = pd.to_datetime(str(selected_date_from) + ' ' + str(selected_hour_from) + ':00:00')
    fecha_fin_dt = pd.to_datetime(str(selected_date_to) + ' ' + str(selected_hour_to) + ':00:00')

    df_filtrado = nuevo_df_ordenado[(nuevo_df_ordenado['Tiempo'] >= fecha_inicio_dt) & (nuevo_df_ordenado['Tiempo'] <= fecha_fin_dt)]

    st.subheader('Filtered data')
    st.write(df_filtrado)

    




    # HALLAMOS LAS MEDIAS DE LOS SENSORES

    columnas_filtradas = df_filtrado.drop(columns=df_filtrado.columns[df_filtrado.columns.str.contains('Tiempo|gbag|gcount')])
    # Calcular la media de cada columna
    medias_por_columna = columnas_filtradas.mean()

    columnes = st.columns(len(medias_por_columna))

    # Ver las medias
    i=0
    for columna, media in medias_por_columna.items():
        nombre = columna.split('/')[1]
        with columnes[i]:
            st.metric(f'{nombre}', round(media,2))
        i=i+1


    


    # HALLAMOS VALORES PARA LAS 23:00

    columna_gbag = df_filtrado.columns[df_filtrado.columns.str.contains('gbag')]
    columna_gcount = df_filtrado.columns[df_filtrado.columns.str.contains('gcount')]

    # Filtrar las filas donde la hora sea 23
    df_filtrado_23h = df_filtrado[df_filtrado['Tiempo'].dt.hour == 23]
    df_filtrado_23h = df_filtrado_23h[['Tiempo'] + list(columna_gbag) + list(columna_gcount)]

    # Muestra las filas filtradas
    st.subheader('Data 23h')
    st.write(df_filtrado_23h)