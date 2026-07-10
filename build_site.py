#!/usr/bin/env python3
"""Generate index.html for the Sommerkonzert lyrics site from the Word doc."""
import zipfile, re, html, unicodedata
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
import os
HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, 'Monaco - 12 luglio 2026.docx')
OUT = os.path.join(HERE, 'index.html')

CATEGORIES = {
    'CANTI NAPOLETANI / SUD ITALIA',
    'CANTI IRLANDESI',
    'COUNTRY, FOLK, ROCK U.S.A.',
    'GOSPEL',
    'MONDO IBERICO / AMERICA LATINA',
}

z = zipfile.ZipFile(DOCX)
root = ET.fromstring(z.read('word/document.xml'))
paras = []
for p in root.iter(W + 'p'):
    line = ''.join(t.text or '' for t in p.iter(W + 't'))
    paras.append(line.rstrip())

def is_title(line):
    """A song title: pre-dash part is all-caps-ish."""
    m = re.match(r"^(.+?)\s*[-–]\s*(.+)$", line)
    if not m:
        return None
    pre = m.group(1).strip()
    letters = [c for c in pre if c.isalpha()]
    if len(letters) < 3:
        return None
    if pre != pre.upper():
        return None
    return (pre.strip(), m.group(2).strip())

def slugify(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-zA-Z0-9]+", '-', s).strip('-').lower()
    return s

# Parse into categories -> songs -> stanzas
cats = []          # list of {name, songs: [{title, author, stanzas: [[line,...],...]}]}
cur_cat = None
cur_song = None
cur_stanza = []

def flush_stanza():
    global cur_stanza
    if cur_song is not None and cur_stanza:
        cur_song['stanzas'].append(cur_stanza)
    cur_stanza = []

for line in paras:
    stripped = line.strip()
    if stripped == 'CANTI POPOLARI DAL MONDO':
        continue
    if stripped in CATEGORIES:
        flush_stanza()
        cur_song = None
        cur_cat = {'name': stripped, 'songs': []}
        cats.append(cur_cat)
        continue
    t = is_title(stripped)
    if t and cur_cat is not None:
        flush_stanza()
        cur_song = {'title': t[0], 'author': t[1], 'stanzas': []}
        cur_cat['songs'].append(cur_song)
        continue
    if not stripped:
        flush_stanza()
        continue
    if cur_song is not None:
        cur_stanza.append(stripped)
flush_stanza()

n_songs = sum(len(c['songs']) for c in cats)
print(f"Parsed {len(cats)} categories, {n_songs} songs")
for c in cats:
    print(f"  {c['name']}: {len(c['songs'])} songs -> " + ', '.join(s['title'] for s in c['songs']))

# Pretty display names for categories (title-case-ish, keep as in doc but nicer)
CAT_DISPLAY = {
    'CANTI NAPOLETANI / SUD ITALIA': 'Canti napoletani / Sud Italia',
    'CANTI IRLANDESI': 'Canti irlandesi',
    'COUNTRY, FOLK, ROCK U.S.A.': 'Country, Folk, Rock U.S.A.',
    'GOSPEL': 'Gospel',
    'MONDO IBERICO / AMERICA LATINA': 'Mondo iberico / America Latina',
}

def title_display(t):
    """Title-case without capitalizing after apostrophes (unlike str.title())."""
    def cap(word):
        for i, c in enumerate(word):
            if c.isalpha():
                return word[:i] + c.upper() + word[i+1:].lower()
        return word
    return ' '.join(cap(w) for w in t.split(' '))

# Build HTML
toc = ''
songs = ''
toc_html = []
songs_html = []
for c in cats:
    cslug = slugify(c['name'])
    toc_html.append(f'<h2 class="toc-cat">{html.escape(CAT_DISPLAY[c["name"]])}</h2>')
    toc_html.append('<ol class="toc-list">')
    for s in c['songs']:
        sid = slugify(s['title'])
        toc_html.append(
            f'<li><a href="#{sid}"><span class="toc-title">{html.escape(title_display(s["title"]))}</span>'
            f'<span class="toc-author">{html.escape(s["author"])}</span></a></li>')
    toc_html.append('</ol>')

    songs_html.append(f'<section class="category" id="{cslug}">')
    songs_html.append(f'<h2 class="cat-heading">{html.escape(CAT_DISPLAY[c["name"]])}</h2>')
    for s in c['songs']:
        sid = slugify(s['title'])
        songs_html.append(f'<article class="song" id="{sid}">')
        songs_html.append(f'<h3 class="song-title">{html.escape(title_display(s["title"]))}</h3>')
        songs_html.append(f'<p class="song-author">{html.escape(s["author"])}</p>')
        for stanza in s['stanzas']:
            lines = '<br>'.join(html.escape(l) for l in stanza)
            # refrain reminder lines like "Sona, sona…" – single short line ending with …
            cls = ' class="refrain"' if (len(stanza) == 1 and stanza[0].rstrip().endswith(('…', '...'))) else ''
            songs_html.append(f'<p{cls}>{lines}</p>')
        songs_html.append('<p class="back-link"><a href="#top">↑ Programm</a></p>')
        songs_html.append('</article>')
    songs_html.append('</section>')

toc = '\n'.join(toc_html)
songs = '\n'.join(songs_html)

page = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sommerkonzert im Englischen Garten – Heart of Gold – Liedtexte</title>
<meta name="description" content="Liedtexte zum Mitsingen – Sommerkonzert im Englischen Garten mit Heart of Gold, 12. Juli 2026, Hirschau München. Kulturzentrum You e.V.">
<style>
  :root {{
    --bg: #fdfaf4;
    --ink: #2b2a26;
    --muted: #77716a;
    --accent: #b3541e;
    --accent-soft: #f3e3d3;
    --rule: #e5ddd0;
    --card: #ffffff;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #1c1b19;
      --ink: #ece7de;
      --muted: #a39c92;
      --accent: #e08a4e;
      --accent-soft: #3a2d22;
      --rule: #37342f;
      --card: #262420;
    }}
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: Georgia, 'Times New Roman', serif;
    line-height: 1.55;
    font-size: var(--fs, 18px);
  }}
  .wrap {{ max-width: 680px; margin: 0 auto; padding: 0 1.1rem 4rem; }}

  header.hero {{
    text-align: center;
    padding: 2.2rem 1rem 1.6rem;
    border-bottom: 3px double var(--accent);
    margin-bottom: 1.5rem;
  }}
  .hero .pretitle {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    text-transform: uppercase;
    letter-spacing: .18em;
    font-size: .72rem;
    color: var(--muted);
    margin: 0 0 .6rem;
  }}
  .hero h1 {{
    font-size: 1.9rem;
    line-height: 1.2;
    margin: 0 0 .2rem;
    font-weight: normal;
  }}
  .hero h1 em {{ font-style: italic; color: var(--accent); }}
  .hero .band {{
    font-size: 1.15rem;
    margin: .5rem 0 1rem;
  }}
  .hero .band strong {{ color: var(--accent); }}
  .hero .details {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: .85rem;
    color: var(--muted);
    margin: 0;
  }}
  .hero .details span {{ display: block; margin: .15rem 0; }}
  .hero .free {{
    display: inline-block;
    margin-top: .8rem;
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: .8rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 999px;
    padding: .25rem .9rem;
  }}

  .toc-cat {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    text-transform: uppercase;
    letter-spacing: .14em;
    font-size: .78rem;
    color: var(--accent);
    margin: 1.6rem 0 .4rem;
  }}
  .toc-list {{ list-style: none; margin: 0; padding: 0; }}
  .toc-list li {{ border-bottom: 1px solid var(--rule); }}
  .toc-list a {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 1rem;
    padding: .55rem .2rem;
    text-decoration: none;
    color: var(--ink);
  }}
  .toc-list a:active {{ background: var(--accent-soft); }}
  .toc-title {{ font-size: 1rem; }}
  .toc-author {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: .7rem;
    color: var(--muted);
    text-align: right;
    text-transform: uppercase;
    letter-spacing: .05em;
    flex-shrink: 0;
    max-width: 45%;
  }}

  .cat-heading {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    text-transform: uppercase;
    letter-spacing: .16em;
    font-size: .85rem;
    color: var(--accent);
    text-align: center;
    margin: 3.5rem 0 0;
    padding-top: 1.5rem;
    border-top: 3px double var(--accent);
  }}
  .song {{ padding-top: 1rem; margin-top: 1.5rem; }}
  .song + .song {{ border-top: 1px solid var(--rule); }}
  .song-title {{
    font-size: 1.35rem;
    font-weight: normal;
    margin: 1rem 0 0;
    color: var(--ink);
  }}
  .song-author {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: .72rem;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--muted);
    margin: .2rem 0 1.2rem;
  }}
  .song p {{ margin: 0 0 1.05em; }}
  .song p.refrain {{ font-style: italic; color: var(--muted); }}
  .back-link {{ text-align: right; }}
  .back-link a {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: .75rem;
    color: var(--muted);
    text-decoration: none;
    letter-spacing: .05em;
  }}

  footer {{
    margin-top: 4rem;
    padding-top: 1.2rem;
    border-top: 3px double var(--accent);
    text-align: center;
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: .78rem;
    color: var(--muted);
  }}

  .font-controls {{
    position: fixed;
    right: .8rem;
    bottom: .8rem;
    display: flex;
    gap: .4rem;
    z-index: 10;
  }}
  .font-controls button {{
    width: 2.6rem;
    height: 2.6rem;
    border-radius: 50%;
    border: 1px solid var(--rule);
    background: var(--card);
    color: var(--ink);
    font-family: Georgia, serif;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
  }}
  .font-controls .small {{ font-size: .8rem; }}
  .font-controls .big {{ font-size: 1.2rem; }}
</style>
</head>
<body id="top">
<div class="wrap">

<header class="hero">
  <p class="pretitle">Kulturzentrum You e.V. präsentiert</p>
  <h1>Sommerkonzert<br><em>im Englischen Garten</em></h1>
  <p class="band">mit <strong>Heart of Gold</strong><br><span style="font-size:.85em;color:var(--muted)">Canti popolari dal mondo &middot; Folk songs from around the world</span></p>
  <p class="details">
    <span>Sonntag, 12. Juli 2026 &middot; 18:00 Uhr</span>
    <span>Hirschau im Englischen Garten</span>
    <span>Gyßlingstraße 15 &middot; 80805 München</span>
  </p>
  <span class="free">Eintritt frei</span>
</header>

<nav id="programm" aria-label="Programm">
{toc}
</nav>

{songs}

<footer>
  <p>Sommerkonzert im Englischen Garten &middot; Heart of Gold<br>
  Eine Veranstaltung des Kulturzentrum You e.V.</p>
</footer>

</div>

<div class="font-controls" aria-hidden="false">
  <button class="small" onclick="zoom(-1)" aria-label="Schrift verkleinern">A−</button>
  <button class="big" onclick="zoom(1)" aria-label="Schrift vergrößern">A+</button>
</div>

<script>
  var sizes = [16, 18, 20, 23, 26];
  var idx = parseInt(localStorage.getItem('fs-idx') || '1', 10);
  function apply() {{
    document.body.style.setProperty('--fs', sizes[idx] + 'px');
    localStorage.setItem('fs-idx', idx);
  }}
  function zoom(d) {{
    idx = Math.min(sizes.length - 1, Math.max(0, idx + d));
    apply();
  }}
  apply();
</script>
</body>
</html>
"""

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(page)
print(f"Wrote {OUT} ({len(page)} bytes)")
