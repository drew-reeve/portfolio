"""Static site builder for drew-reeve.github.io/portfolio.

Pages live in _src/pages/*.html as fragments. The first line is a meta comment:
  <!--meta {"title": "...", "desc": "...", "nav": "work", "og": "slug"} -->
Tokens inside fragments:
  {{root}}            relative path to site root ("" or "../")
  {{img:slug}}        responsive <img> for a photo in photos.py (lazy)
  {{img:slug:SIZES}}  same with a custom sizes attribute
  {{hero:slug}}       eager, high-priority <img> for heroes
  {{full:slug}}       URL of the largest version
  {{gallery}}         the field-notes gallery (filters + grid + lightbox)
  {{contact}}         shared contact band
Run: python3 _src/build.py   (from the site root)
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from photos import P

PH = {p["slug"]: p for p in P}
SIZES = json.load(open(os.path.join(HERE, "photo_sizes.json")))
EMAIL = "drew.reeve@gmail.com"

def url(slug, w, root):
    return f"{root}img/p/{slug}-{w}.webp"

def full(slug, root):
    return url(slug, SIZES[slug]["sizes"][-1], root)

def img(slug, root, sizes="(max-width: 800px) 100vw, 50vw", eager=False, extra=""):
    p, s = PH[slug], SIZES[slug]
    ws = s["sizes"]
    srcset = ", ".join(f"{url(slug, w, root)} {min(w, s['w']) if w == ws[-1] else w}w" for w in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="{url(slug, ws[0], root)}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{s["w"]}" height="{s["h"]}" alt="{html.escape(p["alt"])}" {load}{extra}>')

SPRITE = open(os.path.join(HERE, "sprite.svg")).read()

GALLERY_ORDER = [
  "missouri-sunset-cliffs", "andes-snowboard", "lolo-lake-overlook", "bald-eagle", "snowfield-valley",
  "white-cliffs-drew", "salmon-gravel-bar", "first-snow-ridge", "sandstone-slot", "drew-overlook",
  "rapid-line", "andes-rime", "missouri-tent-dawn", "fog-valley", "huckleberries", "salmon-canyon-drew",
  "snow-sunrise", "missouri-canoe-bow", "rock-perch", "white-cliffs-pink", "patagonia-sunset",
  "lolo-tread", "snowboard-lift", "clear-river-bank", "paintbrush-ridge", "amanita", "astoria-fog",
  "frosted-road", "snowmelt-creek", "missouri-oxbow", "ridge-trail-snags", "missouri-canoe-paddler",
  "lolo-van-fog", "salmon-sunset-ridge", "blue-lake-mountains", "whitewater-pines", "lolo-creek",
  "drysuit-putin", "still-water-dawn",
]
FILTERS = [("all", "Everything"), ("rivers", "Rivers"), ("mountains", "Mountains"), ("snow", "Snow"), ("trail", "Trail work")]

def gallery(root):
    counts = {k: sum(1 for s in GALLERY_ORDER if k == "all" or k in PH[s]["tags"].split()) for k, _ in FILTERS}
    btns = "".join(f'<button type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{lab} <span>{counts[k]}</span></button>' for k, lab in FILTERS)
    figs = []
    for s in GALLERY_ORDER:
        p = PH[s]
        figs.append(
            f'<figure class="note" data-tags="{p["tags"]}"><button type="button" aria-label="View larger: {html.escape(p["place"])}">'
            + img(s, root, sizes="(max-width: 600px) 92vw, (max-width: 1100px) 45vw, 300px", extra=f' data-full="{full(s, root)}"')
            + f'</button><figcaption><span class="date">{p["date"]}</span><span class="what">{html.escape(p["place"])}</span></figcaption></figure>')
    return (f'<div class="filters" role="group" aria-label="Filter photos">{btns}</div>'
            f'<div class="notes" id="notes-grid">{"".join(figs)}</div>'
            '<dialog class="lightbox" id="lightbox" aria-label="Photo viewer"><div class="stage">'
            '<img id="lightbox-img" src="" alt=""><p id="lightbox-cap"></p></div>'
            '<button class="lb-btn close" type="button" id="lightbox-close" aria-label="Close">×</button>'
            '<button class="lb-btn prev" type="button" id="lightbox-prev" aria-label="Previous photo">←</button>'
            '<button class="lb-btn next" type="button" id="lightbox-next" aria-label="Next photo">→</button></dialog>')

def contact(root):
    return f'''<section class="section band topo-bg" id="contact">
  <div class="wrap contact">
    <div class="intro">
      <div class="sign"><svg class="mark" viewBox="0 0 44 36" aria-hidden="true"><use href="#m-sun"/></svg><h2>Let's talk</h2></div>
      <p>I'm open to research collaborations, research-assistant and data roles, conversations about graduate study, and the occasional river trip. Write to me in English or Spanish.</p>
      <div class="contact-links">
        <div class="row"><span class="k">Email</span><span class="v"><a href="mailto:{EMAIL}" style="border:0;padding:0;display:inline">{EMAIL}</a><button class="copy" type="button" data-copy="{EMAIL}">Copy</button></span></div>
        <a href="https://www.linkedin.com/in/drew-reeve" target="_blank" rel="noopener"><span class="k">LinkedIn</span><span class="v">in/drew-reeve ↗</span></a>
        <a href="https://github.com/drew-reeve" target="_blank" rel="noopener"><span class="k">GitHub</span><span class="v">drew-reeve ↗</span></a>
        <a href="{root}cv.html"><span class="k">CV</span><span class="v">View online · PDF ↓</span></a>
        <div class="row"><span class="k">Based in</span><span class="v">Lolo, Montana · Mountain Time</span></div>
      </div>
    </div>
    <form class="form" id="contact-form" action="https://formsubmit.co/ajax/{EMAIL}" method="POST">
      <h3>Send a note</h3>
      <div class="two">
        <label>Name<input name="name" autocomplete="name" required></label>
        <label>Email<input name="email" type="email" autocomplete="email" required></label>
      </div>
      <div class="two">
        <label>Organization<input name="org" autocomplete="organization" placeholder="Optional"></label>
        <label>About<select name="topic">
          <option>Research collaboration</option><option>Graduate study</option><option>Data or economics work</option><option>Guiding or field work</option><option>Just saying hi</option>
        </select></label>
      </div>
      <label>Message<textarea name="message" required></textarea></label>
      <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="btn-row" style="align-items:center"><button class="btn ember" type="submit">Send message <span class="arrow">→</span></button><span class="fine">Goes straight to my inbox.</span></div>
      <p class="status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>'''

NAV = [("research", "Research", "index.html#research"), ("work", "Work", "portfolio.html"),
       ("field", "Field", "index.html#field"), ("photos", "Photos", "index.html#notes"), ("cv", "CV", "cv.html")]

def layout(meta, body, root):
    title = meta["title"]
    desc = meta["desc"]
    og_url = "https://drew-reeve.github.io/portfolio/img/og.jpg"
    nav = "".join(
        f'<a href="{root}{h}"{" aria-current=\"page\"" if meta.get("nav") == k else ""}>{lab}</a>' for k, lab, h in NAV)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="Andrew (Drew) Reeve">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{og_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1b2b3c">
<link rel="icon" href="{root}img/favicon.svg" type="image/svg+xml">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
<link rel="preload" href="{root}fonts/zilla-700.woff" as="font" type="font/woff" crossorigin>
<link rel="preload" href="{root}fonts/public-sans.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="{root}css/style.css">
{meta.get("head", "")}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{SPRITE}
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="{root}index.html"><svg class="mark" viewBox="0 0 44 36" aria-hidden="true"><use href="#m-mountain"/></svg><span><b>Drew Reeve</b><small>Economist · Data scientist · Guide</small></span></a>
    <div class="head-tools">
      <nav class="nav" id="nav" aria-label="Main">{nav}<a href="{root}index.html#contact" class="pill">Get in touch</a></nav>
      <button class="theme-btn" id="theme-btn" type="button" aria-label="Toggle dark theme"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z"/></svg></button>
      <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <span><svg class="mark" viewBox="0 0 44 36" aria-hidden="true"><use href="#m-mountain"/></svg>Built by hand in Lolo, Montana · © <span id="year">2026</span> Andrew "Drew" Reeve</span>
    <nav aria-label="Footer"><a href="{root}portfolio.html">Work</a><a href="{root}cv.html">CV</a><a href="mailto:{EMAIL}">Email</a><a href="https://www.linkedin.com/in/drew-reeve" target="_blank" rel="noopener">LinkedIn</a><a href="https://github.com/drew-reeve" target="_blank" rel="noopener">GitHub</a></nav>
  </div>
</footer>
<script src="{root}js/main.js" defer></script>
</body>
</html>
'''

def render(src, root):
    src = src.replace("{{root}}", root)
    src = src.replace("{{gallery}}", gallery(root)).replace("{{contact}}", contact(root))
    src = re.sub(r"\{\{hero:([a-z0-9-]+)\}\}", lambda m: img(m.group(1), root, sizes="100vw", eager=True), src)
    src = re.sub(r"\{\{full:([a-z0-9-]+)\}\}", lambda m: full(m.group(1), root), src)
    src = re.sub(r"\{\{img:([a-z0-9-]+)(?::([^}]*))?\}\}",
                 lambda m: img(m.group(1), root, sizes=m.group(2) or "(max-width: 800px) 100vw, 50vw"), src)
    left = re.findall(r"\{\{[^}]*\}\}", src)
    if left: raise SystemExit(f"unrendered tokens: {left}")
    return src

pages_dir = os.path.join(HERE, "pages")
for dirpath, _, files in os.walk(pages_dir):
    for f in sorted(files):
        if not f.endswith(".html"): continue
        rel = os.path.relpath(os.path.join(dirpath, f), pages_dir)
        depth = rel.count(os.sep)
        root = "../" * depth
        raw = open(os.path.join(dirpath, f), encoding="utf-8").read()
        m = re.match(r"<!--meta (.*?) -->\n", raw, re.S)
        meta = json.loads(m.group(1)); body = raw[m.end():]
        out = os.path.join(SITE, rel); os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(layout(meta, render(body, root), root))
        print("built", rel)
