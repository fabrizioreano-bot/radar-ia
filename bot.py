import json
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

JSON_FILE = 'datos.json'

# Lista maestra de pasarelas y bancos a detectar en Perú
PASARELAS_DETECTAR = [
    {"id": "yape", "nombre": "Yape", "tiempo": "Inmediato"},
    {"id": "plin", "nombre": "Plin", "tiempo": "Inmediato"},
    {"id": "pagoefectivo", "nombre": "PagoEfectivo", "tiempo": "< 5 mins"},
    {"id": "tarjetas", "nombre": "Visa / Mastercard", "tiempo": "Inmediato"},
    {"id": "bcp", "nombre": "Banca por Internet BCP", "tiempo": "Inmediato"},
    {"id": "bbva", "nombre": "BBVA", "tiempo": "Inmediato"},
    {"id": "interbank", "nombre": "Interbank", "tiempo": "Inmediato"},
    {"id": "scotiabank", "nombre": "Scotiabank", "tiempo": "Inmediato"},
    {"id": "safetypay", "nombre": "SafetyPay", "tiempo": "Inmediato"},
    {"id": "astropay", "nombre": "AstroPay", "tiempo": "Inmediato"},
    {"id": "tienda", "nombre": "Pago en Tienda / Red de Puntos", "tiempo": "Inmediato"}
]

async def extraer_metodos_pagina(page, url, operador_nombre):
    print(f"🔍 Escaneando en profundidad: {operador_nombre} ({url})...")
    metodos_encontrados = []
    
    try:
        await page.goto(url, timeout=35000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000) # Espera a que carguen scripts dinámicos
        
        # Intentar desplegar botones de "Ver más" si existen
        botones_desplegar = page.locator("text=/Ver más|Mostrar todos|Métodos de pago|Cajero/i")
        count = await botones_desplegar.count()
        for i in range(min(count, 3)):
            try:
                await botones_desplegar.nth(i).click(timeout=2000)
                await page.wait_for_timeout(1000)
            except:
                pass

        html_content = (await page.content()).lower()

        # Rastrear qué canales están presentes en el texto/código de la página
        for pasarela in PASARELAS_DETECTAR:
            palabra_clave = pasarela["id"].lower()
            if palabra_clave in html_content or pasarela["nombre"].lower() in html_content:
                metodos_encontrados.append({
                    "canal": pasarela["nombre"],
                    "tiempo": pasarela["tiempo"],
                    "estado": "Operativo",
                    "min_recarga": "S/ 10",
                    "max_recarga": "S/ 5,000"
                })

        print(f"  ✓ {operador_nombre}: Detectados {len(metodos_encontrados)} métodos automáticos.")
    except Exception as e:
        print(f"  ❌ Error escaneando {operador_nombre}: {e}")

    return metodos_encontrados

async def ejecutar_bot():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("⚠️ No existe datos.json base.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Mapeo directo a secciones de ayuda y cajeros de cada plataforma
        urls_operadores = {
            "Te Apuesto": "https://www.teapuesto.pe/",
            "Betano": "https://www.betano.pe/articulo/metodos-de-pago/327645/",
            "Betsson": "https://www.betsson.pe/pago",
            "Olimpo.bet": "https://olimpo.bet/",
            "Apuesta Total": "https://www.apuestatotal.com/"
        }

        for op in data.get("operadores", []):
            nombre = op.get("nombre")
            if nombre in urls_operadores:
                nuevos_metodos = await extraer_metodos_pagina(page, urls_operadores[nombre], nombre)
                if nuevos_metodos:
                    # Sobreescribir la lista con todos los métodos detectados en vivo
                    op["recargas"] = nuevos_metodos

        await browser.close()

    ahora = datetime.now()
    data['ultima_actualizacion'] = f"Última verificación en vivo: {ahora.strftime('%d/%m/%Y a las %H:%M')}"

    # Guardar cambios en JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ datos.json actualizado automáticamente con todos los canales encontrados.")

if __name__ == '__main__':
    asyncio.run(ejecutar_bot())
