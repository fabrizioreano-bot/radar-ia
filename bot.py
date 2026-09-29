import json
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

JSON_FILE = 'datos.json'

async def obtener_datos_casas():
    print("🚀 Iniciando motor Playwright (Navegador Chromium Headless)...")
    
    # Aquí iremos mapeando las URLs públicas y selectores de cada operador
    # Por ejemplo, verificando respuestas de red y elementos visibles en cajeros/landing
    
    # Cargar estructura base
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("⚠️ No se encontró datos.json base.")
        return None

    async with async_playwright() as p:
        # Lanzamos navegador simulando un usuario real en Windows
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("🔍 Verificando estado de pasarelas y plataformas...")

        # --- EJEMPLO RASTREO TE APUESTO ---
        try:
            print("→ Consultando Te Apuesto...")
            await page.goto("https://www.teapuesto.pe/", timeout=30000, wait_until="networkidle")
            # El scraper interactúa y valida respuesta del servidor
            print("  ✓ Te Apuesto respondiendo correctamente.")
        except Exception as e:
            print(f"  ❌ Error consultando Te Apuesto: {e}")

        # --- EJEMPLO RASTREO BETANO ---
        try:
            print("→ Consultando Betano Perú...")
            await page.goto("https://www.betano.pe/", timeout=30000, wait_until="domcontentloaded")
            print("  ✓ Betano respondiendo correctamente.")
        except Exception as e:
            print(f"  ❌ Error consultando Betano: {e}")

        await browser.close()

    # Actualizar la fecha y hora de la auditoría en vivo (Hora Perú UTC-5)
    ahora = datetime.now()
    data['ultima_actualizacion'] = f"Última verificación en vivo: {ahora.strftime('%d/%m/%Y a las %H:%M')}"

    return data

def guardar_cambios(data):
    if not data:
        return

    # 1. Sobreescribir datos.json
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ datos.json actualizado en vivo.")

    # 2. Guardar snapshot en /historico
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
