import os
import time
import requests
from flask import Flask
from threading import Thread

# ==========================================
# ⚙️ CONFIGURACIÓN
# ==========================================
ID_PRODUCTO = "0196214140189"  # ID o EAN del producto
CODIGO_POSTAL = "90402"       # Código postal (PLZ) en Alemania
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1541378828331516006/LFZo_P_nlcuAKjHT03E_r7OGf94PkgN-hHOCV-eQTCg4Xmtrfqr0nvFjnmnzNOOrIW3Y"

app = Flask('')

@app.route('/')
def home():
    return "Bot de Rossmann (Stock Físico) activo."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 🔍 LÓGICA DE COMPROBACIÓN DE STOCK
# ==========================================
def consultar_stock_tienda():
    url = f"https://www.rossmann.de/de/service-und-hilfe/filialfinder/api/availability/{ID_PRODUCTO}?zip={CODIGO_POSTAL}"
    
    # Cabeceras avanzadas para evitar bloqueos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.rossmann.de/de/service-und-hilfe/filialfinder.html"
    }

    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        
        if respuesta.status_code == 200:
            try:
                datos = respuesta.json()
            except ValueError:
                print(f"[{time.strftime('%H:%M:%S')}] La web ha bloqueado la consulta temporalmente (Respuesta no-JSON).", flush=True)
                return

            tiendas = datos.get("stores", [])
            
            for tienda in tiendas:
                if tienda.get("available") is True:
                    nombre = tienda.get("name", "Tienda Rossmann")
                    direccion = tienda.get("street", "")
                    ciudad = tienda.get("city", "")
                    
                    mensaje = (
                        f"🚨 **¡STOCK EN TIENDA FÍSICA ROSSMANN!** 🚨\n"
                        f"**Producto ID:** `{ID_PRODUCTO}`\n"
                        f"**Tienda:** {nombre}\n"
                        f"**Ubicación:** {direccion}, {ciudad} ({CODIGO_POSTAL})\n"
                        f"**Estado:** ¡Disponible para recoger!"
                    )
                    
                    enviar_alerta_discord(mensaje)
                    print(f"[!] Stock detectado en: {nombre}", flush=True)
                    return True

            print(f"[{time.strftime('%H:%M:%S')}] Sin stock en el código postal {CODIGO_POSTAL}.", flush=True)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Error HTTP {respuesta.status_code} al consultar la API.", flush=True)

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error de conexión: {e}", flush=True)

def enviar_alerta_discord(mensaje):
    payload = {"content": mensaje}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Error enviando mensaje a Discord: {e}", flush=True)

# ==========================================
# 🔄 BUCLE PRINCIPAL
# ==========================================
def loop_monitoreo():
    while True:
        consultar_stock_tienda()
        time.sleep(300)  # Revisa cada 5 minutos

if __name__ == "__main__":
    Thread(target=run_flask).start()
    loop_monitoreo()
