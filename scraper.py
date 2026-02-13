import json
import feedparser
from newspaper import Article
import time

# Configuración de fuentes
FEEDS = {
    "3DJuegos": "https://www.3djuegos.com/feedburner.xml",
    "VidaExtra": "https://www.vidaextra.com/feedburner.xml",
    "Eurogamer": "https://www.eurogamer.es/feed",
    "Generación Xbox": "https://generacionxbox.com/feed/",
    "Vandal": "https://vandal.elespanol.com/xml.cgi"
}

def clean_text(text):
    """Limpia el texto para que el Lumia no sufra con caracteres extraños"""
    if not text:
        return ""
    # Limitamos a 1200 caracteres para no saturar la RAM del 830
    return text[:1200].replace('\n', ' ').strip() + "..."

def procesar_noticias():
    noticias_finales = []
    print("Iniciando extracción de noticias...")

    for nombre_fuente, url_feed in FEEDS.items():
        print(f"Procesando: {nombre_fuente}")
        feed = feedparser.parse(url_feed)
        
        # Tomamos las 8 noticias más recientes de cada medio
        for entrada in feed.entries[:8]:
            try:
                # Configuramos la extracción del artículo
                article = Article(entrada.link, language='es')
                article.download()
                article.parse()
                
                # Solo agregamos si hay contenido real
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
                    print(f"  - OK: {article.title[:40]}...")
                
                # Pequeña pausa para no saturar los servidores de los medios
                time.sleep(1)
                
            except Exception as e:
                print(f"  - Error en {entrada.link}: {e}")
                continue

    # Guardar el resultado final
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    
    print(f"\nProceso terminado. Se guardaron {len(noticias_finales)} noticias.")

if __name__ == "__main__":
    procesar_noticias()
