import streamlit as st
import pandas as pd
import html

# ─── CONFIGURACIÓN ───────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente de Estados — Poder Judicial",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS PERSONALIZADO ───────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fc;
        border-right: 1px solid #e0e5f0;
    }
    [data-testid="stSidebar"] .stButton button {
        text-align: left;
        background: transparent;
        border: none;
        border-radius: 6px;
        color: #1a2d50;
        font-size: 13px;
        padding: 6px 10px;
        margin-bottom: 2px;
        white-space: normal;
        height: auto;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #e8edf7;
        color: #1C3A6E;
    }
    /* Texto del speech */
    .speech-box {
        background-color: #f0f4fb;
        border: 1px solid #bdd0f0;
        border-radius: 10px;
        padding: 20px 24px;
        font-family: Georgia, serif;
        font-size: 15px;
        line-height: 1.8;
        color: #0f1923;
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-wrap: break-word;
        margin-bottom: 8px;
    }
    /* text_area para copiar */
    .stTextArea textarea {
        font-family: Georgia, serif !important;
        font-size: 14px !important;
        line-height: 1.7 !important;
        color: #0f1923 !important;
        background-color: #f0f4fb !important;
        border: 1px solid #bdd0f0 !important;
        border-radius: 10px !important;
        resize: none !important;
    }
    .speech-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #2B5CB8;
        margin-bottom: 8px;
    }
    .def-box {
        background-color: #f4f5f8;
        border-left: 3px solid #2B5CB8;
        padding: 10px 16px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: #4a5568;
        font-style: italic;
        margin-bottom: 16px;
    }
    .grupo-header {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #8a96a8;
        margin: 12px 0 4px 2px;
    }
</style>
""", unsafe_allow_html=True)


# ─── CARGA DE DATOS ──────────────────────────────────────────────
@st.cache_data(ttl=30)  # recarga automática cada 30 seg si el Excel cambió
def cargar_datos():
    df = pd.read_excel("estados.xlsx", dtype=str)
    df = df.fillna("")
    return df


df = cargar_datos()


# ─── SESSION STATE ───────────────────────────────────────────────
if "estado_seleccionado" not in st.session_state:
    st.session_state.estado_seleccionado = None


# ─── SIDEBAR ─────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://mcbesteiro.com.ar/images/sitio/logo.png", use_container_width=True)
    st.markdown("#### Asistente de Estados")
    st.caption("MCBesteiro Abogadas y Abogados")
    st.divider()

    busqueda = st.text_input("🔍 Buscar estado", placeholder="Escribí para filtrar...")

    # Estados únicos (de-duplicados)
    estados_unicos = df.drop_duplicates(subset=["grupo", "nombre"])[
        ["grupo", "codigo", "nombre"]
    ].copy()

    if busqueda:
        mask = (
            estados_unicos["nombre"].str.contains(busqueda, case=False, na=False)
            | estados_unicos["codigo"].str.contains(busqueda, case=False, na=False)
        )
        estados_unicos = estados_unicos[mask]

    # Orden de grupos definido manualmente
    orden_grupos = [
        "Pre-judicial",
        "Primera Instancia",
        "Cámara",
        "Corte Suprema",
        "Sin mensaje definido",
    ]

    for grupo in orden_grupos:
        grupo_df = estados_unicos[estados_unicos["grupo"] == grupo]
        if grupo_df.empty:
            continue

        st.markdown(f'<div class="grupo-header">{grupo}</div>', unsafe_allow_html=True)

        for _, fila in grupo_df.iterrows():
            tiene_speech = df[
                (df["nombre"] == fila["nombre"]) & (df["speech"] != "")
            ].shape[0] > 0

            icono = "🔵" if tiene_speech else "⚪"
            etiqueta = f"{icono} {fila['codigo']} — {fila['nombre']}"

            if st.button(
                etiqueta,
                key=f"btn_{fila['grupo']}_{fila['nombre']}",
                use_container_width=True,
            ):
                st.session_state.estado_seleccionado = fila["nombre"]


# ─── PANEL PRINCIPAL ─────────────────────────────────────────────
if st.session_state.estado_seleccionado is None:
    st.image("https://mcbesteiro.com.ar/images/sitio/logo.png", width=280)
    st.markdown("## Asistente de Estados — Poder Judicial")
    st.markdown("*MCBesteiro Abogadas y Abogados*")
    st.info("👈 Seleccioná un estado del expediente en el panel izquierdo para ver el mensaje al cliente.")

else:
    nombre = st.session_state.estado_seleccionado
    filas_estado = df[df["nombre"] == nombre]
    primera_fila = filas_estado.iloc[0]

    # Título
    st.markdown(f"## {primera_fila['codigo']} — {nombre}")
    st.markdown(f"*Grupo: {primera_fila['grupo']}*")

    # Definición interna
    if primera_fila["definicion"]:
        st.markdown(
            f'<div class="def-box">📌 <strong>Definición interna:</strong> {primera_fila["definicion"]}</div>',
            unsafe_allow_html=True,
        )

    # Advertencia
    if primera_fila["advertencia"]:
        st.warning(f"⚠️ {primera_fila['advertencia']}")

    st.divider()

    # Speeches
    speeches = filas_estado[filas_estado["speech"] != ""]

    if speeches.empty:
        st.info("📭 Este estado no tiene un mensaje definido para el cliente. Consultá internamente antes de comunicar.")
    else:
        st.markdown("#### 💬 Mensaje al cliente")
        st.caption("Seleccioná todo el texto del cuadro (Ctrl+A) y copiá (Ctrl+C).")

        for i, (_, fila) in enumerate(speeches.iterrows()):
            if fila["opcion_label"]:
                st.markdown(
                    f'<div class="speech-label">{fila["opcion_label"]}</div>',
                    unsafe_allow_html=True,
                )

            # Calcular altura del text_area según cantidad de líneas
            lineas = fila["speech"].count("\n") + 1
            altura = max(120, min(lineas * 32 + 40, 400))

            st.text_area(
                label="",
                value=fila["speech"],
                height=altura,
                key=f"ta_{i}_{nombre}",
                label_visibility="collapsed",
            )

            st.markdown("---") if i < len(speeches) - 1 else None

    # Botón para volver
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Volver a seleccionar"):
        st.session_state.estado_seleccionado = None
        st.rerun()
