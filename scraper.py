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

def clean_final_gold(text):
    if not text: return ""
    
    # 1. TRADUCCIÓN MAESTRA (Incluye mayúsculas raras de Vandal)
    repairs = {
        '┴': 'Á', '╔': 'É', '¾': 'ó', 'ķ': 'é', '·': 'ú', 'ß': 'á', 
        'Ē': 'í', '±': 'ñ', 'ń': 'ñ', 'ańo': 'año', 'reseńa': 'reseña'
    }
    for broken, fixed in repairs.items():
        text = text.replace(broken, fixed)

    # 2. LIMPIEZA QUIRÚRGICA (Borra los bloques de enlaces finales)
    text = re.sub(r'En 3DJuegos \|.*', '', text, flags=re.DOTALL)
    text = re.sub(r'En VidaExtra \|.*', '', text, flags=re.DOTALL)
    
    basura_frases = [
        r"Imagen principal de 3DJuegos",
        r"íSíguenos en Google News!",
        r"No te pierdas nada y",
        r"PUBLICIDAD",
        r"Más historias en la categoría.*",
        r"Suscribete al canal de.*"
    ]
    for patron in basura_frases:
        text = re.sub(patron, "", text, flags=re.IGNORECASE)

    # 3. ESPACIADO
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text[:8000].strip()

def procesar_noticias():
    noticias_finales = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}

    for nombre_fuente, url_feed in FEEDS.items():
        print(f"Sincronizando: {nombre_fuente}")
        feed = feedparser.parse(url_feed)
        
        for entrada in feed.entries[:10]:
            try:
                r = requests.get(entrada.link, headers=headers, timeout=10)
                r.encoding = r.apparent_encoding if "vandal" in entrada.link or "generacion" in entrada.link else 'utf-8'

                article = Article(entrada.link, language='es')
                article.set_html(r.text)
                article.parse()
                
                if len(article.text) > 100:
                    noticia = {
                        "titulo": clean_final_gold(article.title),
                        "fecha": entrada.get("published", "Reciente"),
                        "imagen": article.top_image,
                        "resumen": clean_final_gold(article.text),
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                time.sleep(0.1)
            except:
                continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print("Sincronización terminada.")

if __name__ == "__main__":
    procesar_noticias()
