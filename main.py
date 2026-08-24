import os
import time
import requests
from flask import Flask
from threading import Thread

# ==========================================
# ⚙️ CONFIGURACIÓN (SUSTITUYE ESTOS DATOS)
# ==========================================
ID_PRODUCTO = "0196214140189"  # ID o EAN de 13 dígitos del producto
CODIGO_POSTAL = "90402"       # Código postal (PLZ) de la zona a buscar
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1541378828331516006/LFZo_P_nlcuAKjHT03E_r7OGf94PkgN-hHOCV-eQTCg4Xmtrfqr0nvFjnmnzNOOrIW3Y"  # Tu Webhook de Discord

# Servidor Flask básico para que Render no suspenda el servicio gratis
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            tiendas = datos.get("stores", [])
            
            # Recorrer las tiendas cercanas devueltas por la API
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
                    print(f"[!] Stock detectado en: {nombre}")
                    return True

            print(f"[{time.strftime('%H:%M:%S')}] Sin stock en el código postal {CODIGO_POSTAL}.")
        else:
            print(f"Error HTTP {respuesta.status_code} al consultar la API.")

    except Exception as e:
        print(f"Error de conexión: {e}")

def enviar_alerta_discord(mensaje):
    payload = {"content": mensaje}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Error enviando mensaje a Discord: {e}")

# ==========================================
# 🔄 BUCLE PRINCIPAL
# ==========================================
def loop_monitoreo():
    while True:
        consultar_stock_tienda()
        time.sleep(300)  # Revisa cada 5 minutos (300 segundos)

if __name__ == "__main__":
    # Iniciar el servidor web en un hilo secundario
    Thread(target=run_flask).start()
    # Iniciar el monitor de stock en el hilo principal
    loop_monitoreo()
