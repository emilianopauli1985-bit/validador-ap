import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(page_title="Validador de Cargas AP", layout="centered")

st.title("Validador de Solicitudes AP - Personas x Grupo")
st.write("Subí tu Excel para controlar que no tenga errores antes de enviarlo a emisión.")

# Subida del archivo por el agente
archivo_agente = st.file_uploader("Seleccioná el archivo Excel (.xlsx)", type=["xlsx"])

if archivo_agente is not None:
    try:
        # Leer el archivo del agente
        df = pd.read_excel(archivo_agente, sheet_name="AP - Personas x Grupo")
        st.info("Procesando validaciones...")

        errors_list = [[] for _ in range(len(df))]
        hoy = pd.Timestamp.today()

        # Aplicar reglas fila por fila
        for index, row in df.iterrows():
            errs = []
            
            # 1. Tipo Id.
            tipo_id = str(row.get('*Tipo Id.', '')).strip().upper()
            if pd.isna(row.get('*Tipo Id.')) or tipo_id == 'NAN' or not tipo_id:
                errs.append("Tipo Id: Debe seleccionar D.N.I. o Pasaporte")
            
            # 2. Nro. Id.
            nro_id = row.get('*Nro. Id.')
            nro_id_str = str(nro_id).strip()
            
            if pd.isna(nro_id) or nro_id_str == 'nan' or not nro_id_str:
                errs.append("Nro Id: Debe ingresar el número de documento.")
            else:
                if not nro_id_str.replace('.', '').isdigit() or '.' in nro_id_str or ',' in nro_id_str:
                    errs.append("Nro Id: El DNI debe contener únicamente números.")
                
                if tipo_id == 'PASAPORTE':
                    if not nro_id_str.isdigit() or nro_id_str.startswith('0'):
                        errs.append("Nro Id (Pasaporte): No puede comenzar con cero y debe tener solo números.")
            
            # 3. Fecha de Nacimiento
            fecha_nac = row.get('*Fecha de Nacimiento')
            if pd.notna(fecha_nac):
                if not isinstance(fecha_nac, pd.Timestamp) and not isinstance(fecha_nac, datetime):
                    errs.append("Fecha Nac: Formato de texto. Use formato de Fecha en Excel.")
                else:
                    if fecha_nac > hoy:
                        errs.append("Fecha Nac: La fecha no puede ser futura.")
                    else:
                        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                        if edad < 15:
                            errs.append("Fecha Nac: El asegurado debe ser mayor de 14 años.")
                            
            # 4. Sumas Aseguradas
            sumas = [('*S.A. Individual Muerte', 'Muerte'), ('S.A. Individual Inválidez', 'Invalidez'), ('S.A. AMF', 'AMF')]
            for col_sa, nombre_err in sumas:
                sa_val = row.get(col_sa)
                if pd.isna(sa_val):
                    errs.append(f"S.A. {nombre_err}: Debe colocar suma asegurada.")
                else:
                    try:
                        float(sa_val)
                    except ValueError:
                        errs.append(f"S.A. {nombre_err}: Debe ser un número.")
                        
            # 5. Incapacidad
            incap = str(row.get('*Incapacidad')).strip().upper()
            if incap not in ['SI', 'NO']:
                errs.append("Incapacidad: Debe indicar SI o NO.")
                
            # 6. Ocupación y Nacionalidad
            ocup = str(row.get('*Ocupación')).strip().upper()
            if pd.isna(row.get('*Ocupación')) or ocup == 'NAN' or not ocup:
                errs.append("Ocupación: Debe detallar la ocupación.")
                
            nac = str(row.get('*Nacionalidad')).strip().upper()
            if pd.isna(row.get('*Nacionalidad')) or nac == 'NAN' or not nac:
                errs.append("Nacionalidad: Debe indicar la nacionalidad.")
                
            errors_list[index].extend(errs)

        # Control de Duplicados DNI
        nro_ids = df['*Nro. Id.'].dropna().astype(str).tolist()
        dups = set([x for x in nro_ids if nro_ids.count(x) > 1])

        for index, row in df.iterrows():
            nro_id = str(row.get('*Nro. Id.'))
            if nro_id in dups:
                errors_list[index].append("Nro Id: DNI duplicado en el archivo.")

        # Generar columna final
        df['Errores Detectados'] = ["; ".join(errs) if errs else "OK" for errs in errors_list]
        errores_totales = sum(1 for errs in errors_list if errs)
        
        # Resultados visuales
        if errores_totales == 0:
            st.success("✅ ¡Excelente! El archivo no tiene errores. Podés enviarlo.")
        else:
            st.error(f"❌ Se encontraron errores en {errores_totales} asegurados. Descargá el reporte para ver el detalle y corregirlos.")
            st.write("Vista previa de las inconsistencias:")
            st.dataframe(df[df['Errores Detectados'] != "OK"][['*Nro. Id.', '*Apellido', '*Nombre', 'Errores Detectados']])

        # Botón de descarga
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="AP - Personas x Grupo")
        
        st.download_button(
            label="📥 Descargar Excel con Reporte de Errores" if errores_totales > 0 else "📥 Descargar Excel Validado",
            data=buffer.getvalue(),
            file_name="Control_AP.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error al leer el archivo. Verificá que la pestaña se llame exactamente 'AP - Personas x Grupo'. Detalle técnico: {e}")
