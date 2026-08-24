import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# ==========================================
# ⚙️ CONFIGURACIÓN
# ==========================================
ID_PRODUCTO = "0196214140189"
CODIGO_POSTAL = "90402"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1541378828331516006/LFZo_P_nlcuAKjHT03E_r7OGf94PkgN-hHOCV-eQTCg4Xmtrfqr0nvFjnmnzNOOrIW3Y"

app = Flask('')

@app.route('/')
def home():
    return "Bot de Rossmann activo."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 🔍 COMPROBACIÓN VÍA NAVEGACIÓN WEB REAL
# ==========================================
def consultar_stock():
    # URL pública del producto en la web alemana
    url = f"https://www.rossmann.de/de/p/{ID_PRODUCTO}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    try:
        session = requests.Session()
        respuesta = session.get(url, headers=headers, timeout=15)
        
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # Buscar indicadores de falta de stock en el HTML
            texto_pagina = soup.get_text().lower()
            
            # Términos comunes de falta de stock en Rossmann
            agotado = "nicht lieferbar" in texto_pagina or "ausverkauft" in texto_pagina
            
            if not agotado:
                mensaje = (
                    f"🚨 **¡POSIBLE STOCK DETECTADO EN ROSSMANN!** 🚨\n"
                    f"**Producto:** `{ID_PRODUCTO}`\n"
                    f"**Enlace:** {url}\n"
                    f"**Estado:** Revisa la disponibilidad de recogida en tu tienda ({CODIGO_POSTAL})."
                )
                enviar_alerta_discord(mensaje)
                print(f"[{time.strftime('%H:%M:%S')}] ¡Stock o cambio de estado detectado!", flush=True)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Producto sin stock en la web.", flush=True)
        
        elif respuesta.status_code == 403:
            print(f"[{time.strftime('%H:%M:%S')}] Petición bloqueada por el servidor (HTTP 403). Reintentando en 5 min...", flush=True)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Respuesta inesperada HTTP: {respuesta.status_code}", flush=True)

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error en la consulta: {e}", flush=True)

def enviar_alerta_discord(mensaje):
    payload = {"content": mensaje}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        print(f"Error enviando a Discord: {e}", flush=True)

# ==========================================
# 🔄 BUCLE PRINCIPAL
# ==========================================
def loop_monitoreo():
    while True:
        consultar_stock()
        time.sleep(300)  # Revisa cada 5 minutos

if __name__ == "__main__":
    Thread(target=run_flask).start()
    loop_monitoreo()
