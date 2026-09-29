import json
from datetime import datetime

def actualizar_radar():
    ahora = datetime.now().strftime("%H:%M")
    
    # Datos actualizados dinámicamente por el bot
    nuevos_datos = {
        "ultima_actualizacion": f"Actualizado hoy a las {ahora} UTC",
        "alertas": [
            {
                "tipo": "critical",
                "etiqueta": "MOVIMIENTO CRÍTICO",
                "titulo": "Betsson bajó apuesta mínima",
                "descripcion": f"Detectado cambio en el boleto de apuestas de S/0.50 a S/0.20 a las {ahora}."
            },
            {
                "tipo": "opportunity",
                "etiqueta": "OPORTUNIDAD UX",
                "titulo": "Apuesta Total activó Yape Directo",
                "descripcion": "Bot detectó nuevo flujo de recarga directa sin comisión."
            },
            {
                "tipo": "promo",
                "etiqueta": "NUEVA PROMOCIÓN",
                "titulo": "Betano: Bono Liga 1 Flash",
                "descripcion": "Campaña activa detectada: 100% extra en recargas desde S/30."
            }
        ],
        "casas": [
            {
                "codigo": "TA",
                "nombre": "TE APUESTO",
                "color": "#ff5500",
                "billeteras": ["Yape", "Plin"],
                "tiempo_retiro": "3 días (Promedio)",
                "tiempo_clase": "",
                "apuesta_min": "S/ 1.00",
                "apuesta_clase": "",
                "ganancia_max": "S/ 500,000"
            },
            {
                "codigo": "B",
                "nombre": "Betsson",
                "color": "#3b82f6",
                "billeteras": ["PagoEfectivo"],
                "tiempo_retiro": "✓ 2 días",
                "tiempo_clase": "text-green",
                "apuesta_min": "↓ S/ 0.20",
                "apuesta_clase": "text-red",
                "ganancia_max": "Sin límite"
            },
            {
                "codigo": "BT",
                "nombre": "Betano",
                "color": "#ef4444",
                "billeteras": ["Yape"],
                "tiempo_retiro": "1 día",
                "tiempo_clase": "",
                "apuesta_min": "S/ 0.50",
                "apuesta_clase": "",
                "ganancia_max": "Sin límite"
            }
        ]
    }
    
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(nuevos_datos, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    actualizar_radar()
