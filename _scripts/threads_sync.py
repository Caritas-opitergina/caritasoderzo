#!/usr/bin/env python3
"""
Sincronizza gli ultimi post Threads di Caritas opitergina con il sito.

- Legge i post via Threads API (token nel secret THREADS_TOKEN)
- Scarica e ridimensiona le immagini in assets/threads/ (nessun collegamento
  a Meta dal browser dei visitatori: niente cookie, niente tracciamento)
- Scrive _data/threads.json, che la home legge con Jekyll
- Il lunedì rinnova il token; se Meta ne restituisce uno diverso lo scrive
  in nuovo_token.txt (il workflow poi aggiorna il secret)
"""
import io, json, os, sys, datetime, urllib.request, urllib.parse, urllib.error
from zoneinfo import ZoneInfo
from PIL import Image

API = "https://graph.threads.net/v1.0"
MAX_POST = 5               # quanti post salvare (la home ne mostra quanti indicato in index.html)
LARGHEZZA_IMG = 640        # px
CARTELLA_IMG = "assets/threads"
FILE_DATI = "_data/threads.json"
FUSO = ZoneInfo("Europe/Rome")

TOKEN = os.environ.get("THREADS_TOKEN", "").strip()
if not TOKEN:
    sys.exit("Manca il secret THREADS_TOKEN.")


def chiama(url, params=None):
    params = dict(params or {})
    params["access_token"] = TOKEN
    full = url + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(full, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode("utf-8", "replace")
        sys.exit(f"Errore API Threads ({e.code}): {corpo}")


def rinnova_token():
    """Rinnovo settimanale (lunedì). Il token long-lived dura 60 giorni."""
    if datetime.date.today().weekday() != 0 and os.environ.get("FORZA_RINNOVO") != "1":
        return
    url = "https://graph.threads.net/refresh_access_token?" + urllib.parse.urlencode(
        {"grant_type": "th_refresh_token", "access_token": TOKEN})
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            nuovo = json.load(r).get("access_token", "")
    except urllib.error.HTTPError as e:
        # Non blocca l'aggiornamento dei post: il token attuale è ancora valido
        print(f"::warning::Rinnovo token non riuscito ({e.code}): {e.read().decode('utf-8','replace')}")
        return
    print(f"Token rinnovato: valido per altri 60 giorni.")
    if nuovo and nuovo != TOKEN:
        print(f"::add-mask::{nuovo}")
        with open("nuovo_token.txt", "w") as f:
            f.write(nuovo)


def scarica_immagine(url, nome):
    os.makedirs(CARTELLA_IMG, exist_ok=True)
    percorso = f"{CARTELLA_IMG}/{nome}.jpg"
    if os.path.exists(percorso):
        return "/" + percorso
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            img = Image.open(io.BytesIO(r.read()))
        img = img.convert("RGB")
        if img.width > LARGHEZZA_IMG:
            img = img.resize((LARGHEZZA_IMG, round(img.height * LARGHEZZA_IMG / img.width)), Image.LANCZOS)
        img.save(percorso, "JPEG", quality=82, optimize=True, progressive=True)
        return "/" + percorso
    except Exception as e:
        print(f"::warning::Immagine non scaricata per il post {nome}: {e}")
        return None


def url_immagine(p):
    tipo = p.get("media_type")
    if tipo == "IMAGE":
        return p.get("media_url")
    if tipo == "VIDEO":
        return p.get("thumbnail_url")
    if tipo == "CAROUSEL_ALBUM":
        if p.get("media_url"):
            return p["media_url"]
        figli = (p.get("children") or {}).get("data") or []
        if figli:
            f = chiama(f"{API}/{figli[0]['id']}", {"fields": "media_type,media_url,thumbnail_url"})
            return f.get("media_url") if f.get("media_type") == "IMAGE" else f.get("thumbnail_url")
    return None


def main():
    rinnova_token()

    profilo = chiama(f"{API}/me", {"fields": "username"})
    risposta = chiama(f"{API}/me/threads", {
        "fields": "id,media_type,media_url,thumbnail_url,permalink,text,timestamp,children",
        "limit": 15,
    })

    post = []
    for p in risposta.get("data", []):
        # Esclude i repost di contenuti altrui
        if p.get("media_type") == "REPOST_FACADE":
            continue
        quando = datetime.datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(FUSO)
        img = url_immagine(p)
        post.append({
            "id": p["id"],
            "data": quando.strftime("%Y-%m-%d %H:%M:%S %z"),
            "testo": (p.get("text") or "").strip(),
            "link": p.get("permalink"),
            "immagine": scarica_immagine(img, p["id"]) if img else None,
            "video": p.get("media_type") == "VIDEO",
        })
        if len(post) >= MAX_POST:
            break

    # Rimuove le immagini dei post non più mostrati
    tenere = {f"{p['id']}.jpg" for p in post}
    if os.path.isdir(CARTELLA_IMG):
        for f in os.listdir(CARTELLA_IMG):
            if f not in tenere:
                os.remove(os.path.join(CARTELLA_IMG, f))

    dati = {"profilo": profilo.get("username", ""), "post": post}
    nuovo = json.dumps(dati, ensure_ascii=False, indent=2) + "\n"
    vecchio = open(FILE_DATI, encoding="utf-8").read() if os.path.exists(FILE_DATI) else ""
    if nuovo != vecchio:
        with open(FILE_DATI, "w", encoding="utf-8") as f:
            f.write(nuovo)
        print(f"Aggiornati {len(post)} post.")
    else:
        print("Nessun post nuovo.")


if __name__ == "__main__":
    main()
