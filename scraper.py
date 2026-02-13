import json
import feedparser
import requests
from newspaper import Article
import time

# Fuentes de noticias
FEEDS = {
    "3DJuegos": "https://www.3djuegos.com/feedburner.xml",
    "VidaExtra": "https://www.vidaextra.com/feedburner.xml",
    "Eurogamer": "https://www.eurogamer.es/feed",
    "Generación Xbox": "https://generacionxbox.com/feed/",
    "Vandal": "https://vandal.elespanol.com/xml.cgi"
}

def fix_encoding(text):
    """Repara errores comunes de codificación en sitios españoles"""
    if not text: return ""
    try:
        # Intenta reparar el error de UTF-8 interpretado como Latin-1
        return text.encode('latin-1').decode('utf-8')
    except:
        return text

def procesar_noticias():
    noticias_finales = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    print("--- Iniciando extracción optimizada para Lumia ---")

    for nombre_fuente, url_feed in FEEDS.items():
        print(f"Procesando: {nombre_fuente}")
        feed = feedparser.parse(url_feed)
        
        for entrada in feed.entries[:8]:
            try:
                # Usamos requests para descargar el HTML y detectar el encoding real
                response = requests.get(entrada.link, headers=headers, timeout=10)
                response.encoding = response.apparent_encoding # <--- AQUÍ SE ARREGLAN LOS CARACTERES
                
                article = Article(entrada.link, language='es')
                article.set_html(response.text)
                article.parse()
                
                if len(article.text) > 100:
                    # Arreglamos posibles restos de caracteres raros en título y texto
                    titulo_limpio = fix_encoding(article.title.strip())
                    # Aumentamos el límite a 2500 caracteres para el Lumia
                    texto_limpio = fix_encoding(article.text[:2500].strip())

                    noticia = {
                        "titulo": titulo_limpio,
                        "fecha": entrada.get("published", "Reciente"),
                        "imagen": article.top_image,
                        "resumen": texto_limpio + ("..." if len(article.text) > 2500 else ""),
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                    print(f"  OK: {titulo_limpio[:50]}...")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  Error en {entrada.link}: {e}")
                continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    
    print(f"\nFinalizado: {len(noticias_finales)} noticias procesadas.")

if __name__ == "__main__":
    procesar_noticias()
