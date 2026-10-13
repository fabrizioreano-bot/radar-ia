import json
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

JSON_FILE = 'datos.json'

# URLs públicas donde los operadores publican sus campañas / promociones
URLS_PROMOS = {
    "doradobet": "https://doradobet.com/promociones",
    "betano": "https://www.betano.pe/ofertas/",
    "apuesta-total": "https://www.apuestatotal.com/promociones",
    "te-apuesto": "https://www.teapuesto.pe/promociones",
    "betsson": "https://www.betsson.pe/promociones/"
}

async def extraer_campanas_reales(page, op_id, url):
    print(f"🔍 [Extrayendo Datos] Escaneando promociones en vivo: {url}")
    campanas_encontradas = []
    try:
        # Entramos a la página de promociones
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000) # Esperamos 4 segundos para que carguen los banners
        
        # Extraemos todos los subtítulos (h2 y h3) que suelen ser los nombres de las promociones
        elementos = await page.query_selector_all("h2, h3")
        for el in elementos:
            texto = await el.inner_text()
            # Filtramos textos cortos o muy largos para quedarnos con los títulos reales
            if texto and 5 < len(texto) < 50:
                campanas_encontradas.append(texto.strip())
        
        # Eliminamos duplicados
        campanas_encontradas = list(set(campanas_encontradas))
        
        if campanas_encontradas:
            print(f"  ✓ {op_id}: ¡Datos extraídos! ({len(campanas_encontradas)} campañas)")
            return campanas_encontradas[:2] # Devolvemos las 2 campañas principales
        else:
            print(f"  ⚠️ {op_id}: No se detectaron textos de campañas legibles.")
            return []
    except Exception as e:
        print(f"  ❌ {op_id}: Bloqueo o error al leer la página -> {e}")
        return []

async def ejecutar_bot():
    if not os.path.exists(JSON_FILE):
        print("⚠️ No se encontró el archivo datos.json.")
        return

    # 1. Leemos la base de datos actual
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Aseguramos que exista el bloque de campañas en el JSON
    if "campanas_extraidas" not in data:
        data["campanas_extraidas"] = []
    
    nuevas_campanas = []

    # 2. Iniciamos el navegador robot
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 3. Recorremos las casas y extraemos la data
        for op_id, url in URLS_PROMOS.items():
            titulos = await extraer_campanas_reales(page, op_id, url)
            
            for titulo in titulos:
                nuevas_campanas.append({
                    "operador": op_id.capitalize(),
                    "tipo": "Detectada en Web",
                    "nombre": titulo,
                    "estado": "Activa",
                    "ganadores": "Automático (Scraping)"
                })

        await browser.close()

    # 4. Actualizamos el JSON con la data 100% fresca extraída de las páginas
    ahora = datetime.now()
    data['ultima_actualizacion'] = f"Última extracción automática: {ahora.strftime('%d/%m/%Y %H:%M')}"
    
    # Si encontró campañas en vivo, reemplazamos las antiguas
    if nuevas_campanas:
        data["campanas_extraidas"] = nuevas_campanas

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Proceso completado. La data real ha sido sacada de las páginas.")

if __name__ == '__main__':
    asyncio.run(ejecutar_bot())
