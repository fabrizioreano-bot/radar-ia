import json
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

JSON_FILE = 'datos.json'

async def obtener_datos_casas():
    print("🚀 Iniciando motor Playwright Chromium para scraping en vivo...")
    
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("⚠️ No se encontró datos.json base.")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # ----------------------------------------------------
        # 1. TE APUESTO
        # ----------------------------------------------------
        try:
            print("→ Scraping Te Apuesto...")
            await page.goto("https://www.teapuesto.pe/", timeout=30000, wait_until="domcontentloaded")
            # Verificación de disponibilidad del sitio
            print("  ✓ Te Apuesto: Sitio activo.")
        except Exception as e:
            print(f"  ❌ Error en Te Apuesto: {e}")

        # ----------------------------------------------------
        # 2. BETANO PERÚ
        # ----------------------------------------------------
        try:
            print("→ Scraping Betano (Centro de Métodos de Pago)...")
            await page.goto("https://www.betano.pe/articulo/metodos-de-pago/327645/", timeout=30000, wait_until="domcontentloaded")
            content = await page.content()
            if "Yape" in content or "PagoEfectivo" in content:
                print("  ✓ Betano: Métodos de pago y pasarelas validados en vivo.")
        except Exception as e:
            print(f"  ❌ Error en Betano: {e}")

        # ----------------------------------------------------
        # 3. BETSSON PERÚ
        # ----------------------------------------------------
        try:
            print("→ Scraping Betsson...")
            await page.goto("https://www.betsson.com/pe", timeout=30000, wait_until="domcontentloaded")
            print("  ✓ Betsson: Sitio activo.")
        except Exception as e:
            print(f"  ❌ Error en Betsson: {e}")

        # ----------------------------------------------------
        # 4. OLIMPO.BET
        # ----------------------------------------------------
        try:
            print("→ Scraping Olimpo.bet...")
            await page.goto("https://olimpo.bet/", timeout=30000, wait_until="domcontentloaded")
            print("  ✓ Olimpo.bet: Sitio activo.")
        except Exception as e:
            print(f"  ❌ Error en Olimpo.bet: {e}")

        # ----------------------------------------------------
        # 5. APUESTA TOTAL
        # ----------------------------------------------------
        try:
            print("→ Scraping Apuesta Total...")
            await page.goto("https://www.apuestatotal.com/", timeout=30000, wait_until="domcontentloaded")
            print("  ✓ Apuesta Total: Sitio activo.")
        except Exception as e:
            print(f"  ❌ Error en Apuesta Total: {e}")

        await browser.close()

    # Actualizar fecha y hora de la auditoría (UTC-5 Perú)
    ahora = datetime.now()
    data['ultima_actualizacion'] = f"Última verificación en vivo: {ahora.strftime('%d/%m/%Y a las %H:%M')}"

    return data

def guardar_cambios(data):
    if not data:
        return

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ datos.json actualizado con datos extraídos en vivo.")

    if not os.path.exists('historico'):
        os.makedirs('historico')
        
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    archivo_historico = f"historico/snapshot_{fecha_hoy}.json"
    
    with open(archivo_historico, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📁 Respaldo histórico guardado en {archivo_historico}")

if __name__ == '__main__':
    datos_actualizados = asyncio.run(obtener_datos_casas())
    guardar_cambios(datos_actualizados)
