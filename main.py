import os
import time
import cloudscraper
from flask import Flask
from threading import Thread

# ==========================================
# ⚙️ CONFIGURACIÓN DE BÚSQUEDA
# ==========================================
# Código EAN de 13 dígitos del producto de Pokémon
ID_PRODUCTO = "0196214140189"  

# Código Postal (PLZ) de la ciudad donde quieres buscar tiendas físicas
CODIGO_POSTAL = "90419"       

# Tu Webhook de Discord
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1541378828331516006/LFZo_P_nlcuAKjHT03E_r7OGf94PkgN-hHOCV-eQTCg4Xmtrfqr0nvFjnmnzNOOrIW3Y"

# Servidor básico para mantener Render activo
app = Flask('')

@app.route('/')
def home():
    return "Bot de Inventario Físico de Tiendas Rossmann Activo."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 🔍 CONSULTA DE INVENTARIO FÍSICO INTERNO
# ==========================================
def consultar_inventario_tienda():
    # API interna del buscador de filiales / inventario físico
    url = f"https://www.rossmann.de/de/service-und-hilfe/filialfinder/api/availability/{ID_PRODUCTO}?zip={CODIGO_POSTAL}"
    
    # Creamos sesión con Cloudscraper para simular la app oficial
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )

    try:
        respuesta = scraper.get(url, timeout=12)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            tiendas = datos.get("stores", [])
            
            tiendas_con_stock = []

            for tienda in tiendas:
                # Comprobar si la pistola de la tienda marca disponible (True o cantidad > 0)
                if tienda.get("available") is True or tienda.get("stock", 0) > 0:
                    nombre = tienda.get("name", "Rossmann Filiale")
                    direccion = tienda.get("street", "")
                    ciudad = tienda.get("city", "")
                    unidades = tienda.get("stock", "Disponible")
                    
                    tiendas_con_stock.append(
                        f"📍 **{nombre}**\n"
                        f"   └ Dirección: {direccion}, {ciudad}\n"
                        f"   └ Stock reportado: `{unidades}`"
                    )

            # SI HAY TIENDAS CON STOCK -> AVISAR A DISCORD
            if tiendas_con_stock:
                lista_detallada = "\n\n".join(tiendas_con_stock)
                mensaje = (
                    f"🚨 **¡CARTAS DE PÓKEMON DETECTADAS EN TIENDA FÍSICA!** 🚨\n\n"
                    f"**EAN del producto:** `{ID_PRODUCTO}`\n"
                    f"**Código Postal (PLZ):** `{CODIGO_POSTAL}`\n\n"
                    f"**Tiendas físicas que las tienen físicas en el estante:**\n"
                    f"{lista_detallada}\n\n"
                    f"⚡ *Corre a la tienda física antes de que las compren.*"
                )
                enviar_alerta_discord(mensaje)
                print(f"[{time.strftime('%H:%M:%S')}] ¡INVENTARIO ENCONTRADO EN TIENDA FÍSICA!", flush=True)
                return True
            else:
                # SI NO HAY STOCK -> SILENCIO TOTAL EN DISCORD (solo log interno)
                print(f"[{time.strftime('%H:%M:%S')}] Comprobado inventario PLZ {CODIGO_POSTAL}: Sin unidades en las estanterías de las tiendas de la zona.", flush=True)
        
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Servidor de inventario respondió con estado HTTP: {respuesta.status_code}", flush=True)

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error al consultar inventario: {e}", flush=True)

def enviar_alerta_discord(mensaje):
    payload = {"content": mensaje}
    try:
        scraper = cloudscraper.create_scraper()
        scraper.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        print(f"Error enviando notificación a Discord: {e}", flush=True)

# ==========================================
# 🔄 BUCLE DE MONITOREO
# ==========================================
def loop_monitoreo():
    while True:
        consultar_inventario_tienda()
        time.sleep(300)  # Consulta cada 5 minutos

if __name__ == "__main__":
    Thread(target=run_flask).start()
    loop_monitoreo()
