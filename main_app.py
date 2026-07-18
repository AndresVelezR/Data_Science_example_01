"""
Dashboard Interactivo COVID-19 (datos sintéticos)
==================================================
Aplicación construida en Streamlit que:
1. Genera datos sintéticos de COVID-19 (10 registros x 8 columnas, tipos mixtos)
   directamente dentro de la plataforma, de forma interactiva.
2. Presenta un esquema de métricas: estadística cuantitativa, cualitativa
   y análisis gráfico.
3. Permite construir gráficas dinámicas con Plotly, eligiendo variables,
   tipo de gráfico, líneas de umbral y personalización visual.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard COVID-19 (Datos Sintéticos)",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAISES = [
    "Colombia", "México", "Argentina", "Chile", "Perú",
    "España", "Brasil", "Ecuador", "Uruguay", "Paraguay",
]

NIVELES_RIESGO = ["Bajo", "Medio", "Alto"]

COLUMNAS_NUMERICAS = [
    "Casos_Confirmados", "Casos_Recuperados", "Fallecidos", "Tasa_Positividad",
]
COLUMNAS_CATEGORICAS = ["Pais", "Nivel_Riesgo", "Cuarentena_Activa"]
COLUMNA_FECHA = "Fecha"


# ---------------------------------------------------------------------------
# 1. GENERACIÓN DE DATOS SINTÉTICOS (interactiva)
# ---------------------------------------------------------------------------
def generar_datos_sinteticos(n_registros: int, semilla: int) -> pd.DataFrame:
    """Simula un dataset de COVID-19 con 8 columnas de tipos de dato variados:
    texto, fecha, enteros, flotante, categórica y booleana.
    """
    rng = np.random.default_rng(semilla)

    paises = rng.choice(PAISES, size=n_registros, replace=True)

    fecha_hoy = pd.Timestamp.today().normalize()
    dias_atras = rng.integers(0, 90, size=n_registros)
    fechas = [fecha_hoy - pd.Timedelta(days=int(d)) for d in dias_atras]

    casos_confirmados = rng.integers(150, 5000, size=n_registros)

    # Recuperados: proporción realista respecto a confirmados (60% - 95%)
    prop_recuperados = rng.uniform(0.60, 0.95, size=n_registros)
    casos_recuperados = (casos_confirmados * prop_recuperados).astype(int)

    # Fallecidos: pequeña proporción de los confirmados (0% - 6%)
    prop_fallecidos = rng.uniform(0.0, 0.06, size=n_registros)
    fallecidos = (casos_confirmados * prop_fallecidos).astype(int)

    tasa_positividad = np.round(rng.uniform(1.0, 35.0, size=n_registros), 2)

    nivel_riesgo = rng.choice(NIVELES_RIESGO, size=n_registros, p=[0.5, 0.35, 0.15])

    cuarentena_activa = rng.choice([True, False], size=n_registros, p=[0.3, 0.7])

    df = pd.DataFrame({
        "Pais": paises,
        "Fecha": pd.to_datetime(fechas),
        "Casos_Confirmados": casos_confirmados.astype(int),
        "Casos_Recuperados": casos_recuperados.astype(int),
        "Fallecidos": fallecidos.astype(int),
        "Tasa_Positividad": tasa_positividad.astype(float),
        "Nivel_Riesgo": pd.Categorical(nivel_riesgo, categories=NIVELES_RIESGO, ordered=True),
        "Cuarentena_Activa": cuarentena_activa.astype(bool),
    })

    df = df.sort_values("Fecha").reset_index(drop=True)
    return df


# --- Estado de la sesión: permite regenerar datos sin perder configuración ---
if "semilla" not in st.session_state:
    st.session_state.semilla = 42
if "df" not in st.session_state:
    st.session_state.df = generar_datos_sinteticos(10, st.session_state.semilla)


# ---------------------------------------------------------------------------
# BARRA LATERAL: controles de simulación y personalización global
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Panel de Control")

st.sidebar.subheader("🧪 Simulación de datos")
n_registros = st.sidebar.slider("Número de registros", min_value=5, max_value=50, value=10, step=1)
semilla_input = st.sidebar.number_input("Semilla aleatoria", min_value=0, max_value=9999, value=st.session_state.semilla, step=1)

col_regen1, col_regen2 = st.sidebar.columns(2)
if col_regen1.button("🔄 Regenerar datos", use_container_width=True):
    st.session_state.semilla = semilla_input
    st.session_state.df = generar_datos_sinteticos(n_registros, st.session_state.semilla)
if col_regen2.button("🎲 Semilla aleatoria", use_container_width=True):
    nueva_semilla = int(np.random.default_rng().integers(0, 9999))
    st.session_state.semilla = nueva_semilla
    st.session_state.df = generar_datos_sinteticos(n_registros, nueva_semilla)

# Si el usuario cambia el slider sin dar clic, mantenemos coherencia de tamaño
if len(st.session_state.df) != n_registros:
    st.session_state.df = generar_datos_sinteticos(n_registros, st.session_state.semilla)

df = st.session_state.df

st.sidebar.subheader("🎨 Personalización visual")
tema_plotly = st.sidebar.selectbox(
    "Plantilla de gráficos",
    ["plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"],
    index=0,
)
paleta_color = st.sidebar.selectbox(
    "Paleta de colores",
    ["Plotly", "Viridis", "Bluered", "Sunset", "Tealrose", "Rainbow"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Los datos son 100% sintéticos y se generan en tiempo real dentro de "
    "la aplicación. No provienen de fuentes oficiales."
)


# ---------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL
# ---------------------------------------------------------------------------
st.title("🦠 Dashboard Interactivo COVID-19 — Datos Sintéticos")
st.markdown(
    "Este panel simula registros epidemiológicos para practicar análisis "
    "estadístico y visualización dinámica. Usa el **panel lateral** para "
    "regenerar los datos y personalizar los gráficos."
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Registros", len(df))
k2.metric("Confirmados totales", f"{df['Casos_Confirmados'].sum():,}")
k3.metric("Recuperados totales", f"{df['Casos_Recuperados'].sum():,}")
k4.metric("Fallecidos totales", f"{df['Fallecidos'].sum():,}")

st.markdown("---")

tab_datos, tab_cuanti, tab_cuali, tab_graficos = st.tabs([
    "📊 Datos Simulados",
    "🔢 Estadística Cuantitativa",
    "🏷️ Estadística Cualitativa",
    "📈 Análisis Gráfico Dinámico",
])


# ---------------------------------------------------------------------------
# TAB 1: DATOS SIMULADOS
# ---------------------------------------------------------------------------
with tab_datos:
    st.subheader("Vista del dataset sintético")
    st.dataframe(df, use_container_width=True)

    st.caption("**Tipos de dato por columna:**")
    tipos_df = pd.DataFrame({
        "Columna": df.columns,
        "Tipo de dato": [str(t) for t in df.dtypes],
    })
    st.dataframe(tipos_df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar CSV",
        data=csv,
        file_name="covid_datos_sinteticos.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# TAB 2: ESTADÍSTICA CUANTITATIVA
# ---------------------------------------------------------------------------
with tab_cuanti:
    st.subheader("Resumen estadístico de variables numéricas")

    resumen = []
    for col in COLUMNAS_NUMERICAS:
        serie = df[col]
        resumen.append({
            "Variable": col,
            "Media": round(serie.mean(), 2),
            "Mediana": round(serie.median(), 2),
            "Desv. Estándar": round(serie.std(), 2),
            "Varianza": round(serie.var(), 2),
            "Mínimo": serie.min(),
            "Q1 (25%)": round(serie.quantile(0.25), 2),
            "Q3 (75%)": round(serie.quantile(0.75), 2),
            "Máximo": serie.max(),
            "Rango": serie.max() - serie.min(),
            "Coef. Variación (%)": round((serie.std() / serie.mean()) * 100, 2) if serie.mean() != 0 else 0,
        })
    resumen_df = pd.DataFrame(resumen)
    st.dataframe(resumen_df, use_container_width=True, hide_index=True)

    st.markdown("##### Matriz de correlación (variables numéricas)")
    corr = df[COLUMNAS_NUMERICAS].corr(numeric_only=True)
    fig_corr = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale=paleta_color,
        template=tema_plotly,
        aspect="auto",
    )
    fig_corr.update_layout(height=450)
    st.plotly_chart(fig_corr, use_container_width=True)


# ---------------------------------------------------------------------------
# TAB 3: ESTADÍSTICA CUALITATIVA
# ---------------------------------------------------------------------------
with tab_cuali:
    st.subheader("Resumen de variables cualitativas / categóricas")

    for col in COLUMNAS_CATEGORICAS:
        st.markdown(f"**{col}**")
        conteo = df[col].value_counts(dropna=False).reset_index()
        conteo.columns = [col, "Frecuencia"]
        conteo["Proporción (%)"] = round(100 * conteo["Frecuencia"] / len(df), 2)
        moda = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"

        c1, c2 = st.columns([1, 1.3])
        with c1:
            st.dataframe(conteo, use_container_width=True, hide_index=True)
            st.caption(f"Moda: **{moda}**")
        with c2:
            fig_bar = px.bar(
                conteo, x=col, y="Frecuencia", color=col,
                template=tema_plotly, color_discrete_sequence=px.colors.qualitative.Set2,
                text="Frecuencia",
            )
            fig_bar.update_layout(showlegend=False, height=280, margin=dict(t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("---")


# ---------------------------------------------------------------------------
# TAB 4: ANÁLISIS GRÁFICO DINÁMICO (Plotly interactivo)
# ---------------------------------------------------------------------------
with tab_graficos:
    st.subheader("Constructor de gráficas dinámicas")

    tipo_grafico = st.selectbox(
        "Tipo de gráfico",
        ["Histograma", "Boxplot", "Dispersión (Scatter)", "Barras", "Líneas", "Violín"],
    )

    col_izq, col_der = st.columns([1, 2.2])

    with col_izq:
        st.markdown("##### Variables")

        if tipo_grafico in ["Dispersión (Scatter)", "Líneas"]:
            var_x = st.selectbox("Variable eje X", [COLUMNA_FECHA] + COLUMNAS_NUMERICAS + COLUMNAS_CATEGORICAS)
            var_y = st.selectbox("Variable eje Y", COLUMNAS_NUMERICAS)
        elif tipo_grafico == "Barras":
            var_x = st.selectbox("Variable categórica (X)", COLUMNAS_CATEGORICAS)
            var_y = st.selectbox("Variable numérica (Y)", COLUMNAS_NUMERICAS)
        else:  # Histograma, Boxplot, Violín
            var_y = st.selectbox("Variable numérica", COLUMNAS_NUMERICAS)
            var_x = None

        color_por = st.selectbox("Colorear por (opcional)", ["Ninguno"] + COLUMNAS_CATEGORICAS)
        color_por = None if color_por == "Ninguno" else color_por

        st.markdown("##### Umbral de referencia")
        activar_umbral = st.checkbox("Mostrar línea de umbral", value=False)
        if activar_umbral:
            var_umbral_ref = var_y if var_y else var_x
            valor_min = float(df[var_umbral_ref].min()) if var_umbral_ref in df.columns and pd.api.types.is_numeric_dtype(df[var_umbral_ref]) else 0.0
            valor_max = float(df[var_umbral_ref].max()) if var_umbral_ref in df.columns and pd.api.types.is_numeric_dtype(df[var_umbral_ref]) else 100.0
            valor_umbral = st.slider(
                "Valor del umbral",
                min_value=float(valor_min * 0.5),
                max_value=float(valor_max * 1.5) if valor_max > 0 else 100.0,
                value=float((valor_min + valor_max) / 2),
            )
            color_umbral = st.color_picker("Color del umbral", "#FF4B4B")
            etiqueta_umbral = st.text_input("Etiqueta del umbral", "Umbral crítico")

        st.markdown("##### Personalización")
        color_base = st.color_picker("Color principal (si no hay categoría)", "#636EFA")
        opacidad = st.slider("Opacidad", min_value=0.1, max_value=1.0, value=0.85)
        titulo_custom = st.text_input("Título del gráfico", f"{tipo_grafico} - {var_y if var_y else var_x}")

    with col_der:
        fig = None
        color_args = {"color": color_por} if color_por else {}
        color_seq = px.colors.qualitative.Set2 if color_por else None

        if tipo_grafico == "Histograma":
            fig = px.histogram(
                df, x=var_y, template=tema_plotly, opacity=opacidad,
                color_discrete_sequence=color_seq or [color_base], **color_args,
            )
        elif tipo_grafico == "Boxplot":
            fig = px.box(
                df, y=var_y, template=tema_plotly,
                color_discrete_sequence=color_seq or [color_base], points="all", **color_args,
            )
        elif tipo_grafico == "Violín":
            fig = px.violin(
                df, y=var_y, template=tema_plotly, box=True, points="all",
                color_discrete_sequence=color_seq or [color_base], **color_args,
            )
        elif tipo_grafico == "Dispersión (Scatter)":
            fig = px.scatter(
                df, x=var_x, y=var_y, template=tema_plotly, opacity=opacidad,
                size="Casos_Confirmados" if "Casos_Confirmados" not in (var_x, var_y) else None,
                color_discrete_sequence=color_seq or [color_base], **color_args,
            )
        elif tipo_grafico == "Líneas":
            df_ordenado = df.sort_values(var_x) if var_x == COLUMNA_FECHA else df
            fig = px.line(
                df_ordenado, x=var_x, y=var_y, template=tema_plotly, markers=True,
                color_discrete_sequence=color_seq or [color_base], **color_args,
            )
        elif tipo_grafico == "Barras":
            agregado = st.radio("Agregación", ["Suma", "Promedio"], horizontal=True)
            func_agg = "sum" if agregado == "Suma" else "mean"
            df_agg = df.groupby(var_x, observed=True)[var_y].agg(func_agg).reset_index()
            fig = px.bar(
                df_agg, x=var_x, y=var_y, template=tema_plotly, opacity=opacidad,
                color=var_x, color_discrete_sequence=color_seq or px.colors.qualitative.Set2,
            )

        if fig is not None:
            fig.update_layout(title=titulo_custom, height=520)

            if activar_umbral:
                eje_umbral = var_y if var_y and tipo_grafico != "Histograma" else None
                if tipo_grafico == "Histograma":
                    fig.add_vline(
                        x=valor_umbral, line_dash="dash", line_color=color_umbral, line_width=3,
                        annotation_text=etiqueta_umbral, annotation_position="top",
                    )
                else:
                    fig.add_hline(
                        y=valor_umbral, line_dash="dash", line_color=color_umbral, line_width=3,
                        annotation_text=etiqueta_umbral, annotation_position="top right",
                    )

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("##### Vista rápida multivariable")
    variables_multi = st.multiselect(
        "Selecciona variables numéricas para comparar (gráfico de líneas normalizado)",
        COLUMNAS_NUMERICAS, default=COLUMNAS_NUMERICAS[:2],
    )
    if variables_multi:
        df_norm = df[variables_multi].copy()
        df_norm = (df_norm - df_norm.min()) / (df_norm.max() - df_norm.min() + 1e-9)
        df_norm[COLUMNA_FECHA] = df[COLUMNA_FECHA].values
        df_norm_melt = df_norm.melt(id_vars=COLUMNA_FECHA, var_name="Variable", value_name="Valor normalizado")
        fig_multi = px.line(
            df_norm_melt, x=COLUMNA_FECHA, y="Valor normalizado", color="Variable",
            template=tema_plotly, markers=True, color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_multi.update_layout(height=400)
        st.plotly_chart(fig_multi, use_container_width=True)
    else:
        st.info("Selecciona al menos una variable para ver la comparación.")
