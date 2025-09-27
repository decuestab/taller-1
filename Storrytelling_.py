# -*- coding: utf-8 -*-
"""
Created on Sat Sep 27 07:45:45 2025
@author: anama
"""

import streamlit as st
import pandas as pd
import altair as alt

# ======================
# 1. Configuración inicial
# ======================
st.set_page_config(page_title="📊 Storytelling de Ventas Meeiko S.A.", layout="wide")
st.title("📊 Storytelling de Ventas por País y Categoría")
st.markdown("Este dashboard analiza automáticamente las ventas y cantidades vendidas por país y categoría usando datos precargados en el repositorio.")

# ======================
# 2. Cargar y limpiar datos
# ======================
@st.cache_data
def load_data():
    path = r"C:\Users\anama\Downloads\superstore.csv"  # ruta local
    df = pd.read_csv(path, encoding="latin1", sep=";")
    
    # Asegurar que las columnas sean numéricas
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    return df

try:
    df = load_data()
    st.success("✅ Datos cargados correctamente desde el repositorio.")
except Exception as e:
    st.error(f"❌ Error al cargar el archivo desde el repositorio: {e}")
    st.stop()

# ======================
# 3. Validación de columnas esperadas
# ======================
required_cols = ["City", "Category", "Sales", "Quantity"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"❌ Faltan las siguientes columnas en el dataset: {missing}")
    st.stop()

# ======================
# 4. Filtros interactivos
# ======================
st.sidebar.header("🔍 Filtros")

cities = df["City"].dropna().unique().tolist()
selected_cities = st.sidebar.multiselect("Selecciona Ciudad(es)", cities, default=cities[:3])
df = df[df["City"].isin(selected_cities)]

categories = df["Category"].dropna().unique().tolist()
selected_categories = st.sidebar.multiselect("Selecciona Categoría(s)", categories, default=categories[:2])
df = df[df["Category"].isin(selected_categories)]

top_n = st.sidebar.slider("Top N registros por ventas", min_value=5, max_value=50, value=10)
df = df.sort_values(by="Sales", ascending=False).head(top_n)

# ======================
# 5. Paleta de colores
# ======================
color_scheme = st.sidebar.selectbox("🎨 Paleta de colores", ["category10", "tableau10", "dark2", "set1"])

# ======================
# 6. Storytelling visual
# ======================
st.subheader("📊 Ventas por Categoría")
bar_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("Category:N", sort="-y"),
    y=alt.Y("Sales:Q"),
    color=alt.Color("Category:N", scale=alt.Scale(scheme=color_scheme)),
    tooltip=["City", "Category", "Sales", "Quantity"]
).properties(width=700, height=400)

if not df.empty:
    max_row = df.loc[df["Sales"].idxmax()]
    anot_bar = alt.Chart(pd.DataFrame({
        "Category": [max_row["Category"]],
        "Sales": [max_row["Sales"]],
        "label": ["⬆ Mayor venta"]
    })).mark_text(dy=-10, color="red", fontWeight="bold").encode(
        x="Category:N", y="Sales:Q", text="label"
    )
    st.altair_chart(bar_chart + anot_bar, use_container_width=True)
else:
    st.warning("⚠️ No hay datos para graficar.")

# ======================
# 📈 Cantidad promedio por ciudad
# ======================
st.subheader("📈 Cantidad promedio por ciudad")

if df["Quantity"].notna().sum() == 0:
    st.warning("⚠️ No hay valores válidos en la columna 'Quantity' para graficar.")
else:
    quantity_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("City:N", title="Ciudad"),
        y=alt.Y("mean(Quantity):Q", title="Cantidad promedio"),
        color=alt.Color("City:N", scale=alt.Scale(scheme=color_scheme)),
        tooltip=["City", alt.Tooltip("mean(Quantity):Q", format=".0f")]
    ).properties(width=700, height=400)

    st.altair_chart(quantity_chart, use_container_width=True)

# ======================
# 🔀 Relación entre Ventas y Cantidad
# ======================
st.subheader("🔀 Relación entre Ventas y Cantidad")
scatter_chart = alt.Chart(df).mark_circle(size=80).encode(
    x=alt.X("Quantity:Q", scale=alt.Scale(zero=False)),
    y=alt.Y("Sales:Q", scale=alt.Scale(zero=False)),
    color=alt.Color("Category:N", scale=alt.Scale(scheme=color_scheme)),
    tooltip=["City", "Category", "Sales", "Quantity"]
).properties(width=700, height=400)

st.altair_chart(scatter_chart, use_container_width=True)

# ======================
# 7. Insights narrativos
# ======================
st.subheader("🧠 Insights clave")

if not df.empty:
    top_city = df.groupby("City")["Sales"].sum().idxmax()
    top_category = df.groupby("Category")["Sales"].sum().idxmax()
    max_quantity = df.loc[df["Quantity"].idxmax()]

    st.markdown(f"""
    - 🌍 La ciudad con mayores ventas es **{top_city}**.
    - 🏷️ La categoría más vendida es **{top_category}**.
    - 📦 La mayor cantidad registrada fue de **{max_quantity['Quantity']}** unidades en **{max_quantity['Category']}** ({max_quantity['City']}).
    """)
else:
    st.warning("⚠️ No hay suficientes datos para generar insights.")

# =======================================================================
# cd "C:\Users\anama\Downloads"
# streamlit run Storrytelling_.py
