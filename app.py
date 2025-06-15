import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Short Put Screener", layout="wide")

st.title("📉 Short Put Screener Dashboard")
st.markdown("Visualiza, filtra y exporta contratos short put detectados por grupo o consolidados.")

storage_path = "storage"
if not os.path.exists(storage_path):
    st.error("No se encontró la carpeta 'storage/'. Asegúrate de ejecutar el screener primero.")
    st.stop()

# Buscar todos los archivos _resultados.csv
csv_files = [f for f in os.listdir(storage_path) if f.endswith("_resultados.csv")]
opciones = [f.replace("_resultados.csv", "") for f in csv_files]

# Agregar el consolidado si existe
consolidado_path = os.path.join(storage_path, "consolidado_validados.csv")
if os.path.exists(consolidado_path):
    opciones.insert(0, "📊 Consolidado general")

grupo_seleccionado = st.selectbox("Selecciona grupo o consolidado:", opciones)

# Cargar el archivo correspondiente
if grupo_seleccionado == "📊 Consolidado general":
    csv_path = consolidado_path
else:
    csv_path = os.path.join(storage_path, f"{grupo_seleccionado}_resultados.csv")

df = pd.read_csv(csv_path)

# Conversión segura de columnas esperadas
for col in ["rentabilidad_anual", "percent_diff", "days_to_expiration"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Filtros en barra lateral
st.sidebar.header("📊 Filtros")

ra_min = st.sidebar.slider("Rentabilidad Anual mínima (%)", 0, 200, 35)
margen_min = st.sidebar.slider("Margen de Seguridad mínimo (%)", 0, 50, 3)
dias_max = st.sidebar.slider("Días hasta vencimiento (máximo)", 1, 60, 30)

tickers_disponibles = sorted(df["ticker"].unique()) if "ticker" in df.columns else []
ticker_filtrado = st.sidebar.multiselect("Filtrar por Ticker(s):", tickers_disponibles, default=tickers_disponibles)

opciones_alerta = ["Mostrar todos", "Solo con alerta", "Solo excluidos"]
tipo_alerta = st.sidebar.selectbox("¿Mostrar contratos con alerta?", opciones_alerta)

# Aplicar filtros
df_filtrado = df[
    (df["rentabilidad_anual"] >= ra_min) &
    (df["percent_diff"] >= margen_min) &
    (df["days_to_expiration"] <= dias_max) &
    (df["ticker"].isin(ticker_filtrado))
]

if "alerta_excluida_por" in df.columns:
    if tipo_alerta == "Solo con alerta":
        df_filtrado = df_filtrado[df_filtrado["alerta_excluida_por"].isna() | (df_filtrado["alerta_excluida_por"] == "")]
    elif tipo_alerta == "Solo excluidos":
        df_filtrado = df_filtrado[df_filtrado["alerta_excluida_por"].notna() & (df_filtrado["alerta_excluida_por"] != "")]

# Orden interactivo
col_orden = st.selectbox("Ordenar por:", ["rentabilidad_anual", "percent_diff", "bid", "days_to_expiration"])
ascendente = st.checkbox("Orden ascendente", value=False)
df_filtrado = df_filtrado.sort_values(by=col_orden, ascending=ascendente)

st.write(f"Se encontraron {len(df_filtrado)} contratos que cumplen los filtros:")

st.dataframe(df_filtrado, use_container_width=True)

# Descargar resultados
def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

nombre_archivo = "consolidado_filtrado.csv" if grupo_seleccionado == "📊 Consolidado general" else f"{grupo_seleccionado}_filtrado.csv"

st.download_button(
    label="📥 Descargar resultados filtrados en CSV",
    data=convertir_csv(df_filtrado),
    file_name=nombre_archivo,
    mime='text/csv'
)
