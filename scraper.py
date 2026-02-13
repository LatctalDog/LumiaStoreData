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

def clean_text_expert(text):
    """Limpieza profunda de texto y caracteres para el Lumia"""
    if not text: return ""
    
    # 1. Eliminar frases basura recurrentes
    basura = [
        r"íComparte!", r"íSíguenos en Google News!", r"PUBLICIDAD",
        r"Más historias en la categoría.*", r"Imagen", r"En 3DJuegos \|.*",
        r"En VidaExtra \|.*", r"Descargar", r"Suscribete al canal de.*"
    ]
    for patron in basura:
        text = re.sub(patron, "", text, flags=re.IGNORECASE)

    # 2. Corregir saltos de línea triples y espacios
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 3. Límite de seguridad (8000 caracteres es el punto dulce para un Lumia 830)
    # Es suficiente para noticias completas sin colapsar la RAM del móvil.
    return text[:8000].strip()

def procesar_noticias():
    noticias_finales = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

    print("--- Iniciando Extracción de Alta Calidad ---")

    for nombre_fuente, url_feed in FEEDS.items():
        print(f"Sincronizando: {nombre_fuente}")
        feed = feedparser.parse(url_feed)
        
        for entrada in feed.entries[:10]:
            try:
                # Descarga inteligente
                r = requests.get(entrada.link, headers=headers, timeout=10)
                
                # Si es Vandal o GenXbox, forzamos detección de encoding
                if "vandal" in entrada.link or "generacionxbox" in entrada.link:
                    r.encoding = r.apparent_encoding
                else:
                    r.encoding = 'utf-8'

                article = Article(entrada.link, language='es')
                article.set_html(r.text)
                article.parse()
                
                if len(article.text) > 100:
                    # Aplicamos limpieza experta
                    titulo = clean_text_expert(article.title)
                    resumen = clean_text_expert(article.text)

                    noticia = {
                        "titulo": titulo,
                        "fecha": entrada.get("published", "Reciente"),
                        "imagen": article.top_image,
                        "resumen": resumen,
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                    print(f"  OK: {titulo[:45]}...")
                
                time.sleep(0.3)
            except Exception as e:
                print(f"  Error en {nombre_fuente}: {e}")
                continue

    # Guardar JSON final
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    
    print(f"\n¡Listo! {len(noticias_finales)} noticias procesadas sin errores.")

if __name__ == "__main__":
    procesar_noticias()
