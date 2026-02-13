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

def clean_extreme(text):
    """Limpieza total de caracteres y basura web para el Lumia 830"""
    if not text: return ""
    
    # 1. Diccionario Maestro de Reparación (Vandal / GenXbox Edition)
    repairs = {
        '±Ē': 'ñ', 'ańo': 'año', 'reseńa': 'reseña', 'ańadir': 'añadir',
        'mßs': 'más', 'tĒtulo': 'título', 'tķrmino': 'término', 'compa±': 'compañ',
        '·ltimo': 'último', 'quķ': 'qué', 'asĒ': 'así', 'estķ': 'está',
        'podrĒa': 'podría', 'tambiķn': 'también', 'se±al': 'señal', 'Í': 'í',
        'þ': 'ñ', 'Õ': 'é', 'µ': 'ó', 'Ú': 'í', 'Ã': 'á', 'º': 'ú'
    }
    for broken, fixed in repairs.items():
        text = text.replace(broken, fixed)

    # 2. Eliminar restos de botones e interfaz
    basura = [
        r"PUBLICIDAD", r"Imagen", r"¡Comparte!", r"íComparte!", 
        r"íSíguenos en Google News!", r"En 3DJuegos \|.*", 
        r"En VidaExtra \|.*", r"Suscribete al canal.*"
    ]
    for patron in basura:
        text = re.sub(patron, "", text, flags=re.IGNORECASE)

    # 3. Normalizar espacios y saltos de línea
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text[:8000].strip()

def procesar_noticias():
    noticias_finales = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}

    for nombre_fuente, url_feed in FEEDS.items():
        print(f"Procesando: {nombre_fuente}")
        feed = feedparser.parse(url_feed)
        
        for entrada in feed.entries[:10]:
            try:
                r = requests.get(entrada.link, headers=headers, timeout=10)
                # Forzamos detección solo si el sitio es problemático
                if "vandal" in entrada.link or "generacionxbox" in entrada.link:
                    r.encoding = r.apparent_encoding
                else:
                    r.encoding = 'utf-8'

                article = Article(entrada.link, language='es')
                article.set_html(r.text)
                article.parse()
                
                if len(article.text) > 100:
                    noticia = {
                        "titulo": clean_extreme(article.title),
                        "fecha": entrada.get("published", "Hoy"),
                        "imagen": article.top_image,
                        "resumen": clean_extreme(article.text),
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                
                time.sleep(0.2)
            except:
                continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print(f"Hecho: {len(noticias_finales)} noticias listas.")

if __name__ == "__main__":
    procesar_noticias()
