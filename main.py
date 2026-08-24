Python
import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# Sustituye tus datos entre las comillas
URL_PRODUCTO = "https://www.rossmann.de/de/ideenwelt-amigo-pokemon-tcg-wachsendes-chaos-3-booster-blister/p/0196214140189"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1541378828331516006/LFZo_P_nlcuAKjHT03E_r7OGf94PkgN-hHOCV-eQTCg4Xmtrfqr0nvFjnmnzNOOrIW3Y"

app = Flask('')

@app.route('/')
def home():
    return "Bot de Rossmann activo."

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def comprobar_stock():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        respuesta = requests.get(URL_PRODUCTO, headers=headers)
        if respuesta.status_code == 200:
            if "ausverkauft" not in respuesta.text.lower():
                requests.post(DISCORD_WEBHOOK, json={"content": f"🚨 **¡STOCK EN ROSSMANN!**\n{URL_PRODUCTO}"})
    except Exception as e:
        print(f"Error: {e}")

def loop():
    while True:
        comprobar_stock()
        time.sleep(300) # Revisa cada 5 minutos

if __name__ == "__main__":
    Thread(target=run).start()
    loop()
