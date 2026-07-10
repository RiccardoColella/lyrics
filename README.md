# Sommerkonzert im Englischen Garten – Liedtexte

Sito statico con i testi delle canzoni del concerto degli **Heart of Gold**
(Hirschau, Englischer Garten, München – 12 luglio 2026, ore 18:00).
Organizzato dal Kulturzentrum You e.V.

Tutto il sito è un unico file: [`index.html`](index.html).

## Aggiornare i testi

I testi sono estratti da un file Word `Monaco - 12 luglio 2026.docx`
(che non ho pubblicato). Se ci sono modifiche con il documento:

```bash
python3 build_site.py   # rigenera index.html
git add index.html && git commit -m "Aggiorna testi" && git push
```

Struttura attesa del documento: titolo canzone in MAIUSCOLO seguito da
`- AUTORE`, strofe separate da righe vuote, sezioni con i nomi delle
categorie (es. `CANTI IRLANDESI`).
