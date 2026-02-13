import json
import newspaper # Librería para extraer contenido
import feedparser # Para leer tus links actuales

# Lista de tus fuentes RSS actuales
FEEDS = [
    "https://www.clarin.com/rss/lo-ultimo/",
    "https://elpais.com/rss/elpais/portada.xml"
]

def procesar_noticias():
    lista_final = []
    
    for url_feed in FEEDS:
        d = feedparser.parse(url_feed)
        # Solo tomamos las 10 últimas de cada medio para no saturar al Lumia
        for entry in d.entries[:10]:
            try:
                # Aquí ocurre la magia: extrae el contenido real del link
                article = newspaper.Article(entry.link)
                article.download()
                article.parse()
                
                noticia = {
                    "titulo": article.title,
                    "fecha": entry.get("published", ""),
                    "imagen": article.top_image,
                    "resumen": article.text[:1000], # Limitamos caracteres para ahorrar RAM
                    "fuente": d.feed.title
                }
                lista_final.append(noticia)
            except:
                continue 

    # Guardamos el resultado en el JSON que leerá el Lumia
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    procesar_noticias()
