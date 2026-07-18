"""
Dashboard de Monitoreo Climático y de Riesgos
Medellín y Área Metropolitana del Valle de Aburrá (datos sintéticos)
=====================================================================
Herramienta de apoyo a la toma de decisiones para la Alcaldía: simula
variables meteorológicas y demográficas por comuna/municipio para
identificar zonas en riesgo de desastre (deslizamientos, inundaciones,
vendavales) y priorizar la respuesta.

Nota: todos los datos (clima, riesgo, coordenadas) son SINTÉTICOS y con
fines académicos/demostrativos. No provienen de IDEAM, SIATA ni de
ninguna fuente oficial.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Riesgos Climáticos - Medellín y AMVA",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# ACCESO CON CÓDIGO (control de operación del panel)
# ---------------------------------------------------------------------------
CODIGO_ACCESO = "4650"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Panel de Riesgos Climáticos — Acceso restringido")
    st.caption("EAFIT 2026 · Ciencia de Datos · Andrés")
    st.write(
        "Este panel simula variables meteorológicas para apoyar decisiones "
        "sobre riesgos y desastres en Medellín y su área metropolitana. "
        "Ingresa el código de operación para continuar."
    )
    with st.form("form_login"):
        codigo_ingresado = st.text_input("Código de acceso", type="password")
        enviar = st.form_submit_button("Ingresar", width="stretch")
    if enviar:
        if codigo_ingresado == CODIGO_ACCESO:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Código incorrecto. Verifica con el administrador del panel.")
    st.stop()

# ---------------------------------------------------------------------------
# CATÁLOGO DE ZONAS: 16 comunas + 5 corregimientos de Medellín
# + 9 municipios del Área Metropolitana del Valle de Aburrá (AMVA)
# Coordenadas y población son aproximadas, con fines ilustrativos.
# Tipo_Zona, Poblacion, Lat, Lon, Riesgo_Base(0-1), Temp_Base(°C), Humedad_Base(%)
# ---------------------------------------------------------------------------
CATALOGO_ZONAS = {
    "Popular":               ("Comuna", 129184, 6.2985, -75.5473, 0.80, 21.0, 78),
    "Santa Cruz":            ("Comuna", 106000, 6.2917, -75.5502, 0.75, 21.5, 77),
    "Manrique":              ("Comuna", 145000, 6.2789, -75.5477, 0.65, 22.0, 75),
    "Aranjuez":              ("Comuna", 160000, 6.2745, -75.5566, 0.55, 22.5, 74),
    "Castilla":              ("Comuna", 155000, 6.2933, -75.5697, 0.50, 22.5, 73),
    "Doce de Octubre":       ("Comuna", 194000, 6.2924, -75.5789, 0.70, 22.0, 76),
    "Robledo":               ("Comuna", 200000, 6.2788, -75.5854, 0.55, 21.5, 75),
    "Villa Hermosa":         ("Comuna", 130000, 6.2529, -75.5497, 0.70, 21.5, 77),
    "Buenos Aires":          ("Comuna", 135000, 6.2453, -75.5537, 0.60, 22.0, 74),
    "La Candelaria":         ("Comuna",  95000, 6.2486, -75.5658, 0.45, 23.0, 70),
    "Laureles-Estadio":      ("Comuna", 120000, 6.2447, -75.5896, 0.20, 23.5, 68),
    "La América":            ("Comuna",  96000, 6.2540, -75.5928, 0.35, 22.5, 72),
    "San Javier":            ("Comuna", 137000, 6.2571, -75.6142, 0.80, 21.0, 78),
    "El Poblado":            ("Comuna", 140000, 6.2088, -75.5679, 0.30, 23.0, 68),
    "Guayabal":              ("Comuna",  96000, 6.2244, -75.5836, 0.45, 23.0, 71),
    "Belén":                 ("Comuna", 194000, 6.2244, -75.6033, 0.40, 22.5, 72),
    "San Cristóbal":         ("Corregimiento", 60000, 6.2833, -75.6333, 0.50, 19.5, 80),
    "Altavista":             ("Corregimiento", 30000, 6.2333, -75.6167, 0.55, 20.0, 79),
    "San Antonio de Prado":  ("Corregimiento", 75000, 6.1917, -75.6444, 0.50, 19.0, 81),
    "Santa Elena":           ("Corregimiento", 20000, 6.2167, -75.5000, 0.40, 15.5, 85),
    "Palmitas":              ("Corregimiento",  6000, 6.3667, -75.6500, 0.45, 18.0, 82),
    "Bello":                 ("Municipio AMVA", 481000, 6.3373, -75.5581, 0.55, 23.0, 74),
    "Itagüí":                ("Municipio AMVA", 280000, 6.1719, -75.6122, 0.40, 23.5, 71),
    "Envigado":              ("Municipio AMVA", 230000, 6.1667, -75.5833, 0.30, 23.0, 70),
    "Sabaneta":              ("Municipio AMVA",  90000, 6.1500, -75.6167, 0.25, 23.5, 69),
    "La Estrella":           ("Municipio AMVA",  77000, 6.1500, -75.6431, 0.35, 23.0, 72),
    "Copacabana":            ("Municipio AMVA",  91000, 6.3486, -75.5097, 0.40, 24.0, 73),
    "Girardota":             ("Municipio AMVA",  57000, 6.3778, -75.4444, 0.35, 25.0, 71),
    "Barbosa":               ("Municipio AMVA",  54000, 6.4383, -75.3319, 0.40, 26.0, 70),
    "Caldas":                ("Municipio AMVA",  91000, 6.0917, -75.6347, 0.45, 22.0, 76),
}
CATALOGO_DF = pd.DataFrame.from_dict(
    CATALOGO_ZONAS, orient="index",
    columns=["Tipo_Zona", "Poblacion", "Lat", "Lon", "Riesgo_Base", "Temp_Base", "Humedad_Base"],
)

COLUMNAS_NUMERICAS = [
    "Temperatura_C", "Humedad_Relativa", "Velocidad_Viento_kmh",
    "Precipitacion_mm", "Poblacion",
]
COLUMNAS_CATEGORICAS = ["Zona", "Tipo_Zona", "Nivel_Riesgo", "Alerta_Activa"]
COLUMNA_FECHA = "Fecha"
NIVELES_RIESGO = ["Bajo", "Medio", "Alto", "Crítico"]
COLOR_RIESGO = {"Bajo": "#2ECC71", "Medio": "#F1C40F", "Alto": "#E67E22", "Crítico": "#E74C3C"}

# Nombres de escala CONTINUA válidos para px.imshow / px.colors (en minúscula).
# "Plotly" es una paleta cualitativa (para barras/dispersión), no una escala
# continua, por lo que se mapea a "plotly3", su equivalente continuo.
PALETAS_CONTINUAS = {
    "Plotly": "plotly3",
    "Viridis": "viridis",
    "Bluered": "bluered",
    "Sunset": "sunset",
    "Tealrose": "tealrose",
    "Rainbow": "rainbow",
}


# ---------------------------------------------------------------------------
# 1. GENERACIÓN DE DATOS SINTÉTICOS (interactiva) — 500 registros x 10 columnas
# ---------------------------------------------------------------------------
def generar_datos_sinteticos(n_registros: int, semilla: int) -> pd.DataFrame:
    """Simula variables meteorológicas y de riesgo por zona (comuna,
    corregimiento o municipio del AMVA). Devuelve exactamente 10 columnas
    con tipos de dato variados: texto, categórica, fecha, enteros,
    flotantes y booleano.
    """
    rng = np.random.default_rng(semilla)

    zonas_sel = rng.choice(CATALOGO_DF.index.values, size=n_registros, replace=True)
    base = CATALOGO_DF.loc[zonas_sel].reset_index().rename(columns={"index": "Zona"})

    # --- Fechas: últimos 90 días, con hora aleatoria -> permite serie de tiempo
    fecha_hoy = pd.Timestamp.today().normalize()
    dias_atras = rng.integers(0, 90, size=n_registros)
    horas = rng.integers(0, 24, size=n_registros)
    fechas = pd.to_datetime(fecha_hoy) - pd.to_timedelta(dias_atras, unit="D") + pd.to_timedelta(horas, unit="h")
    dia_del_anio = fechas.dayofyear.to_numpy()

    # --- Estacionalidad simplificada: dos "temporadas de lluvia" por año
    factor_lluvia = 1.0 + 0.7 * np.abs(np.sin(2 * np.pi * dia_del_anio / 183))

    precipitacion_mm = rng.exponential(scale=8 * factor_lluvia, size=n_registros)
    precipitacion_mm = np.round(np.clip(precipitacion_mm, 0, 120), 1)

    temp_noise = rng.normal(0, 1.8, size=n_registros)
    temperatura_c = base["Temp_Base"].to_numpy() + temp_noise - 0.03 * precipitacion_mm
    temperatura_c = np.round(np.clip(temperatura_c, 8, 34), 1)

    humedad_noise = rng.normal(0, 5, size=n_registros)
    humedad = base["Humedad_Base"].to_numpy() + humedad_noise + 0.25 * precipitacion_mm
    humedad = np.round(np.clip(humedad, 30, 100), 1)

    viento_base = rng.uniform(4, 22, size=n_registros)
    viento_tormenta = np.where(precipitacion_mm > 25, rng.uniform(5, 20, size=n_registros), 0)
    viento_kmh = np.round(np.clip(viento_base + viento_tormenta, 2, 70), 1)

    poblacion = base["Poblacion"].to_numpy().astype(int)

    def normalizar(x, lo, hi):
        return np.clip((x - lo) / (hi - lo), 0, 1)

    puntaje_riesgo = (
        0.40 * base["Riesgo_Base"].to_numpy(dtype=float)
        + 0.35 * normalizar(precipitacion_mm, 0, 100)
        + 0.15 * normalizar(viento_kmh, 0, 60)
        + 0.10 * normalizar(humedad, 30, 100)
    )
    nivel_riesgo = pd.cut(
        puntaje_riesgo, bins=[-0.01, 0.30, 0.55, 0.75, 1.01], labels=NIVELES_RIESGO,
    )

    alerta_activa = (
        (nivel_riesgo.isin(["Alto", "Crítico"]) & (rng.random(n_registros) < 0.75))
        | (precipitacion_mm > 45)
    )

    df = pd.DataFrame({
        "Zona": base["Zona"].to_numpy(),
        "Tipo_Zona": base["Tipo_Zona"].to_numpy(),
        "Fecha": fechas,
        "Temperatura_C": temperatura_c,
        "Humedad_Relativa": humedad,
        "Velocidad_Viento_kmh": viento_kmh,
        "Precipitacion_mm": precipitacion_mm,
        "Poblacion": poblacion,
        "Nivel_Riesgo": pd.Categorical(nivel_riesgo, categories=NIVELES_RIESGO, ordered=True),
        "Alerta_Activa": alerta_activa.astype(bool),
    })
    df = df.sort_values("Fecha").reset_index(drop=True)
    return df


# --- Estado de la sesión: permite regenerar datos sin perder configuración ---
if "semilla" not in st.session_state:
    st.session_state.semilla = 42
if "df" not in st.session_state:
    st.session_state.df = generar_datos_sinteticos(500, st.session_state.semilla)


# ---------------------------------------------------------------------------
# BARRA LATERAL: identidad, simulación, filtros y personalización
# ---------------------------------------------------------------------------
st.sidebar.markdown("## 🎓 EAFIT 2026")
st.sidebar.markdown("**Ciencia de Datos**")
st.sidebar.caption("Desarrollado por: Andrés")
st.sidebar.markdown("---")

if st.sidebar.button("🔓 Cerrar sesión", width="stretch"):
    st.session_state.autenticado = False
    st.rerun()

st.sidebar.subheader("🧪 Simulación de datos")
n_registros = st.sidebar.slider("Número de registros", min_value=100, max_value=2000, value=500, step=50)
semilla_input = st.sidebar.number_input("Semilla aleatoria", min_value=0, max_value=9999, value=st.session_state.semilla, step=1)

col_regen1, col_regen2 = st.sidebar.columns(2)
if col_regen1.button("🔄 Regenerar", width="stretch"):
    st.session_state.semilla = semilla_input
    st.session_state.df = generar_datos_sinteticos(n_registros, st.session_state.semilla)
if col_regen2.button("🎲 Aleatorio", width="stretch"):
    nueva_semilla = int(np.random.default_rng().integers(0, 9999))
    st.session_state.semilla = nueva_semilla
    st.session_state.df = generar_datos_sinteticos(n_registros, nueva_semilla)

if len(st.session_state.df) != n_registros:
    st.session_state.df = generar_datos_sinteticos(n_registros, st.session_state.semilla)

df_completo = st.session_state.df

st.sidebar.subheader("🔎 Filtros")
rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(df_completo["Fecha"].min().date(), df_completo["Fecha"].max().date()),
)
tipos_sel = st.sidebar.multiselect(
    "Tipo de zona", sorted(df_completo["Tipo_Zona"].unique()),
    default=sorted(df_completo["Tipo_Zona"].unique()),
)
zonas_sel = st.sidebar.multiselect(
    "Zonas específicas (opcional)", sorted(df_completo["Zona"].unique()), default=[],
)
riesgo_sel = st.sidebar.multiselect(
    "Nivel de riesgo", NIVELES_RIESGO, default=NIVELES_RIESGO,
)

df = df_completo.copy()
if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    ini, fin = rango_fechas
    df = df[(df["Fecha"].dt.date >= ini) & (df["Fecha"].dt.date <= fin)]
if tipos_sel:
    df = df[df["Tipo_Zona"].isin(tipos_sel)]
if zonas_sel:
    df = df[df["Zona"].isin(zonas_sel)]
if riesgo_sel:
    df = df[df["Nivel_Riesgo"].isin(riesgo_sel)]

if df.empty:
    st.sidebar.warning("Los filtros no arrojan registros. Ajusta la selección.")
    df = df_completo.copy()

st.sidebar.subheader("🎨 Personalización visual")
tema_plotly = st.sidebar.selectbox(
    "Plantilla de gráficos", ["plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"], index=0,
)
paleta_color = st.sidebar.selectbox("Paleta de colores", list(PALETAS_CONTINUAS.keys()), index=0)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Datos 100% sintéticos con fines académicos. No provienen de IDEAM, "
    "SIATA ni de ninguna fuente oficial."
)


# ---------------------------------------------------------------------------
# ENCABEZADO Y KPIs
# ---------------------------------------------------------------------------
st.title("🌦️ Riesgos Climáticos — Medellín y Área Metropolitana")
st.markdown(
    "Panel sintético para apoyar decisiones sobre **riesgos y desastres** "
    "(deslizamientos, inundaciones, vendavales) por comuna, corregimiento "
    "y municipio del Valle de Aburrá."
)

alertas_df = df[df["Alerta_Activa"]]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Zonas monitoreadas", df["Zona"].nunique())
k2.metric("Temp. promedio", f"{df['Temperatura_C'].mean():.1f} °C")
k3.metric("Precipitación media", f"{df['Precipitacion_mm'].mean():.1f} mm")
k4.metric("Alertas activas", int(df["Alerta_Activa"].sum()))
k5.metric("Población en alerta", f"{alertas_df['Poblacion'].sum():,}")

st.markdown("---")

tab_datos, tab_cuanti, tab_cuali, tab_series, tab_graficos, tab_riesgo = st.tabs([
    "📊 Datos Simulados",
    "🔢 Estadística Cuantitativa",
    "🏷️ Estadística Cualitativa",
    "⏱️ Series de Tiempo",
    "📈 Gráfico Dinámico",
    "🚨 Riesgo y Alertas",
])


# ---------------------------------------------------------------------------
# TAB 1: DATOS SIMULADOS
# ---------------------------------------------------------------------------
with tab_datos:
    st.subheader("Vista del dataset sintético")
    st.caption(f"{len(df)} registros tras aplicar filtros (de {len(df_completo)} generados en total).")
    st.dataframe(df, width="stretch")

    st.caption("**Tipos de dato por columna (10 columnas):**")
    tipos_df = pd.DataFrame({"Columna": df.columns, "Tipo de dato": [str(t) for t in df.dtypes]})
    st.dataframe(tipos_df, width="stretch", hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", data=csv, file_name="clima_riesgo_medellin.csv", mime="text/csv")


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
    st.dataframe(resumen_df, width="stretch", hide_index=True)

    st.markdown("##### Matriz de correlación (variables numéricas)")
    corr = df[COLUMNAS_NUMERICAS].corr(numeric_only=True)
    fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale=PALETAS_CONTINUAS[paleta_color],
        template=tema_plotly, aspect="auto",
    )
    fig_corr.update_layout(height=450)
    st.plotly_chart(fig_corr, width="stretch")
    st.caption(
        "Útil para identificar, por ejemplo, si la precipitación se asocia con "
        "mayor humedad o viento, insumo para priorizar variables de alerta temprana."
    )


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
            st.dataframe(conteo, width="stretch", hide_index=True)
            st.caption(f"Moda: **{moda}**")
        with c2:
            if col == "Nivel_Riesgo":
                fig_bar = px.bar(
                    conteo, x=col, y="Frecuencia", color=col, template=tema_plotly,
                    color_discrete_map=COLOR_RIESGO, text="Frecuencia",
                )
            else:
                fig_bar = px.bar(
                    conteo, x=col, y="Frecuencia", color=col, template=tema_plotly,
                    color_discrete_sequence=px.colors.qualitative.Set2, text="Frecuencia",
                )
            fig_bar.update_layout(showlegend=False, height=280, margin=dict(t=20, b=20))
            st.plotly_chart(fig_bar, width="stretch")
        st.markdown("---")


# ---------------------------------------------------------------------------
# TAB 4: SERIES DE TIEMPO
# ---------------------------------------------------------------------------
with tab_series:
    st.subheader("Tendencia general en el tiempo")
    variable_serie = st.selectbox("Variable a graficar", COLUMNAS_NUMERICAS, index=0, key="var_serie_general")

    df_diario = df.copy()
    df_diario["Dia"] = df_diario["Fecha"].dt.date
    serie_general = df_diario.groupby("Dia", as_index=False)[variable_serie].mean()
    fig_general = px.line(
        serie_general, x="Dia", y=variable_serie, template=tema_plotly, markers=True,
        color_discrete_sequence=[px.colors.qualitative.Set2[0]],
        title=f"Promedio diario de {variable_serie} — todas las zonas filtradas",
    )
    fig_general.update_layout(height=380)
    st.plotly_chart(fig_general, width="stretch")

    st.markdown("---")
    st.subheader("Comparativo entre zonas")
    zonas_disponibles = sorted(df["Zona"].unique())
    zonas_comparar = st.multiselect(
        "Selecciona hasta 6 zonas a comparar", zonas_disponibles,
        default=zonas_disponibles[:3] if len(zonas_disponibles) >= 3 else zonas_disponibles,
        max_selections=6,
    )
    variable_comparar = st.selectbox("Variable a comparar", COLUMNAS_NUMERICAS, index=0, key="var_serie_comparar")

    if zonas_comparar:
        df_zonas = df[df["Zona"].isin(zonas_comparar)].copy()
        df_zonas["Dia"] = df_zonas["Fecha"].dt.date
        serie_zonas = df_zonas.groupby(["Dia", "Zona"], as_index=False)[variable_comparar].mean()
        fig_comparar = px.line(
            serie_zonas, x="Dia", y=variable_comparar, color="Zona", template=tema_plotly, markers=True,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_comparar.update_layout(height=430)
        st.plotly_chart(fig_comparar, width="stretch")
    else:
        st.info("Selecciona al menos una zona para ver su serie de tiempo.")


# ---------------------------------------------------------------------------
# TAB 5: ANÁLISIS GRÁFICO DINÁMICO (Plotly interactivo)
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
            es_numerica = var_umbral_ref in df.columns and pd.api.types.is_numeric_dtype(df[var_umbral_ref])
            valor_min = float(df[var_umbral_ref].min()) if es_numerica else 0.0
            valor_max = float(df[var_umbral_ref].max()) if es_numerica else 100.0
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
        if color_por == "Nivel_Riesgo":
            color_seq_kwargs = {"color_discrete_map": COLOR_RIESGO}
        elif color_por:
            color_seq_kwargs = {"color_discrete_sequence": px.colors.qualitative.Set2}
        else:
            color_seq_kwargs = {"color_discrete_sequence": [color_base]}

        if tipo_grafico == "Histograma":
            fig = px.histogram(df, x=var_y, template=tema_plotly, opacity=opacidad, **color_args, **color_seq_kwargs)
        elif tipo_grafico == "Boxplot":
            fig = px.box(df, y=var_y, template=tema_plotly, points="all", **color_args, **color_seq_kwargs)
        elif tipo_grafico == "Violín":
            fig = px.violin(df, y=var_y, template=tema_plotly, box=True, points="all", **color_args, **color_seq_kwargs)
        elif tipo_grafico == "Dispersión (Scatter)":
            fig = px.scatter(
                df, x=var_x, y=var_y, template=tema_plotly, opacity=opacidad,
                size="Poblacion" if "Poblacion" not in (var_x, var_y) else None,
                **color_args, **color_seq_kwargs,
            )
        elif tipo_grafico == "Líneas":
            df_ordenado = df.sort_values(var_x) if var_x == COLUMNA_FECHA else df
            fig = px.line(df_ordenado, x=var_x, y=var_y, template=tema_plotly, markers=True, **color_args, **color_seq_kwargs)
        elif tipo_grafico == "Barras":
            agregado = st.radio("Agregación", ["Suma", "Promedio"], horizontal=True)
            func_agg = "sum" if agregado == "Suma" else "mean"
            df_agg = df.groupby(var_x, observed=True)[var_y].agg(func_agg).reset_index()
            if var_x == "Nivel_Riesgo":
                fig = px.bar(df_agg, x=var_x, y=var_y, template=tema_plotly, opacity=opacidad, color=var_x, color_discrete_map=COLOR_RIESGO)
            else:
                fig = px.bar(df_agg, x=var_x, y=var_y, template=tema_plotly, opacity=opacidad, color=var_x, color_discrete_sequence=px.colors.qualitative.Set2)

        if fig is not None:
            fig.update_layout(title=titulo_custom, height=520)

            if activar_umbral:
                if tipo_grafico == "Histograma":
                    fig.add_vline(x=valor_umbral, line_dash="dash", line_color=color_umbral, line_width=3, annotation_text=etiqueta_umbral, annotation_position="top")
                else:
                    fig.add_hline(y=valor_umbral, line_dash="dash", line_color=color_umbral, line_width=3, annotation_text=etiqueta_umbral, annotation_position="top right")

            st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    st.markdown("##### Vista rápida multivariable (normalizada)")
    variables_multi = st.multiselect(
        "Selecciona variables numéricas para comparar en el tiempo",
        COLUMNAS_NUMERICAS, default=["Temperatura_C", "Precipitacion_mm"],
    )
    if variables_multi:
        df_norm = df[variables_multi + [COLUMNA_FECHA]].copy()
        df_norm["Dia"] = df_norm[COLUMNA_FECHA].dt.date
        df_norm_diario = df_norm.groupby("Dia", as_index=False)[variables_multi].mean()
        for col in variables_multi:
            rango = df_norm_diario[col].max() - df_norm_diario[col].min()
            df_norm_diario[col] = (df_norm_diario[col] - df_norm_diario[col].min()) / (rango + 1e-9)
        df_norm_melt = df_norm_diario.melt(id_vars="Dia", var_name="Variable", value_name="Valor normalizado")
        fig_multi = px.line(
            df_norm_melt, x="Dia", y="Valor normalizado", color="Variable", template=tema_plotly,
            markers=True, color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_multi.update_layout(height=400)
        st.plotly_chart(fig_multi, width="stretch")
    else:
        st.info("Selecciona al menos una variable para ver la comparación.")


# ---------------------------------------------------------------------------
# TAB 6: RIESGO Y ALERTAS
# ---------------------------------------------------------------------------
with tab_riesgo:
    st.subheader("Zonas más críticas")

    ranking = (
        df.groupby("Zona", as_index=False)
        .agg(
            Poblacion=("Poblacion", "first"),
            Tipo_Zona=("Tipo_Zona", "first"),
            Precipitacion_media=("Precipitacion_mm", "mean"),
            Pct_Alerta=("Alerta_Activa", "mean"),
            Registros_Alto_Critico=("Nivel_Riesgo", lambda s: s.isin(["Alto", "Crítico"]).sum()),
        )
    )
    ranking["Pct_Alerta"] = round(ranking["Pct_Alerta"] * 100, 1)
    ranking["Precipitacion_media"] = round(ranking["Precipitacion_media"], 1)
    ranking = ranking.sort_values(["Registros_Alto_Critico", "Pct_Alerta"], ascending=False).reset_index(drop=True)

    st.dataframe(
        ranking.rename(columns={
            "Pct_Alerta": "% Registros en alerta",
            "Precipitacion_media": "Precipitación media (mm)",
            "Registros_Alto_Critico": "Registros riesgo Alto/Crítico",
        }).head(10),
        width="stretch", hide_index=True,
    )

    csv_alertas = alertas_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar reporte ejecutivo de zonas en alerta",
        data=csv_alertas, file_name="reporte_alertas_medellin.csv", mime="text/csv",
    )

    st.markdown("---")
    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.markdown("##### Distribución de nivel de riesgo")
        conteo_riesgo = df["Nivel_Riesgo"].value_counts().reindex(NIVELES_RIESGO).reset_index()
        conteo_riesgo.columns = ["Nivel_Riesgo", "Registros"]
        fig_riesgo = px.bar(
            conteo_riesgo, x="Nivel_Riesgo", y="Registros", color="Nivel_Riesgo",
            color_discrete_map=COLOR_RIESGO, template=tema_plotly, text="Registros",
        )
        fig_riesgo.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_riesgo, width="stretch")
    with c2:
        st.markdown("##### Mapa de riesgo por zona")
        st.caption("Coordenadas aproximadas con fines ilustrativos, no georreferenciación oficial.")
        df_mapa = (
            df.sort_values("Fecha")
            .groupby("Zona", as_index=False)
            .last()[["Zona", "Nivel_Riesgo", "Poblacion", "Precipitacion_mm"]]
            .merge(CATALOGO_DF[["Lat", "Lon"]], left_on="Zona", right_index=True)
        )
        fig_mapa = px.scatter_map(
            df_mapa, lat="Lat", lon="Lon", color="Nivel_Riesgo", size="Poblacion",
            hover_name="Zona", color_discrete_map=COLOR_RIESGO, zoom=9.3,
            center={"lat": 6.24, "lon": -75.58}, height=420,
            hover_data={"Precipitacion_mm": True, "Lat": False, "Lon": False},
        )
        fig_mapa.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_mapa, width="stretch")
