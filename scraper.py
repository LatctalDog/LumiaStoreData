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

def clean_news_final(text):
    if not text: return ""
    
    # 1. TRADUCCIÓN MAESTRA (Vandal, GenXbox y tildes perdidas)
    repairs = {
        'ń': 'ñ', '±': 'ñ', '¾': 'ó', 'ķ': 'é', '·': 'ú', 'ß': 'á', 
        'Ē': 'í', '┴': 'Á', '╔': 'É', 'ańo': 'año', 'ú PC': '| PC',
        'íL': '¡L', 'íS': '¡S', 'íC': '¡C'
    }
    for broken, fixed in repairs.items():
        text = text.replace(broken, fixed)

    # 2. LIMPIEZA DE BLOQUES (Borra los enlaces del final de 3DJ/VidaExtra)
    text = re.sub(r'En 3DJuegos \|.*', '', text, flags=re.DOTALL)
    text = re.sub(r'En VidaExtra \|.*', '', text, flags=re.DOTALL)
    
    # 3. FRASES BASURA (Solo frases exactas de botones, no palabras sueltas)
    basura = [
        r"Imagen principal de 3DJuegos",
        r"¡Síguenos en Google News!",
        r"No te pierdas nada y",
        r"PUBLICIDAD",
        r"Más historias en la categoría Slider",
        r"Suscribete al canal de.*"
    ]
    for patron in basura:
        text = re.sub(patron, "", text, flags=re.IGNORECASE)

    # 4. NORMALIZACIÓN
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
                # Detección de encoding inteligente
                r.encoding = r.apparent_encoding if "vandal" in entrada.link or "generacion" in entrada.link else 'utf-8'

                article = Article(entrada.link, language='es')
                article.set_html(r.text)
                article.parse()
                
                if len(article.text) > 100:
                    noticia = {
                        "titulo": clean_news_final(article.title),
                        "fecha": entrada.get("published", "Hoy"),
                        "imagen": article.top_image,
                        "resumen": clean_news_final(article.text),
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                
                time.sleep(0.1)
            except:
                continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print("¡Proceso completado!")

if __name__ == "__main__":
    procesar_noticias()
