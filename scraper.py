import json
import feedparser
import requests
from newspaper import Article
import time
import re

FEEDS = {
    "3DJuegos": "https://www.3djuegos.com/feedburner.xml",
    "VidaExtra": "https://www.vidaextra.com/feedburner.xml",
    "Eurogamer": "https://www.eurogamer.es/feed",
    "Generación Xbox": "https://generacionxbox.com/feed/",
    "Vandal": "https://vandal.elespanol.com/xml.cgi"
}

def clean_content(text):
    """Limpia basura publicitaria y errores de codificación"""
    if not text: return ""
    
    # 1. Reparación de caracteres rotos (Específico para Vandal/Generación Xbox)
    repairs = {
        'þ': 'ñ', 'Õ': 'é', 'µ': 'ó', 'Ú': 'í', 'Ã': 'á', 'º': 'ú',
        'þ': 'ñ', 'ń': 'ñ', 'è': 'é', 'ê': 'á', 'à': 'á', '¡': 'í'
    }
    for broken, fixed in repairs.items():
        text = text.replace(broken, fixed)

    # 2. Quitar restos de la web
    text = re.sub(r'PUBLICIDAD', '', text)
    text = re.sub(r'En 3DJuegos \|.*', '', text)
    text = re.sub(r'En VidaExtra \|.*', '', text)
    
    # 3. Límite de seguridad para RAM del Lumia (5000 es seguro)
    return text[:5000].strip()

def procesar_noticias():
    noticias_finales = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

    print("--- Extracción Definitiva para Windows 10 Mobile ---")

    for nombre_fuente, url_feed in FEEDS.items():
        print(f"Sincronizando: {nombre_fuente}")
        feed = feedparser.parse(url_feed)
        
        for entrada in feed.entries[:10]: # Subimos a 10 por medio
            try:
                # Descarga con detección forzada de UTF-8
                r = requests.get(entrada.link, headers=headers, timeout=10)
                r.encoding = 'utf-8' 
                
                article = Article(entrada.link, language='es')
                article.set_html(r.text)
                article.parse()
                
                if len(article.text) > 100:
                    noticia = {
                        "titulo": clean_content(article.title),
                        "fecha": entrada.get("published", "Hoy"),
                        "imagen": article.top_image,
                        "resumen": clean_content(article.text),
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                    print(f"  + {noticia['titulo'][:40]}...")
                
                time.sleep(0.3)
            except:
                continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    
    print(f"\nFinalizado: {len(noticias_finales)} noticias listas para el Lumia.")

if __name__ == "__main__":
    procesar_noticias()
