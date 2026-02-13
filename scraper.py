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

def fix_mojibake(text):
    """Corrige los símbolos raros específicos de Vandal y GenXbox"""
    if not text: return ""
    translations = {
        '¾': 'ó', 'ķ': 'é', '·': 'ú', 'ß': 'á', 'Ē': 'í', 
        '±': 'ñ', 'ańo': 'año', 'reseńa': 'reseña', 'ańadir': 'añadir',
        'íLo ': '¡Lo ', 'íComparte': '¡Comparte', 'íSíguenos': '¡Síguenos'
    }
    for broken, fixed in translations.items():
        text = text.replace(broken, fixed)
    return text

def clean_content_safe(text):
    """Limpia basura sin romper la gramática de las noticias"""
    if not text: return ""
    
    # 1. Borrar frases de interfaz (solo frases enteras)
    basura = [
        r"Imagen principal de 3DJuegos",
        r"¡Síguenos en Google News!",
        r"¡Comparte!",
        r"PUBLICIDAD",
        r"Más historias en la categoría Slider",
        r"Suscribete al canal de Generación Xbox Suscríbirse"
    ]
    for patron in basura:
        text = re.sub(patron, "", text, flags=re.IGNORECASE)

    # 2. Arreglar caracteres y espacios
    text = fix_mojibake(text)
    text = re.sub(r' +', ' ', text) # Quitar espacios dobles
    text = re.sub(r'\n{3,}', '\n\n', text) # Máximo 2 saltos de línea
    
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
                
                # Dejamos que el sistema decida el encoding si es Vandal/GenXbox
                if "vandal" in entrada.link or "generacion" in entrada.link:
                    r.encoding = r.apparent_encoding
                else:
                    r.encoding = 'utf-8'

                article = Article(entrada.link, language='es')
                article.set_html(r.text)
                article.parse()
                
                if len(article.text) > 100:
                    noticia = {
                        "titulo": clean_content_safe(article.title),
                        "fecha": entrada.get("published", "Reciente"),
                        "imagen": article.top_image,
                        "resumen": clean_content_safe(article.text),
                        "fuente": nombre_fuente,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                    print(f"  OK: {noticia['titulo'][:40]}...")
                
                time.sleep(0.2)
            except:
                continue

    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    print(f"Finalizado: {len(noticias_finales)} noticias listas.")

if __name__ == "__main__":
    procesar_noticias()
