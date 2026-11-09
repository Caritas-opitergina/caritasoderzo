# CLAUDE.md — sito caritasoderzo.org

Istruzioni per Claude Code su questo repository. Rispondi sempre in italiano, in modo diretto e concreto, senza approfondimenti non richiesti.

## Cos'è

Sito di **Caritas opitergina – Centro di Ascolto ODV** (Oderzo, TV — RUNTS n. 96793, C.F. 94029790261).
Il nome si scrive sempre **"Caritas opitergina"**, con la "o" minuscola.

- Jekyll su GitHub Pages, repo `Caritas-opitergina/caritasoderzo`, branch `main`, cartella root.
- Ogni push su `main` pubblica il sito (tab Actions → "pages build and deployment").
- Dominio su Squarespace Domains. **Non toccare mai `CNAME`.**

## Regole di lavoro (obbligatorie)

1. **All'inizio di ogni sessione e prima di ogni push: `git pull`.** Due GitHub Action fanno commit da sole due volte al giorno.
2. **Prima di fare commit, mostra le modifiche pagina per pagina** (prima/dopo, o il diff) e **aspetta l'ok esplicito**. Niente commit né push senza conferma.
3. Commit piccoli, con messaggi in italiano che dicano cosa cambia (es. "Contatti: numeri cliccabili").
4. Dopo il push, controlla che il deploy in Actions sia verde e segnala eventuali errori di build.
5. Se una richiesta è ambigua o contraddice queste regole, chiedi prima di procedere.

## File generati automaticamente — non modificarli a mano

- `_data/threads.json` e `assets/threads/`: ultimi post Threads in home. Li scrive `.github/workflows/threads.yml` con `_scripts/threads_sync.py`.
- `_data/rete_caritas.json`: notizie della rete Caritas in home. Lo scrive `.github/workflows/rete-caritas.yml` con `_scripts/rete_caritas_sync.py`.
- I secret `THREADS_TOKEN` e `SECRETS_PAT` stanno nelle impostazioni del repo. `SECRETS_PAT` scade il **17/1/2027** e va rinnovato a inizio gennaio.

## Struttura

- Pagine: `index.html`, `servizi.html`, `contatti.html`, `notizie.html`, `borse-di-studio.html`, `video.html`, `rassegna-stampa.html`, `privacy.html`.
- `_layouts/default.html` (header, menu, footer), `post.html` (articoli), `redirect.html`.
- `_data/`: `menu.yml`, `video.yml`, `rassegna.yml`, `mesi.yml` + i file automatici sopra.
- Notizie in `_posts/AAAA-MM-GG-titolo.html`, con front matter `title`, `tipo` (es. "Comunicato stampa"), `description`, `sommario`. Se `title` + " | Caritas opitergina" supera 70 caratteri, aggiungi `titolo_seo` (max 49 caratteri): cambia solo il `<title>` della pagina, il titolo visibile resta intatto. URL: `/notizie/AAAA-MM-GG-titolo.html`.
- I vecchi indirizzi `/comunicati/...` restano attivi con `redirect_from`: non toglierli.
- Sitemap, feed e meta SEO sono generati dai plugin Jekyll (`jekyll-sitemap`, `jekyll-feed`, `jekyll-seo-tag`, `jekyll-redirect-from`).
- `llms.txt` (root): file per i motori di IA, processato da Jekyll. L’elenco delle notizie si aggiorna da solo; pagine principali e dati fissi (email, sedi, Donorbox, servizi) sono scritti a mano.
- `style.scss` (pubblicato da Jekyll come `/style.css` minimizzato: si modifica solo `style.scss`, non creare un `style.css` nella root), con variabili colore: `--brick #ac2c29`, `--ochre #edb230`, `--ink #332e32`, `--pine #1f4741`, sfondo `--paper #f2efe4`. Font self-hosted in `assets/fonts/` (Source Serif 4, Public Sans).

## Regole sui contenuti

- **Non aggiungere dati non verificati** (date, numeri, nomi, indirizzi, orari, telefoni): se mancano, chiedi.
- Dove il sito contraddice dati verificati (Il Dialogo, post Facebook, comunicati ufficiali), si corregge il sito.
- I comunicati stampa si pubblicano **alla lettera**. Sono ammessi solo interventi tipografici (doppi spazi, "E’" → "È", apostrofi), sempre segnalati.
- Nei testi visibili usa l'apostrofo tipografico (’), mai nel codice.
- Tono diretto, informale, concreto. Niente linguaggio pietistico o agiografico.
- Mai immagini di persone assistite.
- Fondazione: "nati formalmente nel 1994".
- Forania di Oderzo: comuni **Oderzo, Fontanelle, Mansuè, Portobuffolè**. Non aggiungere Ponte di Piave: la forania ne copre solo due frazioni.
- Non usare "Casa della Carità" per la sede di Piazzale Turroni 1.
- Non pubblicare i nomi delle agenzie immobiliari partner.
- Abitare Solidale va tenuto in basso profilo: non dargli più risalto di quanto ne abbia ora.
- Il servizio mobili usati è chiuso a tempo indeterminato. Su `contatti.html` la scritta resta, su `servizi.html` no.
- Comunicato Ex Caserma Zanusso del 25/9/2026: resta com'è.
- Borse di studio Caterina De Luca: non aggiungere la data di morte né il numero totale di edizioni previste (non confermati).
- Dopo ogni modifica a recapiti o orari, ricorda che va aggiornato anche **lnk.bio** (lnk.bio/caritas.oderzo).
- Se aggiungi, togli o rinomini una pagina, o cambiano recapiti, sedi, link Donorbox o servizi, aggiorna anche **`llms.txt`**. Nelle notizie compila sempre bene la `description`: finisce in `llms.txt`.

## Privacy e servizi esterni

- Il sito è **senza cookie e senza banner**: va mantenuto così.
- **Nessun nuovo script, font, embed o servizio esterno** senza approvazione esplicita, e in quel caso va aggiornato `privacy.html`.
- Oggi i servizi esterni sono: GoatCounter (statistiche senza cookie), pixel Metricool, link a Donorbox, YouTube solo dopo clic, widget Almanacco CEI in home caricato solo su schermi larghi.
- **Ogni modifica a `privacy.html` va validata dal CdA** prima di essere pubblicata: preparala, mostrala, non pubblicarla di tua iniziativa.
