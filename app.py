import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Short Put Screener", layout="wide")

st.title("📉 Short Put Screener Dashboard")
st.markdown("Visualiza y filtra contratos por grupo, rentabilidad, margen, etc.")

storage_path = "storage"
if not os.path.exists(storage_path):
    st.error("No se encontró la carpeta 'storage/'. Asegúrate de ejecutar el screener primero.")
    st.stop()

# Buscar todos los archivos _resultados.csv
csv_files = [f for f in os.listdir(storage_path) if f.endswith("_resultados.csv")]
if not csv_files:
    st.warning("No hay archivos de resultados disponibles.")
    st.stop()

# Selección de grupo
grupos = [f.replace("_resultados.csv", "") for f in csv_files]
grupo_seleccionado = st.selectbox("Selecciona grupo:", grupos)

# Cargar datos del grupo seleccionado
csv_path = os.path.join(storage_path, f"{grupo_seleccionado}_resultados.csv")
df = pd.read_csv(csv_path)

# Filtros
st.sidebar.header("📊 Filtros")
ra_min = st.sidebar.slider("Rentabilidad Anual mínima (%)", 0, 200, 30)
margen_min = st.sidebar.slider("Margen de Seguridad mínimo (%)", 0, 50, 3)
dias_max = st.sidebar.slider("Días hasta vencimiento (máximo)", 1, 60, 30)

df_filtrado = df[
    (df["rentabilidad_anual"] >= ra_min) &
    (df["percent_diff"] >= margen_min) &
    (df["days_to_expiration"] <= dias_max)
]

st.write(f"Se encontraron {len(df_filtrado)} contratos que cumplen los filtros:")

st.dataframe(df_filtrado, use_container_width=True)
