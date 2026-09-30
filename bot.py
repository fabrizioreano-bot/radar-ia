import json
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

JSON_FILE = 'datos.json'

async def obtener_datos_casas():
    print("🚀 Iniciando navegador Chromium en modo invisible...")
    
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("⚠️ No se encontró datos.json base.")
        return None

    async with async_playwright() as p:
        # Abrimos Chromium simulando ser un navegador normal de usuario
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Verificación Te Apuesto
        try:
            print("→ Consultando Te Apuesto...")
            await page.goto("https://www.teapuesto.pe/", timeout=30000, wait_until="domcontentloaded")
            print("  ✓ Te Apuesto respondiendo.")
        except Exception as e:
            print(f"  ❌ Error en Te Apuesto: {e}")

        # Verificación Betano
        try:
            print("→ Consultando Betano...")
            await page.goto("https://www.betano.pe/", timeout=30000, wait_until="domcontentloaded")
            print("  ✓ Betano respondiendo.")
        except Exception as e:
            print(f"  ❌ Error en Betano: {e}")

        await browser.close()

    ahora = datetime.now()
    data['ultima_actualizacion'] = f"Última verificación en vivo: {ahora.strftime('%d/%m/%Y a las %H:%M')}"

    return data

def guardar_cambios(data):
    if not data:
        return

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ datos.json actualizado.")

    if not os.path.exists('historico'):
        os.makedirs('historico')
        
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    archivo_historico = f"historico/snapshot_{fecha_hoy}.json"
    
    with open(archivo_historico, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📁 Respaldo guardado en {archivo_historico}")

if __name__ == '__main__':
    datos_actualizados = asyncio.run(obtener_datos_casas())
    guardar_cambios(datos_actualizados)
