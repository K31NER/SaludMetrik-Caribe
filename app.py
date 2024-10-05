import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración general de la página
st.set_page_config(
    page_icon="computadora.png",
    page_title="Proyecto",
    layout="wide"
)

st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

departamentos = [ "Bolívar", "Cartagena", "Sucre", "San Andrés y Providencia", "Córdoba"]
# Título
st.title(':orange[Analisis de las IPS en la zona caribe]')

# Cargar archivo CSV
st.sidebar.image("hospital.png")
st.sidebar.header('Opciones avanzadas', divider="red")
st.logo("icon.png")
file = "data.csv"
try:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Filtrar por los departamentos definidos
    filtered_df = df[df['Departamento'].isin(departamentos)].reset_index(drop=True)
    
    # Opciones en la barra lateral
    st.sidebar.subheader("Estadísticas",divider="orange")
    estadística = st.sidebar.button("Generar estadísticas")
    
    st.sidebar.subheader("Graficar",divider="orange")
    gráficos = st.sidebar.button("Generar gráficos")
    
    st.sidebar.subheader("Valores",divider="orange")
    nulos = st.sidebar.button("Ver valores nulos")
    
    st.sidebar.subheader("Todo",divider="orange")
    todo = st.sidebar.button("Generar todo")
    
    # Columnas numéricas
    numerical_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        # Mostrar datos filtrados
    st.subheader(f'Datos filtrados por departamentos del caribe',divider="orange")
    
    #dataframe filtrado
    st.dataframe(filtered_df)
    
    sin_null = filtered_df["num nivel atencion"].fillna(1)
    #sin los nulos
    st.dataframe(sin_null)
    
    #funciones 
    def v_nulos(filtered_df):
        st.subheader("Datos nulos",divider="orange")
        valores_null = filtered_df.isnull().sum()
        st.dataframe(valores_null,use_container_width=True)
        
    def estadisticas(filtered_df):
        st.subheader("Estadisticas",divider="orange")
        st.dataframe(filtered_df.describe(),use_container_width=True)
        
    
    if estadística:
        estadisticas(filtered_df)
        
    if nulos:
        v_nulos(filtered_df)  
    # ------- datos agrupados ------------- #
        
    st.header("Datos agrupados",divider="orange")
        
    #sacamos el numero de sedes por departamento
    num_sede = filtered_df.groupby("Departamento")["Código sede"].count().reset_index()
    
    # Renombrar la columna "Código sede" a "Número de Sede"
    num_sede = num_sede.rename(columns={"Código sede": "Número de Sedes"})
        
    #capacidad por departamento
    capacidad_departamento = filtered_df.groupby('Departamento')['num cantidad capacidad instalada'].sum().reset_index()
    
    #promedio de atencion por departamento
    prom_departamento = filtered_df.groupby("Departamento")["num nivel atencion"].mean().reset_index()
        
    #porcentaje de privadas y publicas
    # Agrupar por departamento y naturaleza, y contar el número de sedes
    sedes_naturaleza = filtered_df.groupby(['Departamento', 'naturaleza'])['Código sede'].count().reset_index()

    # Renombrar la columna de conteo
    sedes_naturaleza = sedes_naturaleza.rename(columns={'Código sede': 'Número de Sedes'})

    # Pivotar la tabla para que cada naturaleza (Pública/Privada) sea una columna
    tabla_naturaleza = sedes_naturaleza.pivot(index='Departamento', columns='naturaleza', values='Número de Sedes').reset_index()

    # Renombrar las columnas para que queden como "Públicas" y "Privadas"
    tabla_naturaleza = tabla_naturaleza.rename(columns={'Pública': 'Públicas', 'Privada': 'Privadas'})
    
    # Llenar valores NaN con 0 (si algún departamento no tiene sedes públicas o privadas)
    tabla_naturaleza = tabla_naturaleza.fillna(0)

    f1,f2 = st.columns(2)
    with f1:
        st.subheader("Sedes por departamento", divider="green")
        st.dataframe(num_sede,use_container_width=True,hide_index=True)
    with f2:
        st.subheader("capacidad por departamento", divider="green")
        st.dataframe(capacidad_departamento,use_container_width=True,hide_index=True)
    f3,f4 = st.columns(2)
    with f3:
        st.subheader("Promedio de atencion",divider="green")
        st.dataframe(prom_departamento,hide_index=True,use_container_width=True)
        
    with f4:
        st.subheader("Naturaleza de sede", divider="green")
        st.dataframe(tabla_naturaleza,hide_index=True , use_container_width=True)
        
    # --------------- Graficas ---------------- #
    def  graficar(filtered_df):
        st.subheader("Graficas",divider="orange")
        try:
            c1,c2,c3= st.columns(3)
            with c1:
                # Contar el número de sedes por departamento
                sedes_departamento = filtered_df.groupby('Departamento')['Código prestador'].count().reset_index()
                sedes_departamento.columns = ['Departamento', 'Número de Sedes']
                # Gráfico de pie
                fig_sedes = px.pie(sedes_departamento, values='Número de Sedes', names='Departamento',
                    title='Distribución del Número de Sedes por Departamento')
                st.plotly_chart(fig_sedes)
            
            with c2:
                prom_departamento = filtered_df.groupby("Departamento")["num nivel atencion"].mean().reset_index()
                fig_radar = px.line_polar(prom_departamento, r='num nivel atencion', theta='Departamento', 
                                    line_close=True, title='Nivel de Atención Promedio por Departamento',
                                    labels={'num nivel atencion': 'Promedio Nivel Atención'})
                st.plotly_chart(fig_radar)

            with c3:
                fig_naturaleza = px.bar(tabla_naturaleza, x='Departamento', y=['Públicas', 'Privadas'],
                                    title='Distribución de Sedes Públicas y Privadas por Departamento', 
                                    labels={'value': 'Número de Sedes'},
                                    barmode='stack')
                st.plotly_chart(fig_naturaleza)
                
            capacidad_departamento = filtered_df.groupby('Departamento')['num cantidad capacidad instalada'].sum().reset_index()
            # Gráfico de burbujas (scatter con tamaño de burbujas)
            fig_burbujas = px.scatter(capacidad_departamento, x='Departamento', y='num cantidad capacidad instalada',
                                    size='num cantidad capacidad instalada', color='Departamento',
                                    title='Capacidad Instalada por Departamento',
                                    labels={'num cantidad capacidad instalada': 'Capacidad Instalada'})
            st.plotly_chart(fig_burbujas)
    
            
        except Exception as e:
            st.error(f"Error al generar el gráfico: {e}")
    if gráficos:
        graficar(filtered_df)
        
    if todo:
        estadisticas(filtered_df)
        v_nulos(filtered_df)
        graficar(filtered_df)
        
except Exception as e:
        st.error(f"Error al leer el archivo CSV: {e}")
        
