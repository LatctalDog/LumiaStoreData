import json
import feedparser
import requests
from newspaper import Article
import time
import re
import os

# Configuración de limpieza (Diccionario Maestro)
def clean_ultimate(text):
    if not text: return ""
    repairs = {
        'ń': 'ñ', '±': 'ñ', '¾': 'ó', 'ķ': 'é', '·': 'ú', 'ß': 'á', 
        'Ē': 'í', 'íL': '¡L', 'íS': '¡S', 'íC': '¡C', 'ańo': 'año'
    }
    for broken, fixed in repairs.items():
        text = text.replace(broken, fixed)

    text = re.sub(r'En 3DJuegos \|.*', '', text, flags=re.DOTALL)
    text = re.sub(r'En VidaExtra \|.*', '', text, flags=re.DOTALL)
    
    basura = [
        r"No te pierdas nada y ¡Síguenos en Google News!",
        r"No te pierdas nada y",
        r"Imagen principal de 3DJuegos",
        r"PUBLICIDAD",
        r"Más historias en la categoría.*",
        r"Suscribete al canal de.*"
    ]
    for patron in basura:
        text = re.sub(patron, "", text, flags=re.IGNORECASE | re.DOTALL)

    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text[:8000].strip()

def procesar_noticias():
    print("--- INICIANDO SCRAPER DINÁMICO ---")
    
    # 1. CARGAR FUENTES
    if not os.path.exists('sources.json'):
        print("ERROR: No se encontró sources.json en la raíz.")
        return

    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            FEEDS = data['fuentes']
            print(f"Fuentes cargadas: {len(FEEDS)}")
    except Exception as e:
        print(f"ERROR al leer sources.json: {e}")
        return

    noticias_finales = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}

    # 2. BUCLE DE EXTRACCIÓN
    for fuente in FEEDS:
        nombre = fuente['nombre']
        url = fuente['url']
        print(f"Sincronizando: {nombre}")
        
        feed = feedparser.parse(url)
        
        for entrada in feed.entries[:10]:
            try:
                r = requests.get(entrada.link, headers=headers, timeout=10)
                r.encoding = r.apparent_encoding if "vandal" in entrada.link or "generacion" in entrada.link else 'utf-8'

                article = Article(entrada.link, language='es')
                article.set_html(r.text)
                article.parse()
                
                if len(article.text) > 100:
                    noticia = {
                        "titulo": clean_ultimate(article.title),
                        "fecha": entrada.get("published", "Reciente"),
                        "imagen": article.top_image,
                        "resumen": clean_ultimate(article.text),
                        "fuente": nombre,
                        "link": entrada.link
                    }
                    noticias_finales.append(noticia)
                    print(f"  OK: {noticia['titulo'][:40]}...")
                
                time.sleep(0.2)
            except Exception as e:
                print(f"  Error en noticia de {nombre}: {e}")
                continue

    # 3. GUARDAR RESULTADOS
    if noticias_finales:
        with open('noticias.json', 'w', encoding='utf-8') as f:
            json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
        print(f"--- PROCESO TERMINADO: {len(noticias_finales)} noticias guardadas ---")
    else:
        print("AVISO: No se extrajo ninguna noticia válida.")

if __name__ == "__main__":
    procesar_noticias()
