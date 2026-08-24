import os
import time
import requests
from flask import Flask
from threading import Thread

# ==========================================
# ⚙️ CONFIGURACIÓN
# ==========================================
ID_PRODUCTO = "0196214140189"  # EAN del producto
CODIGO_POSTAL = "90419"       # PLZ (Nürnberg)
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1541378828331516006/LFZo_P_nlcuAKjHT03E_r7OGf94PkgN-hHOCV-eQTCg4Xmtrfqr0nvFjnmnzNOOrIW3Y"

app = Flask('')

@app.route('/')
def home():
    return "Bot de Rossmann activo."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 🔍 CONSULTA DE INVENTARIO FÍSICO SAFE
# ==========================================
def consultar_inventario_tienda():
    url = f"https://www.rossmann.de/de/service-und-hilfe/filialfinder/api/availability/{ID_PRODUCTO}?zip={CODIGO_POSTAL}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de-DE,de;q=0.9",
        "Referer": "https://www.rossmann.de/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        session = requests.Session()
        respuesta = session.get(url, headers=headers, timeout=10)
        
        # Validar si el contenido devuelto es realmente JSON
        if respuesta.status_code == 200 and "application/json" in respuesta.headers.get("Content-Type", ""):
            datos = respuesta.json()
            tiendas = datos.get("stores", [])
            
            tiendas_con_stock = []
            for tienda in tiendas:
                if tienda.get("available") is True or tienda.get("stock", 0) > 0:
                    nombre = tienda.get("name", "Rossmann Filiale")
                    direccion = tienda.get("street", "")
                    ciudad = tienda.get("city", "")
                    tiendas_con_stock.append(f"📍 **{nombre}**: {direccion}, {ciudad}")

            if tiendas_con_stock:
                lista = "\n".join(tiendas_con_stock)
                mensaje = (
                    f"🚨 **¡STOCK EN TIENDA FÍSICA DETECTADO!** 🚨\n\n"
                    f"**EAN:** `{ID_PRODUCTO}` | **PLZ:** `{CODIGO_POSTAL}`\n\n"
                    f"**Tiendas con unidades:**\n{lista}"
                )
                enviar_alerta_discord(mensaje)
                print(f"[{time.strftime('%H:%M:%S')}] ¡Stock encontrado!", flush=True)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Comprobado PLZ {CODIGO_POSTAL}: Sin stock en tiendas.", flush=True)

        elif respuesta.status_code == 200:
            # Caso en que la IP de Render fue desafiada con Cloudflare (devuelve HTML en vez de JSON)
            print(f"[{time.strftime('%H:%M:%S')}] Petición protegida por Cloudflare (esperando próximo ciclo)...", flush=True)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Estado HTTP: {respuesta.status_code}", flush=True)

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error temporal de red: {e}", flush=True)

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
        consultar_inventario_tienda()
        time.sleep(300)  # Revisa cada 5 minutos

if __name__ == "__main__":
    Thread(target=run_flask).start()
    loop_monitoreo()
