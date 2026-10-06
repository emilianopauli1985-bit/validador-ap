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
    
    /* Fondito blanco semitransparente para que los carteles y la tabla se lean bien */
    .stAlert, [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
    }

    /* Título del uploader en color blanco */
    label[data-testid="stWidgetLabel"] p {
        color: white !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.6);
    }

    /* TRUCO CSS: Ocultar texto en inglés del botón y poner español */
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
    
    /* TRUCO CSS: Ocultar límite en inglés y poner español */
    [data-testid="stFileUploadDropzone"] small {
        color: transparent !important;
    }
    [data-testid="stFileUploadDropzone"] small::after {
        content: "Límite 200MB • XLSX";
        color: rgba(49, 51, 63, 0.6);
        display: block;
        margin-top: -15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título y subtítulo forzados en color blanco
st.markdown('<h1 style="color: white; text-shadow: 2px 2px 5px rgba(0,0,0,0.6);">Validador de Solicitudes AP - Personas x Grupo</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: white; font-size: 18px; text-shadow: 1px 1px 4px rgba(0,0,0,0.6);">Subí tu Excel para controlar que no tenga errores antes de enviarlo a emisión.</p>', unsafe_allow_html=True)

# Achicamos el ancho del uploader usando columnas (ocupa el 40% de la pantalla)
col1, col2 = st.columns([2, 3])

with col1:
    archivo_agente = st.file_uploader("Seleccioná el archivo Excel (.xlsx)", type=["xlsx"])

# A partir de acá, el código de validación sigue exactamente igual
if archivo_agente is not None:
    try:
        # Leer el archivo del agente
        df = pd.read_excel(archivo_agente, sheet_name="AP - Personas x Grupo")
        st.info("Procesando validaciones y corrigiendo formatos...")

        hoy = pd.Timestamp.today()
        
        total_fechas_mal_formato = 0
        total_fechas_corregidas = 0
        
        errores_col = {
            'Err_TipoId': [''] * len(df),
            'Err_NroId': [''] * len(df),
            'Err_FechaNac': [''] * len(df),
            'Err_SAMuerte': [''] * len(df),
            'Err_SAInvalidez': [''] * len(df),
            'Err_SAAMF': [''] * len(df),
            'Err_Incapacidad': [''] * len(df),
            'Err_Ocupacion': [''] * len(df),
            'Err_Nacionalidad': [''] * len(df)
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
                            total_fechas_corregidas += 1
                        except:
                            pass
                    
                    if not corregida:
                        errores_col['Err_FechaNac'][index] = "Fecha en formato texto irreconocible"
                        es_valida = False

                if es_valida and (isinstance(fecha_nac, pd.Timestamp) or isinstance(fecha_nac, datetime)):
                    if fecha_nac > hoy:
                        errores_col['Err_FechaNac'][index] = "Fecha futura"
                    else:
                        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                        if edad < 15:
                            errores_col['Err_FechaNac'][index] = "Menor de 15 años"
                            
            if pd.isna(row.get('*S.A. Individual Muerte')): errores_col['Err_SAMuerte'][index] = "S.A. Muerte vacía"
            else:
                try: float(row.get('*S.A. Individual Muerte'))
                except: errores_col['Err_SAMuerte'][index] = "S.A. Muerte no es número"

            if pd.isna(row.get('S.A. Individual Inválidez')): errores_col['Err_SAInvalidez'][index] = "S.A. Invalidez vacía"
            else:
                try: float(row.get('S.A. Individual Inválidez'))
                except: errores_col['Err_SAInvalidez'][index] = "S.A. Invalidez no es número"

            if pd.isna(row.get('S.A. AMF')): errores_col['Err_SAAMF'][index] = "S.A. AMF vacía"
            else:
                try: float(row.get('S.A. AMF'))
                except: errores_col['Err_SAAMF'][index] = "S.A. AMF no es número"
                    
            incap = str(row.get('*Incapacidad')).strip().upper()
            if incap not in ['SI', 'NO']:
                errores_col['Err_Incapacidad'][index] = "Incapacidad debe ser SI o NO"
                
            ocup = str(row.get('*Ocupación')).strip().upper()
            if pd.isna(row.get('*Ocupación')) or ocup == 'NAN' or not ocup:
                errores_col['Err_Ocupacion'][index] = "Ocupación vacía"
                
            nac = str(row.get('*Nacionalidad')).strip().upper()
            if pd.isna(row.get('*Nacionalidad')) or nac == 'NAN' or not nac:
                errores_col['Err_Nacionalidad'][index] = "Nacionalidad vacía"

        nro_ids = df['*Nro. Id.'].dropna().astype(str).tolist()
        dups = set([x for x in nro_ids if nro_ids.count(x) > 1])

        for index, row in df.iterrows():
            nro_id = str(row.get('*Nro. Id.'))
            if nro_id in dups:
                actual = errores_col['Err_NroId'][index]
                errores_col['Err_NroId'][index] = "DNI duplicado" if not actual else actual + " / DNI duplicado"

        lista_todos_errores = []
        for categoria, lista_err in errores_col.items():
            for error in lista_err:
                if error != '':
                    for sub_error in error.split(" / "):
                        lista_todos_errores.append(sub_error)
        
        conteo_errores = Counter(lista_todos_errores)

        tiene_error_fila = [False] * len(df)
        mapa_nombres = {
            'Err_TipoId': 'Error: Tipo Id',
            'Err_NroId': 'Error: Nro Id',
            'Err_FechaNac': 'Error: Fecha Nac',
            'Err_SAMuerte': 'Error: SA Muerte',
            'Err_SAInvalidez': 'Error: SA Invalidez',
            'Err_SAAMF': 'Error: SA AMF',
            'Err_Incapacidad': 'Error: Incapacidad',
            'Err_Ocupacion': 'Error: Ocupación',
            'Err_Nacionalidad': 'Error: Nacionalidad'
        }

        columnas_con_errores = []
        for clave, nombre_col in mapa_nombres.items():
            if any(errores_col[clave]): 
                df[nombre_col] = errores_col[clave]
                columnas_con_errores.append(nombre_col)
                for i, val in enumerate(errores_col[clave]):
                    if val != '': tiene_error_fila[i] = True

        df.insert(0, 'Estado Fila', ["❌ ERROR" if e else "✅ OK" for e in tiene_error_fila])
        errores_totales = sum(tiene_error_fila)
        
        if total_fechas_mal_formato > 0:
            st.success(f"🪄 **Autocorrección Inteligente:** Se detectaron {total_fechas_mal_formato} fechas de nacimiento mal escritas. El sistema logró corregir automáticamente {total_fechas_corregidas} de ellas.")
        
        if errores_totales == 0:
            st.success("✅ ¡Excelente! El archivo ya no tiene errores y está listo para enviar.")
        else:
            st.error(f"❌ Se encontraron {errores_totales} filas con errores que requieren intervención manual.")
            
            st.markdown("### 📊 Detalle de Errores Restantes:")
            for error_texto, cantidad in conteo_errores.most_common():
                st.write(f"- **{cantidad}** x {error_texto}")
                
            st.write("---")
            st.write("Vista previa (descargá el Excel para ver todos los detalles y usar los filtros):")
            st.dataframe(df[df['Estado Fila'] == "❌ ERROR"][['Estado Fila', '*Nro. Id.', '*Apellido'] + columnas_con_errores])

        df['*Fecha de Nacimiento'] = pd.to_datetime(df['*Fecha de Nacimiento'], errors='ignore').dt.date
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="AP - Personas x Grupo")
            workbook = writer.book
            worksheet = writer.sheets['AP - Personas x Grupo']
            
            formato_rojo = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            formato_verde = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
            formato_amarillo = workbook.add_format({'bg_color': '#FFF2CC', 'font_color': '#9C6500'})
            
            worksheet.conditional_format('A2:A5000', {'type': 'text', 'criteria': 'containing', 'value': 'ERROR', 'format': formato_rojo})
            worksheet.conditional_format('A2:A5000', {'type': 'text', 'criteria': 'containing', 'value': 'OK', 'format': formato_verde})
            worksheet.set_column(0, 0, 15) 
            
            if columnas_con_errores:
                idx_inicio = len(df.columns) - len(columnas_con_errores)
                worksheet.set_column(idx_inicio, len(df.columns)-1, 25, formato_amarillo)

        st.download_button(
            label="📥 Descargar Excel con Reporte de Errores" if errores_totales > 0 else "📥 Descargar Excel Validado",
            data=buffer.getvalue(),
            file_name="Control_AP_Reporte.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error al leer el archivo. Detalle técnico: {e}")
