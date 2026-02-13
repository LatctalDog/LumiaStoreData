import json
import feedparser
from newspaper import Article
import time

# Tus fuentes de noticias de videojuegos
FEEDS = {
    "3DJuegos": "https://www.3djuegos.com/feedburner.xml",
    "VidaExtra": "https://www.vidaextra.com/feedburner.xml",
    "Eurogamer": "https://www.eurogamer.es/feed",
    "Generación Xbox": "https://generacionxbox.com/feed/",
    "Vandal": "https://vandal.elespanol.com/xml.cgi"
}

def clean_text(text):
    """Limpia y acorta el texto para el Lumia 830"""
    if not text:
        return ""
    # 1200 caracteres es ideal para leer sin saturar la RAM del móvil
    return text[:1200].strip() + "..."

def procesar_noticias():
    noticias_finales = []
    print("--- Iniciando extracción para Lumia ---")

    for nombre_fuente, url_feed in FEEDS.items():
        print(f"Leyendo: {nombre_fuente}")
        feed = feedparser.parse(url_feed)
        
        # Tomamos las 8 más recientes de cada uno
        for entrada in feed.entries[:8]:
            try:
                article = Article(entrada.link, language='es')
                article.download()
                article.parse()
                
                if len(article.text) > 100:
                    noticia = {
                        "titulo": article.title.strip(),
                        "fecha": entrada.get("published", "Reciente"),
                        "imagen": article.top_image,
                        "resumen": clean_text(article.text),
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                    print(f"  OK: {article.title[:50]}...")
                
                time.sleep(0.5) # Pausa técnica
                
            except Exception as e:
                print(f"  Error en {entrada.link}: {e}")
                continue

    # Guardar el archivo JSON final
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    
    print(f"\n¡Éxito! {len(noticias_finales)} noticias listas para el Lumia.")

if __name__ == "__main__":
    procesar_noticias()
