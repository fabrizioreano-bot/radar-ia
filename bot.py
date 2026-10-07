import json
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

JSON_FILE = 'datos.json'

# URLs oficiales de los 7 operadores / loterías
OPERADORES_URLS = {
    "doradobet": "https://doradobet.com/",
    "lotowow": "https://lotowow.pe/",
    "te-apuesto": "https://www.teapuesto.pe/",
    "betano": "https://www.betano.pe/",
    "betsson": "https://www.betsson.pe/",
    "olimpo-bet": "https://olimpo.bet/",
    "apuesta-total": "https://www.apuestatotal.com/"
}

async def escandear_operador(page, op_id, url):
    print(f"🔍 Auditando portal en vivo: {op_id} -> {url}")
    try:
        # Intenta cargar la portada con tiempo límite de 30s
        response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        if response and response.status == 200:
            print(f"  ✓ {op_id}: Operativo y respondiendo.")
            return "Operativo"
        else:
            print(f"  ⚠️ {op_id}: Respuesta inusual (Código {response.status if response else 'Sin respuesta'})")
            return "Inestable"
    except Exception as e:
        print(f"  ❌ {op_id}: Error al acceder -> {e}")
        return "Fuera de servicio"

async def ejecutar_bot():
    if not os.path.exists(JSON_FILE):
        print("⚠️ No se encontró el archivo datos.json.")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Recorrer los operadores registrados en datos.json
        for op in data.get("operadores", []):
            op_id = op.get("id")
            if op_id in OPERADORES_URLS:
                estado_sitio = await escandear_operador(page, op_id, OPERADORES_URLS[op_id])
                
                # Actualiza el estado operativo individual de cada canal de recarga
                if "recargas" in op:
                    for recarga in op["recargas"]:
                        recarga["estado"] = estado_sitio

        await browser.close()

    # Actualiza la estampa con fecha y hora de Lima/Perú
    ahora = datetime.now()
    data['ultima_actualizacion'] = f"Última verificación en vivo: {ahora.strftime('%d/%m/%Y a las %H:%M')}"

    # Guarda el JSON preservando las banderas de Visa y los límites del nuevo diseño
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Proceso de scraping diario finalizado y datos.json actualizado.")

if __name__ == '__main__':
    asyncio.run(ejecutar_bot())
