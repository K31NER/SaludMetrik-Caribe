#Finalizado
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Configuración general de la página
st.set_page_config(
    page_icon="https://cdn-icons-png.flaticon.com/128/883/883337.png",
    page_title="SaludMetrik",
    layout="wide"
)

st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        background-color: #072550;
        color: white;
        border-radius: 5px;
        border: none;
    }
        [data-testid="stSidebar"] {
        background-image: url("https://i.ibb.co/MDPGycp/Sin-t-tulo-2160-x-3840-px.png");
        background-size: cover;
    }
            

    </style>
    """, unsafe_allow_html=True)

departamentos = [ "Bolívar", "Cartagena", "Sucre", "San Andrés y Providencia", "Córdoba"]
# Título
st.title(':blue[SaludMetrik]-Caribe')

st.subheader("Poblacion aproximada de cada departamento ", divider="violet")
st.text("Datos verificados por el DANE")
d1,d2,d3,d4,d5 = st.columns(5)

with d1:
    st.metric(":green[Bolivar]", f"{2206000:,}")
with d2:
    st.metric(":green[Cartagena]", f"{1059626:,}")
with d3:
    st.metric(":green[Sucre]", f"{1006044:,}")
with d4:
    st.metric(":green[San Andrés y Providencia]", f"{56309:,}")
with d5:
    st.metric(":green[Córdoba]", f"{1914778:,}")

# Cargar archivo CSV
st.sidebar.image("logo.png")
st.sidebar.header('Opciones avanzadas', divider="violet")
st.logo("icon.png")
file = "data.csv"
try:
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Filtrar por los departamentos definidos
    filtered_df = df[df['Departamento'].isin(departamentos)].reset_index(drop=True)
    
    
    # Opciones en la barra lateral
    st.sidebar.subheader("Estadísticas",divider="green")
    estadística = st.sidebar.button("Generar estadísticas")
    
    st.sidebar.subheader("Graficar",divider="green")
    gráficos = st.sidebar.button("Generar gráficos")
    
    st.sidebar.subheader("Todo",divider="green")
    todo = st.sidebar.button("Generar todo")
    
    st.sidebar.subheader("Referencias",divider="green")
    st.sidebar.markdown("[📑Donde sacamos los datos](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Relaci-n-de-IPS-p-blicas-y-privadas-seg-n-el-nivel/s2ru-bqt6/about_data)")
    st.sidebar.markdown("[👤Datos sobre la poblacion](https://www.dane.gov.co)")

    # Columnas numéricas
    numerical_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        # Mostrar datos filtrados
    st.subheader(f'Datos filtrados por departamentos del caribe',divider="violet")
    
    # Reemplazar valores NaN en la columna "num nivel atencion"
    filtered_df['num nivel atencion'] = filtered_df['num nivel atencion'].fillna(1)
    
    #dataframe filtrado
    st.dataframe(filtered_df)
    #funciones 
    def estadisticas(filtered_df):
        st.subheader("Estadisticas",divider="violet")
        st.dataframe(filtered_df.describe(),use_container_width=True)
        
    if estadística:
        estadisticas(filtered_df)
    
    # ------- datos agrupados ------------- #
        
    st.header("Datos agrupados",divider="violet")
        
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
    st.success("Si desea ver mas informacion puede generar todo el la parte de la barra lateral")
    # --------------- Graficas ---------------- #
    def  graficar(filtered_df):
        st.subheader("Graficas",divider="violet")
        try:
            c1,c2,c3 = st.columns(3)
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
    
                fig_radar = px.line_polar(prom_departamento, 
                            r='num nivel atencion', 
                            theta='Departamento', 
                            line_close=True, 
                            title='Nivel de Atención Promedio por Departamento',
                            labels={'num nivel atencion': 'Promedio Nivel Atención'},
                            color_discrete_sequence=['#636EFA'])  # Color más contrastante
    
                # Mejoras estéticas
                fig_radar.update_traces(fill='toself', marker=dict(size=8))  # Agregar relleno y hacer los puntos más grandes
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, prom_departamento['num nivel atencion'].max()])))  # Ajustar rango de ejes
    
                st.plotly_chart(fig_radar)

            with c3:
                fig_naturaleza = px.bar(tabla_naturaleza, x='Departamento', y=['Públicas', 'Privadas'],
                        title='Distribución de Sedes Públicas y Privadas por Departamento', 
                        labels={'value': 'Número de Sedes'},
                        barmode='group')  # Cambiar a 'group' para barras agrupadas
                st.plotly_chart(fig_naturaleza)

            # Gráfico de box plot: Distribución de la capacidad instalada por departamento
            fig_box = px.box(
                filtered_df, 
                x='Departamento', 
                y='num cantidad capacidad instalada',
                title='Distribución de la Capacidad Instalada por Departamento',
                labels={'num cantidad capacidad instalada': 'Capacidad Instalada'},
                hover_data=['nom sede IPS','naturaleza']  # Aquí pasas el nombre de la columna que se mostrara al pasar el cursor, Hover muestra informacion adicional
                )
            #El parametro hover_data nos permite mostrar informacion de otras columnas tantas como queramos sin saturar la grafica
            
            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig_box)
            

            
            st.subheader("Regresion lineal de poblacion-capacidad",divider="violet")
            poblacion = {
            "Bolívar": 2206000,
            "Cartagena": 1059626,
            "Sucre": 1006044,
            "San Andrés y Providencia": 56309,
            "Córdoba": 1914778
            }
            #agregar funcionalidad 
            #porcentaje = st.number_input("digite porcentaje a usar para la poblacion", min_value=5,max_value=50)
            #porcentaje_analisis = porcentaje/100
            
            # Multiplicamos por 0.05 para obtener el 5% de la población
            poblacion_5pct = {k: v * 0.05 for k, v in poblacion.items()}
            # Agregamos la población del 5% al dataframe
            capacidad_departamento['Poblacion 5%'] = capacidad_departamento['Departamento'].map(poblacion_5pct)

            # Modelo de regresión lineal
            X = capacidad_departamento[['Poblacion 5%']]  # Variable independiente
            y = capacidad_departamento['num cantidad capacidad instalada']  # Variable dependiente

            # Ajuste del modelo
            modelo = LinearRegression()
            modelo.fit(X, y)

            # Predicciones
            capacidad_departamento['Prediccion Capacidad'] = modelo.predict(X)

            # Mostrar los resultados
            st.write("Resultados del modelo de regresión lineal")
            st.dataframe(capacidad_departamento,use_container_width=True)
            
            # Cálculo de R^2
            #r2 = modelo.score(X, y)
            #st.write(f"El coeficiente de determinación (R²) del modelo es: {r2:.4f}")
            
            # Visualización de la regresión
            fig = px.scatter(capacidad_departamento, x='Poblacion 5%', y='num cantidad capacidad instalada', 
                    title='Regresión Lineal: Capacidad vs. Población (5%)', 
                    labels={'Poblacion 5%': 'Población (5%)', 'num cantidad capacidad instalada': 'Capacidad Instalada'}, hover_data=["Departamento"])

            # Añadir la línea de regresión
            fig.add_traces(px.line(capacidad_departamento, x='Poblacion 5%', y='Prediccion Capacidad').data)

            st.plotly_chart(fig)
            



        except Exception as e:
            st.error(f"Error al generar el gráfico: {e}")
    if gráficos:
        graficar(filtered_df)
        
    if todo:
        estadisticas(filtered_df)
        graficar(filtered_df)
        
except Exception as e:
        st.error(f"Error al leer el archivo CSV: {e}")