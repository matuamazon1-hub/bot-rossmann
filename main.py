import os
import time
import requests
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
    return "Bot de Rossmann (App API) activo."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 🔍 CONSULTA VÍA API MÓVIL
# ==========================================
def consultar_stock_tienda():
    # Endpoint directo de consulta de disponibilidad de la App
    url = f"https://www.rossmann.de/de/service-und-hilfe/filialfinder/api/availability/{ID_PRODUCTO}"
    
    params = {
        "zip": CODIGO_POSTAL,
        "radius": "15"  # Radio de búsqueda en km
    }
    
    # User-Agent y cabeceras simulando la aplicación Android de Rossmann
    headers = {
        "User-Agent": "RossmannApp/3.4.1 (Linux; Android 13; Mobile)",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    try:
        session = requests.Session()
        respuesta = session.get(url, headers=headers, params=params, timeout=12)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            tiendas = datos.get("stores", [])
            
            for tienda in tiendas:
                if tienda.get("available") is True or tienda.get("stock", 0) > 0:
                    nombre = tienda.get("name", "Rossmann Filiale")
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
        
        elif respuesta.status_code == 403:
            print(f"[{time.strftime('%H:%M:%S')}] Bloqueo HTTP 403. Reintentando en la siguiente ronda...", flush=True)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Estado HTTP: {respuesta.status_code}", flush=True)

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error en la petición: {e}", flush=True)

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
        consultar_stock_tienda()
        time.sleep(300)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    loop_monitoreo()
