import requests

# ID del producto de Pokémon y tu Código Postal en Alemania
PRODUCT_ID = "0196214140189"  
PLZ = "90419"                 

def comprobar_stock_filial():
    # URL interna de Rossmann para consultar disponibilidad por tienda/código postal
    url = f"https://www.rossmann.de/de/service-und-hilfe/filialfinder/api/availability/{PRODUCT_ID}?zip={PLZ}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        
        # Si la respuesta devuelve tiendas con stock > 0
        for tienda in data.get("stores", []):
            if tienda.get("available") == True:
                nombre_tienda = tienda.get("name")
                enviar_alerta_discord(f"¡Hay stock de Pokémon en la tienda: {nombre_tienda} ({PLZ})!")
    except Exception as e:
        print(f"Buscando en tiendas físicas... {e}")
