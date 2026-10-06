import streamlit as st
import pandas as pd
from datetime import datetime
import io
from collections import Counter
import re

# Configuración de la página
st.set_page_config(page_title="Validador de Cargas AP", layout="wide")

# Fondo de pantalla y estilos de colores/traducción
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/emilianopauli1985-bit/validador-ap/main/L2_Wallpaper-05.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .stAlert, [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
        padding: 10px;
    }

    label[data-testid="stWidgetLabel"] p, .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.6);
    }

    [data-testid="stFileUploadDropzone"] button {
        color: transparent !important;
    }
    [data-testid="stFileUploadDropzone"] button::after {
        content: "Subir archivo";
        color: #262730;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        font-weight: 500;
    }
    
    [data-testid="stFileUploadDropzone"] small {
        color: transparent !important;
    }
    [data-testid="stFileUploadDropzone"] small::after {
        content: "Límite 200MB • Excel/CSV";
        color: rgba(49, 51, 63, 0.6);
        display: block;
        margin-top: -15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 style="color: white; text-shadow: 2px 2px 5px rgba(0,0,0,0.6);">Validador y Armador de Solicitudes AP</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: white; font-size: 18px; text-shadow: 1px 1px 4px rgba(0,0,0,0.6);">Seleccioná la herramienta que necesites usar hoy.</p>', unsafe_allow_html=True)

# Creamos las dos pestañas
tab_armador, tab_validador = st.tabs(["🪄 Armar Excel (Limpiador)", "✅ Validar Carga"])

# ==========================================
# PESTAÑA 1: ARMADOR / LIMPIADOR DE DATOS CRUDOS
# ==========================================
with tab_armador:
    st.markdown('<div style="background-color: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 10px; margin-bottom: 20px;">Subí el Excel desordenado que te envió la empresa. Podés indicarle al sistema en qué fila empiezan los títulos para saltear logos o membretes.</div>', unsafe_allow_html=True)
    
    col_fila, col_espacio = st.columns([2, 3])
    with col_fila:
        fila_titulos = st.number_input("¿En qué fila del Excel están los títulos de las columnas? (Cambiá este número si hay títulos o logos arriba)", min_value=1, value=1)
    
    col1a, col2a = st.columns([2, 3])
    with col1a:
        archivo_crudo = st.file_uploader("Subí el Excel crudo del cliente", type=["xlsx", "xls", "csv"], key="uploader_armador")
    
    if archivo_crudo is not None:
        try:
            filas_a_saltar = int(fila_titulos) - 1
            if archivo_crudo.name.endswith('.csv'):
                df_crudo = pd.read_csv(archivo_crudo, skiprows=filas_a_saltar)
            else:
                df_crudo = pd.read_excel(archivo_crudo, skiprows=filas_a_saltar)
            
            df_crudo = df_crudo.dropna(how='all')
                
            columnas_disponibles = ["No incluir"] + list(df_crudo.columns)
            
            st.markdown('<div style="background-color: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
            st.write("### 📌 Mapeo de Columnas")
            st.write("Indicá en qué columna del Excel del cliente se encuentra cada dato:")
            
            col_map1, col_map2, col_map3 = st.columns(3)
            with col_map1:
                col_dni = st.selectbox("Columna de DNI:", options=columnas_disponibles)
            with col_map2:
                col_nombre = st.selectbox("Columna de Nombre y Apellido:", options=columnas_disponibles)
            with col_map3:
                col_fecha = st.selectbox("Columna de Fecha de Nacimiento:", options=columnas_disponibles)
                
            if st.button("Procesar y Generar Plantilla Oficial"):
                columnas_oficiales = ['MF', '*Tipo Id.', '*Nro. Id.', '*Fecha de Nacimiento', '*Apellido', '*Nombre', '*S.A. Individual Muerte', 'S.A. Individual Inválidez', 'S.A. AMF', '*Incapacidad', '*Ocupación', '*Nacionalidad']
                df_oficial = pd.DataFrame(columns=columnas_oficiales)
                
                if col_dni != "No incluir":
                    df_oficial['*Nro. Id.'] = df_crudo[col_dni].apply(lambda x: re.sub(r'[^0-9]', '', str(x)) if str(x).lower() != 'nan' and pd.notna(x) else '')
                
                if col_nombre != "No incluir":
                    apellidos = []
                    nombres = []
                    for nombre_completo in df_crudo[col_nombre]:
                        texto = str(nombre_completo).strip()
                        if texto.lower() == 'nan' or pd.isna(nombre_completo):
                            apellidos.append("")
                            nombres.append("")
                        elif "," in texto:
                            partes = texto.split(",", 1)
                            apellidos.append(partes[0].strip().upper())
                            nombres.append(partes[1].strip().upper())
                        else:
                            partes = texto.split(" ", 1)
                            if len(partes) > 1:
                                apellidos.append(partes[0].strip().upper())
                                nombres.append(partes[1].strip().upper())
                            else:
                                apellidos.append(texto.upper())
                                nombres.append("")
                    df_oficial['*Apellido'] = apellidos
                    df_oficial['*Nombre'] = nombres
                
                if col_fecha != "No incluir":
                    fechas_limpias = []
                    for f in df_crudo[col_fecha]:
                        if pd.isna(f) or str(f).lower() == 'nan':
                            fechas_limpias.append("")
                        elif isinstance(f, (pd.Timestamp, datetime)):
                            fechas_limpias.append(f.date())
                        else:
                            f_str = str(f)
                            nums = re.sub(r'[^0-9]', '', f_str)
                            if len(nums) == 8:
                                try: fechas_limpias.append(pd.to_datetime(nums, format='%d%m%Y').date())
                                except: fechas_limpias.append(f_str)
                            else:
                                fechas_limpias.append(f_str)
                    df_oficial['*Fecha de Nacimiento'] = fechas_limpias

                df_oficial['*Tipo Id.'] = 'D.N.I.'
                df_oficial['*Nacionalidad'] = 'ARGENTINA'
                df_oficial['*Incapacidad'] = 'NO'
                
                st.success("✅ Plantilla generada exitosamente. Se limpiaron los datos y se aplicaron los valores por defecto.")
                st.dataframe(df_oficial)
                
                buffer_armado = io.BytesIO()
                
                # --- AQUÍ APLICAMOS EL FORMATO DD/MM/YYYY PARA EL ARMADOR ---
                with pd.ExcelWriter(buffer_armado, engine='xlsxwriter', datetime_format='dd/mm/yyyy', date_format='dd/mm/yyyy') as writer:
                    df_oficial.to_excel(writer, index=False, sheet_name="AP - Personas x Grupo")
                
                st.download_button(
                    label="📥 Descargar Plantilla Oficial Pre-armada",
                    data=buffer_armado.getvalue(),
                    file_name="AP_Personas_Prearmado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}. Verificá que la fila de inicio sea la correcta.")

# ==========================================
# PESTAÑA 2: VALIDADOR ESTRICTO (Código Original)
# ==========================================
with tab_validador:
    col1b, col2b = st.columns([2, 3])
    with col1b:
        archivo_agente = st.file_uploader("Seleccioná el archivo Excel listo (.xlsx)", type=["xlsx"], key="uploader_validador")

    if archivo_agente is not None:
        try:
            df = pd.read_excel(archivo_agente, sheet_name="AP - Personas x Grupo")
            st.info("Procesando validaciones y corrigiendo formatos...")

            hoy = pd.Timestamp.today()
            total_fechas_mal_formato = 0
            total_fechas_corregidas = 0
            
            errores_col = {
                'Err_TipoId': [''] * len(df), 'Err_NroId': [''] * len(df), 'Err_FechaNac': [''] * len(df),
                'Err_SAMuerte': [''] * len(df), 'Err_SAInvalidez': [''] * len(df), 'Err_SAAMF': [''] * len(df),
                'Err_Incapacidad': [''] * len(df), 'Err_Ocupacion': [''] * len(df), 'Err_Nacionalidad': [''] * len(df)
            }

            for index, row in df.iterrows():
                tipo_id = str(row.get('*Tipo Id.', '')).strip().upper()
                if pd.isna(row.get('*Tipo Id.')) or tipo_id == 'NAN' or not tipo_id:
                    errores_col['Err_TipoId'][index] = "Falta seleccionar D.N.I. o Pasaporte"
                
                nro_id = row.get('*Nro. Id.')
                nro_id_str = str(nro_id).strip()
                
                if pd.isna(nro_id) or nro_id_str == 'nan' or not nro_id_str:
                    errores_col['Err_NroId'][index] = "DNI vacío"
                else:
                    if not nro_id_str.replace('.', '').isdigit() or '.' in nro_id_str or ',' in nro_id_str:
                        errores_col['Err_NroId'][index] = "DNI con letras/puntos"
                    elif tipo_id == 'PASAPORTE':
                        if not nro_id_str.isdigit() or nro_id_str.startswith('0'):
                            errores_col['Err_NroId'][index] = "Pasaporte inicia con 0 o tiene letras"
                
                fecha_nac = row.get('*Fecha de Nacimiento')
                if pd.notna(fecha_nac):
                    es_valida = True
                    if not isinstance(fecha_nac, pd.Timestamp) and not isinstance(fecha_nac, datetime):
                        total_fechas_mal_formato += 1
                        fecha_str = str(fecha_nac)
                        numeros = re.sub(r'[^0-9]', '', fecha_str)
                        corregida = False
                        
                        if len(numeros) == 8:
                            try:
                                fecha_limpia = pd.to_datetime(numeros, format='%d%m%Y')
                                df.at[index, '*Fecha de Nacimiento'] = fecha_limpia
                                fecha_nac = fecha_limpia
                                corregida = True
                                total_fechas
