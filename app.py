import streamlit as st
import pandas as pd
from datetime import datetime
import io
from collections import Counter
import re
import string

# =========================================================
# LISTAS DESPLEGABLES EXTRAÍDAS DE LA PLANTILLA OFICIAL
# =========================================================
LISTAS_DESPLEGABLES = {
    'Acción': ['Agregar'],
    '*Tipo Id.': ['D.N.I.', 'Pasaporte'],
    '*Incapacidad': ['SI', 'NO'],
    '*Ocupación': ['Administración del hogar. Ama de casa.-4111', 'Administrativos-1112', 'Agricultores, productores y peones de cultivos mixtos y ganaderos-6114', 'Agricultores, productores y trabajadores de cultivos (Agropecuarios, alambradores)-6111', 'Agricultores, productores y trabajadores de plantaciones de frutales, huertas, invernaderos y viveros-6113', 'Agricultores, productores y trabajadores de plantaciones de árboles y arbustos. Trabajadores forestales. (desmonte, hacheros)-6112', 'Alfareros y afines. Barro, arcilla, abrasivos.-8113', 'Alumnos de escuelas, colegios y/o complejos educativos-9111', 'Aon 1-9995', 'Aon 2-9996', 'Aon 3-9997', 'Aon 4-9998', 'Apicultores-6117', 'Artesanos de los tejidos, el cuero y materiales similares (tapiceros)-8116', 'Artesanos en madera, cestería y materiales similares-8115', 'Avicultores-6116', 'Barnizadores, lustradores y afines-7219', 'Bomberos y rescatistas-4135', 'Carboneros de carbón vegetal y afines-6121', 'Colonias de vacaciones-9112', 'Comerciantes al por mayor de bebidas y/o tabacos. Fraccionamiento, carga y descarga, transporte/distribución y venta.-5112', 'Comerciantes al por mayor de madera, papel y derivados y/o materiales para la construcción. Carga y descarga, transporte/distribución y venta.-5114', 'Comerciantes al por mayor de productos alimentarios. Acopio, carga y descarga, distribución/transporte, fraccionamiento, abastecimiento y venta.-5111', 'Comerciantes al por mayor de textiles, prendas de vestir y cuero. Distribución y venta.-5113', 'Comercios al por mayor de motores, máquinas, equipos industriales, comerciales y domésticos. Distribución y venta.-5115', 'Comisionistas y/o cobradores-2116', 'Conductores de autobuses y/o ambulancias-3113', 'Conductores de automóviles, taxis y/o camionetas (remisero, taxista)-3112', 'Conductores de motocicletas y/o bicicletas (Delivery, cadete, repartidor)-3111', 'Conductores y/o acompañantes de camiones-3114', 'Conservación de redes de agua-7612', 'Conservación de redes de gas-7611', 'Constructores y/o demoledores de edificios y/o excavadores (Construcción, zanjeo, albañiles)-7111', 'Criadores de especies acuáticas-6122', 'Criadores de ganado y trabajadores pecuarios. Tamberos. (esquiladores, cuidadores de caballos)-6115', 'Criadores y trabajadores de la cría de animales diversos y de granja-6118', 'Cristaleros. Espejos, vidrios y afines (vidrieros)-7213', 'Cuidadores y adiestradores animales domésticos-4112', 'Deportistas en la práctica de Fútbol-9138', 'Deportistas en la práctica de Hockey-9139', 'Deportistas en la práctica de artes marciales, boxeo, rugby-9144', 'Deportistas en la práctica de básquet, handball, mountain bike, airsoft, arquería-9140', 'Deportistas en la práctica de canotaje, kayak, stand up paddle, Windsurf, Kite, rapel, escalada, esquí, pesca deportiva, equitación, cabalgata-9116', 'Deportistas en la práctica de doma, jinete, jockey, pato, hipismo, sortija-9143', 'Deportistas en la práctica de fútbol, básquet, hockey, handball.-9115', 'Deportistas en la práctica de golf, paddle,  squash, tenis, voleyball, natación en piscinas, ciclismo, atletismo, gimnasia deportiva, esgrima, patinaje, newcom, trekking sin altura, running, maratón-9114', 'Directores y gerentes (Consejeros, Presidente comisión directiva)-1111', 'Electricistas (Instalación domiciliaria e industrial, alarmas)-7511', 'Empleadores / Directivos-9131', 'Empleadores / Oficios-9132', 'En tránsito vehicular-9123', 'En tránsito vehicular-9124', 'Especialistas en operaciones comerciales. Recibidores, rematadores, despachantes de aduana y Agente marítimo-2115', 'Especialistas en operaciones financieras y de administración de empresas. Contadores, productores de seguros, tasadores, agentes de bolsa y cambio. (Actuarios, administrador de propiedades, gestores, peritos)-2114', 'Expendio de combustibles. Estaciones de servicio.-5233', 'Fotógrafos (camarógrafos)-4117', 'Fumigadores terrestres-6123', 'Fumigadores, desinfecciones y otros controladores de plagas domiciliarias-4113', 'Herreros, torneros y forjadores-7311', 'Impresores y/o estampadores y operadores de máquinas de imprenta (Imprenta y litografía)-8118', 'Instaladores de material aislante (Impermeabilización de techos)-7212', 'Instaladores y reparadores de líneas eléctricas-7514', 'Instaladores y reparadores de líneas telefónicas, de tecnología de la información y comunicaciones-7516', 'Jardineros y pileteros (casas particulares)-9135', 'Joyeros, orfebres y plateros-8112', 'Lavadores y/o engrasadores de vehículos.-4114', 'Lavanderos, planchadores, tintoreros-4115', 'Limpiadores de oficinas, hoteles y otros establecimientos-4116', 'Marineros de embarcaciones de paseo-3118', 'Mecánicos montadores de instalaciones de refrigeración y climatización (Reparación de aires acondicionados en vehículos)-7215', 'Mecánicos y reparadores de máquinas agrícolas e industriales-7412', 'Mecánicos y reparadores de vehículos de motor (Taller mecánico, chapa y pintura)-7411', 'Mecánicos y reparadores en electrónica (Técnico electrónico, electromecánico, service de máquinas)-7515', 'Montadores industriales de estructuras metálicas, antenas, maquinarias. (Antenista, ascensores, instalación de máquinas frigoríficas, aire acondicionado, armado de silos y/o norias, molinos, zinguería, cartelería, toldos, carpas)-7312', 'Operadores de grúas, de aparatos elevadores y afines-3117', 'Operadores de instalaciones electrónicas, tableros y/o consolas en la industria-7712', 'Operadores de instalaciones y de máquinas en la industria (operarios de fábrica, frigoríficos, metalúrgicos, fabricación de alimentos, carpintería, clasificador de cereal, aserradero, marmolería)-7711', 'Operadores de maquinaria agrícola y forestal motorizada (cosechadoras, tractores, cargadores frontales, equipos de forraje, sembradoras, desmalezadoras, pulverizadoras, motosierra, excavadora)-3115', 'Operadores de máquinas de movimiento de tierras y afines (Grúas, máquinas viales)-3116', 'Parqueteros y colocadores de suelos (Colocación y pulidores de pisos, alfombras y similares)-7211', 'Pasantías Escolares (tareas ADMINISTRATIVAS)-9136', 'Pasantías Escolares (tareas OFICIOS / TÉCNICOS)-9137', 'Peones de carga y descarga (reparto de gas domiciliario, mudanzas, embaladores, estibadores, reparto frigorífico)-4118', 'Peones de obras públicas y mantenimiento: carreteras, presas y obras similares-7113', 'Personal de pompas fúnebres y embalsamadores-4119', 'Pintores y empapeladores (Limpiadores de vidrios, colocación cielorraso)-7216', 'Plomeros y gasistas (instaladores de tuberías de agua y gas)-7214', 'Porteros, conserjes, ordenanzas, encargados de garages y afines-4120', 'Profesionales de la enseñanza maestros, profesores, docentes y de las ciencias de la información/bibliotecarios-2113', 'Profesionales de la salud. Médicos, enfermeras, paramédicos. (Instrumentista, odontólogo, mecánico dental, radiólogo, oftalmólogo, kinesiologo, fisioterapeuta, fonoudiología, anestesista, camillero)-2112', 'Profesionales de las actividades deportivas. Instructores de educación física, entrenadores, guías de turismo, árbitros o similares.-2121', 'Profesionales de las artes y la cultura. Periodistas, traductores, escritores, locutores, músicos, artistas, actores, diseñadores.-2120', 'Profesionales de las ciencias sociales. Psicólogos, sociólogos, religiosos, Acompañante terapéutico, psicopedagoga.-2119', 'Profesionales de las ciencias y de la ingeniería. Ingenieros,  arquitectos, técnicos, bioquímicos, químicos, biólogos, físicos, geólogos (supervisor, inspectores, laboratorio, topografos y geografos, enologos, agrimensores)-2111', 'Profesionales de tecnología de la información y las comunicaciones, Desarrolladores y analistas de software, administradores de bases de datos, técnicos.-2117', 'Profesionales del derecho. Abogados, jueces o similares, escribanos, procuradores.-2118', 'Pulidores de metales y afiladores de herramientas-7314', 'Reparadores de instrumentos de precisión-8111', 'Sastres, modistos, costureros, bordadores, peleteros, sombrereros y afines-8211', 'Senderismo / Trekking Ushuaia (Residentes)-9141', 'Senderismo / Trekking Ushuaia (Turistas)-9142', 'Servicio Dom. Casas Familia M.V.-9126', 'Servicios de belleza, higiene y estética corporal (Manicura, masajista, pedicuro, peluquero, coiffeur)-4121', 'Servicios de comida y hospedaje prestados en hoteles y similares. Mucamas y cocineros.-4134', 'Servicios de comidas y bebidas prestados en eventos y similares.-4133', 'Servicios de comidas y bebidas prestados en restaurantes, bares y cafés. (cocinero, chef, mozo, barman, catering)-4132', 'Servicios de correo-4136', 'Servicios de diversión y esparcimiento en salones de baile, discotecas, salones de juegos electrónicos, billar y similares. (DJ, sonidista y armado de equipos, iluminación, decoradores de eventos)-4122', 'Servicios de jardinería y horticultura, poda, desmalezamiento y afines-4123', 'Servicios de mantenimiento general de instalaciones en establecimientos o instituciones-4124', 'Servicios de promociones y/o modelaje publicitario o artístico (promotores, modelos, encuestadores, personal en stands)-4125', 'Servicios de protección (bañeros o guardavidas en clubes o instituciones)-4126', 'Servicios de reparación de artículos personales, de los hogares y cerrajeros-4127', 'Servicios de saneamiento y similares. Recolección de residuos, limpieza, desagote de pozos (limpieza tanques de agua)-4128', 'Servicios de seguridad y vigilancia. Serenos, vigilantes, guardaparques y afines. (casero, personal de guardia)-4129', 'Servicios domésticos, cuidadores de niños, cuidadores personales, mucamas-4130', 'Servicios prestados por municipalidades o comunas-4131', 'Soldadores y oxicortadores-7315', 'Sopladores, moldeadores, laminadores, cortadores y pulidores de vidrios-8114', 'Tapiceros, colchoneros y afines-8213', 'Tareas varias por M.V.-9125', 'Transportistas-9130', 'Vendedores de aparatos fotográficos, artículos de fotografía e instrumentos de óptica.-5241', 'Vendedores de armas y cuchillería.-5226', 'Vendedores de artefactos eléctricos para iluminación.-5238', 'Vendedores de artículos de bazar y menaje. Bazares.-5235', 'Vendedores de artículos de juguetería y cotillón. Jugueterías.-5224', 'Vendedores de artículos de librería, papelería y oficina. Librerías y papelerías.-5225', 'Vendedores de artículos de tocador y cosméticos. Perfumerías.-5229', 'Vendedores de artículos para el hogar. Heladeras, lavarropas, televisores, etc.-5237', 'Vendedores de aves y huevos, animales de corral y caza y otros productos de granja.-5213', 'Vendedores de billetes de lotería y otros juegos de azar. Agencias de lotería.-5219', 'Vendedores de calzado y artículos de cuero. Zapaterías. Zapatillerías. Marroquinerías.-5221', 'Vendedores de carne y derivados. Carnicerías-5212', 'Vendedores de cámaras y cubiertas. Gomerías.-5234', 'Vendedores de flores y plantas. Distribución y venta.-5116', 'Vendedores de friambres y comidas preparadas. Rotiserías y fiambrerias.-5215', 'Vendedores de instrumentos musicales y/o discos. Disquerías. (playeros)-5223', 'Vendedores de muebles. Mueblerías.-5222', 'Vendedores de pan y demás productos de panadería. Panaderías, confiterías y/o fábrica de pastas frescas. (venta, producción, elaboración de pan y pastas)-5217', 'Vendedores de pescados y otros productos marinos, fluviales y lacustres. Pescaderías.-5214', 'Vendedores de pinturas, barnices, esmaltes, artículos de ferretería. Ferreterías y pinturerías.-5228', 'Vendedores de prendas de vestir y/o productos textiles.-5220', 'Vendedores de productos en almacenes, supermercados o autoservicios. (Repositores, cajeros).-5211', 'Vendedores de productos farmacéuticos y medicinales. Farmacias.-5227', 'Vendedores de productos medicinales para animales. Veterinarias.-5230', 'Vendedores de repuestos y accesorios para automotores.-5240', 'Vendedores de sanitarios.-5236', 'Vendedores de semillas, abonos y plaguicidas.-5231', 'Vendedores de tabaco, cigarrillos, golosinas.-5218', 'Vendedores de vehículos automotores.-5239', 'Vendedores de verduras, frutas y hortalizas frescas. Verdulerías y fruterías.-5216', 'Veterinarios de animales domésticos-2123', 'Veterinarios y vacunadores rurales-2122', 'Viajeros, excursionistas, campamentistas, turistas-9113', 'Viajes Fuera Territorio Nacional (Exterior)-9120', 'Viajes Territorio Nacional-9119', 'Vitivinicultores y/u olivicultores-6120', 'Yeseros-7218', 'Zapateros y afines-8214'],
    '*Nacionalidad': ['Afganistan ', 'Albania', 'Alemania', 'Andorra', 'Angola', 'Anguila', 'Antartida', 'Antigua y Barbuda', 'Antillas Holandesas', 'Arabia Saudita', 'Argelia', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaiyan', 'Bahamas', 'Bahrein', 'Banglades', 'Barbados', 'Belgica', 'Belice', 'Benin', 'Bermudas', 'Bielorrusia', 'Bolivia', 'Bosnia y Herzegovina', 'Botsuana', 'Brasil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Butan', 'Cabo Verde', 'Camboya', 'Camerun', 'Canada', 'Catar', 'Chad', 'Chile', 'China', 'Chipre', 'Colombia', 'Comoras', 'Congo', 'Corea del Norte', 'Costa de Marfil', 'Costa Rica', 'Croacia', 'Cuba', 'Curazao', 'Dinamarca', 'Dominica', 'Ecuador', 'Edos. Federados de Micronesia', 'Egipto', 'El Salvador', 'Emiratos Arabes Unidos', 'Eritrea', 'Escocia', 'Eslovaquia', 'España', 'Estados Unidos de America', 'Estonia', 'Etiopia', 'Finlandia', 'Fiyi', 'Francia', 'Gabon', 'Gales', 'Gambia', 'Georgia', 'Ghana', 'Gibraltar', 'Granada', 'Grecia', 'Groenlandia', 'Guadalupe', 'Guam', 'Guatemala', 'Guayana Francesa', 'Guernsey', 'Guinea', 'Guinea Bissau', 'Guinea Ecuatorial', 'Guyana', 'Haiti', 'Hawai', 'Honduras', 'Hong Kong', 'Hungria', 'Inglaterra', 'Irak', 'Iran', 'Irlanda del Norte', 'Is. Georgia y Sandwich del Sur', 'Isla Ascension', 'Isla Bouvet', 'Isla de Man', 'Isla Navidad', 'Isla Norfolk', 'Isla Pitcairn', 'Islandia', 'Islas Caiman', 'Islas Cocos', 'Islas Cook', 'Islas Feroe', 'Islas Heard y McDonald', 'Islas Malvinas', 'Islas Marshall', 'Islas Salomon', 'Islas Svalbard y Jan Mayen', 'Islas Turcas y Caicos', 'Islas Virgenes Americanas', 'Islas Virgenes Britanicas', 'Israel', 'Italia', 'Jamaica', 'Japon', 'Jersey', 'Jordania', 'Kazajistan', 'Kenia', 'Kirguisa', 'Kiribati', 'Kuwait', 'Laos', 'Lesoto', 'Letonia', 'Libano', 'Liberia', 'Libia', 'Liechtenstein', 'Lituania', 'Luxemburgo', 'Macao', 'Macedonia', 'Madagascar', 'Malasia', 'Malaui', 'Maldivas', 'Mali', 'Malta', 'Marianas del Norte ', 'Martinica', 'Mauricio', 'Mauritania', 'Mayotte', 'Mexico', 'Moldavia', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Noruega', 'Nueva Caledonia', 'Nueva Zelanda', 'Oman', 'Paises Bajos', 'Pakistan', 'Palaos', 'Palestina', 'Papua Nueva Guinea', 'Paraguay', 'Peru', 'Polinesia Francesa', 'Polonia', 'Portugal', 'Puerto Rico', 'Reino de Marruecos', 'Rep. Bolivariana de Venezuela', 'Rep. Corea (Sur)', 'Rep.Democratica del Congo ', 'Republica Centroafricana', 'Republica Checa', 'Republica de Eslovenia', 'Republica de Filipinas', 'Republica de Indonesia', 'Republica de Irlanda', 'Republica de la India', 'Republica de Panama', 'Republica de Sudafrica', 'Republica Dominicana', 'Republica Oriental del Uruguay', 'Reunion', 'Ruanda', 'Rumania', 'Rusia', 'Sahara Occidental', 'Samoa', 'Samoa Americana', 'San Cristobal y Nieves', 'San Marino', 'San Pedro y Miquelon', 'San Vicente y las Granadinas', 'Santa Elena', 'Santa Lucia', 'Santo Tome y Principe', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leona', 'Singapur', 'Siria', 'Somalia', 'Sri Lanka', 'Suazilandia', 'Sudan', 'Sudan del sur', 'Suecia', 'Suiza', 'Surinam', 'Tailandia', 'Taiwan', 'Tanzania', 'Tayikistan ', 'Terr. Británico del Oc. Indico', 'Tibet', 'Timor Oriental', 'Togo', 'Tokelau', 'Tonga', 'Trinidad y Tobago', 'Tunez', 'Turkmenistan', 'Turquia', 'Tuvalu', 'Ucrania', 'Uganda', 'Uzbekistan', 'Vanuatu', 'Vaticano', 'Vietnam', 'Wallis y Futuna', 'Yemen', 'Yibuti', 'Zambia', 'Zimbabue']
}

# =========================================================
# FUNCIÓN PARA INYECTAR LAS LISTAS DESPLEGABLES EN EXCEL
# =========================================================
def inyectar_listas_desplegables(writer, df_export, workbook, sheet_name):
    worksheet_main = writer.sheets[sheet_name]
    worksheet_dv = workbook.add_worksheet('DataValidation')
    
    col_idx = 0
    for col_name, valores in LISTAS_DESPLEGABLES.items():
        # Escribimos los datos en la hoja oculta
        worksheet_dv.write(0, col_idx, col_name)
        worksheet_dv.write_column(1, col_idx, valores)
        
        # Buscamos si la columna existe en el Excel que estamos por descargar
        if col_name in df_export.columns:
            main_col_idx = list(df_export.columns).index(col_name)
            
            # Cálculo de la letra de la columna para la fórmula de Excel
            if col_idx < 26:
                letra_col_dv = string.ascii_uppercase[col_idx]
            else:
                letra_col_dv = string.ascii_uppercase[col_idx // 26 - 1] + string.ascii_uppercase[col_idx % 26]
                
            rango_formula = f"=DataValidation!${letra_col_dv}$2:${letra_col_dv}${len(valores)+1}"
            
            # Aplicamos la lista a todas las celdas de esa columna
            worksheet_main.data_validation(1, main_col_idx, 5000, main_col_idx, {
                'validate': 'list',
                'source': rango_formula
            })
            
        col_idx += 1
        
    worksheet_dv.hide()

# Configuración de la página
st.set_page_config(page_title="Validador de Cargas AP", layout="wide")

# Fondo de pantalla y estilos
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

    label[data-testid="stWidgetLabel"] p {
        color: white !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.6);
    }

    /* Pestañas (Botones) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px !important;
        background-color: transparent !important;
        flex-wrap: wrap !important;
    }

    button[data-baseweb="tab"] {
        background-color: rgba(0, 0, 0, 0.6) !important; 
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 12px 24px !important;
        margin: 0 !important;
    }
    
    button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 800 !important; 
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.4) !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] p {
        color: #900000 !important; 
        font-weight: 900 !important; 
    }

    div[data-baseweb="tab-highlight"], 
    div[data-baseweb="tab-border"] {
        display: none !important;
        background-color: transparent !important;
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
        content: "Límite 200MB • Excel/CSV/PDF";
        color: rgba(49, 51, 63, 0.6);
        display: block;
        margin-top: -15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 style="color: white; text-shadow: 2px 2px 5px rgba(0,0,0,0.6);">Asistente de Solicitudes de Accidentes Personales</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: white; font-size: 18px; text-shadow: 1px 1px 4px rgba(0,0,0,0.6); margin-bottom: 30px;">Seleccioná la herramienta que necesites usar hoy.</p>', unsafe_allow_html=True)

tab_armador, tab_validador, tab_pdf = st.tabs(["🪄 Armar Excel (Limpiador)", "✅ Validar Carga", "📄 PDF a Excel / Word"])

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
                columnas_oficiales = ['Acción', '*Tipo Id.', '*Nro. Id.', '*Fecha de Nacimiento', '*Apellido', '*Nombre', '*S.A. Individual Muerte', 'S.A. Individual Inválidez', 'S.A. AMF', '*Incapacidad', '*Ocupación', '*Nacionalidad']
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

                # Autocompletado oficial
                df_oficial['Acción'] = 'Agregar'
                df_oficial['*Tipo Id.'] = 'D.N.I.'
                df_oficial['*Nacionalidad'] = 'Argentina'
                df_oficial['*Incapacidad'] = 'NO'
                
                st.success("✅ Plantilla generada exitosamente. Se limpiaron los datos y se aplicaron los valores por defecto y las listas desplegables.")
                st.dataframe(df_oficial)
                
                buffer_armado = io.BytesIO()
                
                with pd.ExcelWriter(buffer_armado, engine='xlsxwriter', datetime_format='dd/mm/yyyy', date_format='dd/mm/yyyy') as writer:
                    df_oficial.to_excel(writer, index=False, sheet_name="AP - Personas x Grupo")
                    workbook = writer.book
                    inyectar_listas_desplegables(writer, df_oficial, workbook, "AP - Personas x Grupo")
                
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
# PESTAÑA 2: VALIDADOR ESTRICTO
# ==========================================
with tab_validador:
    col1b, col2b = st.columns([2, 3])
    with col1b:
        archivo_agente = st.file_uploader("Seleccioná el archivo Excel listo (.xlsx)", type=["xlsx"], key="uploader_validador")

    if archivo_agente is not None:
        try:
            df = pd.read_excel(archivo_agente, sheet_name="AP - Personas x Grupo")
            st.info("Procesando validaciones y corrigiendo formatos...")
