import json
import feedparser
import requests
from newspaper import Article
import time
import re
import os

def procesar_noticias():
    # CARGAR FUENTES DESDE EL JSON
    if not os.path.exists('sources.json'):
        print("Error: No existe sources.json")
        return

    with open('sources.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        FEEDS = data['fuentes']

    noticias_finales = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}

    # FEEDS ahora es una lista de diccionarios [{'nombre': '...', 'url': '...'}]
    for fuente in FEEDS:
        nombre_fuente = fuente['nombre']
        url_feed = fuente['url']
        print(f"Sincronizando: {nombre_fuente}")
        
        feed = feedparser.parse(url_feed)
        # ... (el resto del código del scraper que ya tenemos, usando nombre_fuente y url_feed)
