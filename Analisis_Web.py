import streamlit as st
import time
import os
import numpy as np
import pandas as pd
from datetime import datetime
import re

st.sidebar.caption('BETA VERSION 2023')

file_buffer = st.sidebar.file_uploader("Upload a xlsx file")

tab1, tab2, tab3 = st.tabs(["Automatic analysis", "Filter analysis", "Raw Excel"])

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

    
    with tab1:

        vector = np.arange(1, max+1)

        gasbag_automatic = st.selectbox('Gasbag to analyze automatic',  vector)

        columnas_gasbag = df_xlsx_file.columns[df_xlsx_file.columns.str.contains('Gasbag ' + str(gasbag_automatic) + ' ')]
        nombres_columnas = ['Tiempo'] + list(columnas_gasbag)

        # Crea un nuevo DataFrame con las columnas seleccionadas
        nuevo_df = df_xlsx_file[nombres_columnas]

        # Asegurate de que la columna 'Tiempo' este en un formato de fecha y hora
        nuevo_df['Tiempo'] = pd.to_datetime(nuevo_df['Tiempo'])

        # Ordena el DataFrame por la columna 'Tiempo'
        nuevo_df_ordenado = nuevo_df.sort_values(by='Tiempo')



        # ------------------------------------------------------------------------------------------
        # HALLAMOS LAS MEDIAS DE LOS SENSORES PARA TODOS LOS DIAS

        # Agrupa por dia y calcula la media para cada grupo
        df_agrupado = nuevo_df_ordenado.drop(columns=nuevo_df_ordenado.columns[nuevo_df_ordenado.columns.str.contains('gbag|gcount')])
        df_agrupado = df_agrupado.groupby(df_agrupado['Tiempo'].dt.date).mean()
        df_agrupado = df_agrupado.drop(columns=df_agrupado.columns[df_agrupado.columns.str.contains('Tiempo')])

        # Ver el DataFrame resultante con las medias por dia
        st.subheader('Average values')
        st.write(df_agrupado)


        # ------------------------------------------------------------------------------------------
        # HALLAMOS TODOS LOS VALORES DE LAS 23:00

        columna_gbag = nuevo_df_ordenado.columns[nuevo_df_ordenado.columns.str.contains('gbag')]
        columna_gcount = nuevo_df_ordenado.columns[nuevo_df_ordenado.columns.str.contains('gcount')]

        # Filtrar las filas donde la hora sea 23
        df_filtrado_23h = nuevo_df_ordenado[nuevo_df_ordenado['Tiempo'].dt.hour == 23]
        df_filtrado_23h = df_filtrado_23h[['Tiempo'] + list(columna_gbag) + list(columna_gcount)]

        st.subheader('Data 23h')
        st.write(df_filtrado_23h)

    with tab2:
    
    
        vector = np.arange(1, max+1)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            gasbag_analized = st.selectbox('Gasbag to analyze',  vector)

        # Seleccionar columnas que contienen 'Gasbag' en el nombre
        
        
        columnas_gasbag = df_xlsx_file.columns[df_xlsx_file.columns.str.contains('Gasbag ' + str(gasbag_analized) + ' ')]
        nombres_columnas = ['Tiempo'] + list(columnas_gasbag)

        # Crea un nuevo DataFrame con las columnas seleccionadas
        nuevo_df = df_xlsx_file[nombres_columnas]

        # Asegurate de que la columna 'Tiempo' este en un formato de fecha y hora
        nuevo_df['Tiempo'] = pd.to_datetime(nuevo_df['Tiempo'])

        # Ordena el DataFrame por la columna 'Tiempo'
        nuevo_df_ordenado = nuevo_df.sort_values(by='Tiempo')

        # Selecciona la columna 'Tiempo' y obtén las fechas únicas
        fechas_unicas = nuevo_df_ordenado['Tiempo'].dt.date.unique()
        
        
        with col2:
            selected_date_from = st.selectbox('Date from',  fechas_unicas)
        with col3:
            selected_date_to = st.selectbox('Date to',  fechas_unicas)

        # Filtra las filas correspondientes al día específico
        filas_dia_from = nuevo_df_ordenado[nuevo_df_ordenado['Tiempo'].dt.date == selected_date_from]
        filas_dia_to = nuevo_df_ordenado[nuevo_df_ordenado['Tiempo'].dt.date == selected_date_from]

        # Extrae las horas de las filas del día específico
        horas_unicas_from = filas_dia_from['Tiempo'].dt.hour
        horas_unicas_to = filas_dia_to['Tiempo'].dt.hour

        with col4:
            selected_hour_from = st.selectbox('Hour from',  horas_unicas_from)
        with col5:
            selected_hour_to = st.selectbox('Hour to',  horas_unicas_to)

        # FILTRAMOS DATASET CON FECHAS Y HORAS

        # Convierte las fechas y horas a objetos datetime
        fecha_inicio_dt = pd.to_datetime(str(selected_date_from) + ' ' + str(selected_hour_from) + ':00:00')
        fecha_fin_dt = pd.to_datetime(str(selected_date_to) + ' ' + str(selected_hour_to) + ':00:00')

        df_filtrado = nuevo_df_ordenado[(nuevo_df_ordenado['Tiempo'] >= fecha_inicio_dt) & (nuevo_df_ordenado['Tiempo'] <= fecha_fin_dt)]

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

    with tab3:

        st.write(df_xlsx_file)