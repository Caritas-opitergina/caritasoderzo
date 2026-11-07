#!/usr/bin/env python3
"""
Sincronizza gli ultimi articoli di Caritas Italiana e Caritas Vittorio Veneto
con la home del sito.

- Legge i feed RSS pubblici dei due siti (nessun token necessario)
- Scrive _data/rete_caritas.json, che la home legge con Jekyll
- Se un feed non risponde, mantiene gli articoli già salvati per quella fonte
  (il box non si svuota per un errore temporaneo)
- Nessuna immagine: solo titolo, data e link al sito originale
"""
import json, os, sys, datetime, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

FILE_DATI = "_data/rete_caritas.json"
FUSO = ZoneInfo("Europe/Rome")
MAX_POST = 3   # articoli salvati per ciascuna fonte

FONTI = [
    {
        "id": "italiana",
        "nome": "Caritas Italiana",
        "sito": "https://www.caritas.it/",
        "feed": "https://www.caritas.it/feed/",
        # Categorie da escludere (confronto senza maiuscole/minuscole)
        "escludi_categorie": ["dalle Caritas diocesane"],
    },
    {
        "id": "vittorio-veneto",
        "nome": "Caritas Vittorio Veneto",
        "sito": "https://www.caritasvittorioveneto.it/",
        "feed": "https://www.caritasvittorioveneto.it/feed/",
        "escludi_categorie": [],
    },
]


def scarica(url):
    req = urllib.request.Request(url, headers={
        # Alcuni siti WordPress rifiutano lo user agent predefinito di Python
        "User-Agent": "Mozilla/5.0 (compatible; caritasoderzo.org feed reader)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def leggi_feed(xml_bytes, escludi_categorie):
    radice = ET.fromstring(xml_bytes)
    escludi = {c.strip().lower() for c in escludi_categorie}
    post = []
    for item in radice.iter("item"):
        categorie = {(c.text or "").strip().lower() for c in item.findall("category")}
        if categorie & escludi:
            continue
        titolo = " ".join((item.findtext("title") or "").split())
        link = (item.findtext("link") or "").strip()
        data_raw = item.findtext("pubDate")
        if not (titolo and link and data_raw):
            continue
        quando = parsedate_to_datetime(data_raw).astimezone(FUSO)
        post.append((quando, {
            "titolo": titolo,
            "link": link,
            "data": quando.strftime("%Y-%m-%d %H:%M:%S %z"),
        }))
    post.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in post[:MAX_POST]]


def main():
    vecchio = ""
    precedenti = {}
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, encoding="utf-8") as f:
            vecchio = f.read()
        try:
            for fonte in json.loads(vecchio).get("fonti", []):
                precedenti[fonte["id"]] = fonte.get("post", [])
        except (json.JSONDecodeError, KeyError):
            pass

    fonti = []
    errori = 0
    for fonte in FONTI:
        try:
            post = leggi_feed(scarica(fonte["feed"]), fonte["escludi_categorie"])
            print(f"{fonte['nome']}: {len(post)} articoli.")
        except Exception as e:
            errori += 1
            post = precedenti.get(fonte["id"], [])
            print(f"::warning::{fonte['nome']}: feed non letto ({e}). Mantengo i dati precedenti.")
        fonti.append({
            "id": fonte["id"],
            "nome": fonte["nome"],
            "sito": fonte["sito"],
            "post": post,
        })

    nuovo = json.dumps({"fonti": fonti}, ensure_ascii=False, indent=2) + "\n"
    if nuovo != vecchio:
        with open(FILE_DATI, "w", encoding="utf-8") as f:
            f.write(nuovo)
        print("Dati aggiornati.")
    else:
        print("Nessun articolo nuovo.")

    # Se entrambi i feed falliscono, l'esecuzione risulta rossa nel tab Actions
    if errori == len(FONTI):
        sys.exit("Nessun feed raggiungibile.")


if __name__ == "__main__":
    main()
