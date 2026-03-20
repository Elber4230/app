import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse

# CONFIGURACIÓN ESPECIAL PARA STREAMLIT CLOUD
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # En Streamlit Cloud, el binario ya está en esta ruta gracias a packages.txt
    return webdriver.Chrome(options=options)

st.set_page_config(page_title="Cotizador Pro", page_icon="📚")
st.title("🚀 Buscador de Libros & Negociación")

busqueda = st.text_input("ISBN o Título del libro:", placeholder="Ej: Alas de Ónix")

if st.button("🔍 Calcular Negociación"):
    if not busqueda:
        st.warning("Por favor ingresa un título o ISBN.")
    else:
        with st.spinner('Escaneando mercado...'):
            try:
                driver = get_driver()
                driver.get(f"https://www.buscalibre.com.co/libros/search?q={busqueda}")
                time.sleep(4) # Un poco más de tiempo para asegurar la carga
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()

                precios_nuevos = []
                # Buscamos los contenedores de producto
                for p in soup.find_all('div', class_='producto'):
                    condicion = p.find('span', class_='condicion')
                    # Filtro estricto: solo libros NUEVOS
                    if condicion and "nuevo" in condicion.text.lower():
                        precio_tag = p.find('p', class_='precio-ahora')
                        if precio_tag:
                            valor = int(''.join(filter(str.isdigit, precio_tag.text)))
                            precios_nuevos.append(valor)

                if precios_nuevos:
                    pb = min(precios_nuevos)
                    # Lógica de negociación: sondeo de mercado estimado
                    pn = pb + 15000 
                    pv = pn - 1000 if pn > pb else pb 
                    
                    p_compra = pv * 0.90
                    utilidad = pv - p_compra
                    p_envio = pv + 7900

                    st.markdown("---")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("PRECIO COMPRA", f"${p_compra:,.0f}")
                    with c2:
                        st.metric("UTILIDAD", f"${utilidad:,.0f}")
                    with c3:
                        st.metric("CON ENVÍO", f"${p_envio:,.0f}")
                    
                    st.success(f"Precio de Venta Sugerido: **${pv:,.0f}**")

                    # Botón de WhatsApp
                    mensaje = f"Cotización de libro:\n📖 {busqueda}\n💰 Precio: ${pv:,.0f}\n🚚 Envío: $7,900\n✅ Total: ${p_envio:,.0f}"
                    whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(mensaje)}"
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">📱 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
                else:
                    st.error("No se encontraron ejemplares NUEVOS en Buscalibre.")
            
            except Exception as e:
                st.error(f"Hubo un error al conectar con el navegador: {e}")
