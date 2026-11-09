#!/usr/bin/env python3
"""Generate the project detail pages from projects.json.

Usage:  python3 build.py

Writes  projects/<slug>/index.html      (English)
        de/projects/<slug>/index.html   (German)

Adding content to a project:
  * Text: edit projects.json. Each language has "summary", "facts", "scope",
    "chips" and optional extra "sections":
        {"title": "Design approach", "paragraphs": ["...", "..."]}
  * Pictures: put the files in projects/<slug>/images/. They are picked up
    automatically in file-name order. To add captions, list them under
    "images" in projects.json:
        {"file": "crane-01.jpg", "en": "English caption", "de": "Deutsche Bildunterschrift"}
"""
import json
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg"}

UI = {
    "en": {
        "home": "",  # path of the language home below the site root
        "role_suffix": "Mechanical Design Engineer",
        "nav": [("experience", "Experience"), ("projects", "Projects"), ("skills", "Skills"),
                ("education", "Education"), ("contact", "Contact")],
        "skip": "Skip to content", "sections": "Sections", "language": "Language",
        "theme": "Switch colour theme", "home_label": "Ehsan Shahinfar — home",
        "back": "← All projects", "facts": "Project facts", "scope": "Scope of work",
        "gallery": "Gallery", "prev": "Previous project", "next": "Next project",
        "top": "Back to top ↑", "project": "Project",
    },
    "de": {
        "home": "de/",
        "role_suffix": "Maschinenbauingenieur",
        "nav": [("experience", "Erfahrung"), ("projects", "Projekte"), ("skills", "Kompetenzen"),
                ("education", "Ausbildung"), ("contact", "Kontakt")],
        "skip": "Zum Inhalt springen", "sections": "Abschnitte", "language": "Sprache",
        "theme": "Farbschema wechseln", "home_label": "Ehsan Shahinfar — Startseite",
        "back": "← Alle Projekte", "facts": "Projektdaten", "scope": "Leistungsumfang",
        "gallery": "Bilder", "prev": "Vorheriges Projekt", "next": "Nächstes Projekt",
        "top": "Nach oben ↑", "project": "Projekt",
    },
}


def images_for(project):
    """Captioned images from projects.json first, then any other files in the folder."""
    folder = ROOT / "projects" / project["slug"] / "images"
    listed = [dict(i) for i in project.get("images", [])]
    seen = {i["file"] for i in listed}
    if folder.is_dir():
        for f in sorted(folder.iterdir()):
            if f.suffix.lower() in IMAGE_TYPES and f.name not in seen:
                listed.append({"file": f.name})
    return listed


def page(project, lang, index, projects):
    ui, p = UI[lang], project[lang]
    slug = project["slug"]
    root = "../../" if lang == "en" else "../../../"   # path back to the site root
    home = root + ui["home"]
    other = "de" if lang == "en" else "en"
    other_url = f"{root}{UI[other]['home']}projects/{slug}/"
    url = f"https://shahinfar.me/{ui['home']}projects/{slug}/"
    alt = {l: f"https://shahinfar.me/{UI[l]['home']}projects/{slug}/" for l in UI}
    img_base = "images/" if lang == "en" else f"{root}projects/{slug}/images/"

    nav = "\n".join(f'          <li><a href="{home}#{i}">{e(t)}</a></li>' for i, t in ui["nav"])
    facts = "\n".join(f"            <div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in p["facts"])
    scope = "\n".join(f"              <li>{e(s)}</li>" for s in p["scope"])
    chips = "".join(f"<span>{e(c)}</span>" for c in p["chips"])

    extra = ""
    for s in p.get("sections", []):
        paras = "\n".join(f"            <p>{e(t)}</p>" for t in s["paragraphs"])
        extra += f"""
          <section class="prose">
            <h2>{e(s["title"])}</h2>
{paras}
          </section>"""

    gallery = ""
    imgs = images_for(project)
    if imgs:
        figs = ""
        for im in imgs:
            cap = im.get(lang, "")
            src = img_base + im["file"]
            caption = f"\n              <figcaption>{e(cap)}</figcaption>" if cap else ""
            figs += f"""
            <figure>
              <a href="{e(src)}"><img src="{e(src)}" alt="{e(cap or p["title"])}" loading="lazy"></a>{caption}
            </figure>"""
        gallery = f"""
        <section class="gallery-block">
          <h2>{ui["gallery"]}</h2>
          <div class="gallery">{figs}
          </div>
        </section>"""

    prev_p, next_p = projects[index - 1], projects[(index + 1) % len(projects)]
    en_cur = ' aria-current="page"' if lang == "en" else ' hreflang="en" aria-label="English"'
    de_cur = ' aria-current="page"' if lang == "de" else ' hreflang="de" aria-label="Deutsch"'
    en_href = "./" if lang == "en" else other_url
    de_href = "./" if lang == "de" else other_url

    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(p["title"])} — Ehsan Shahinfar</title>
  <meta name="description" content="{e(p["summary"])}">
  <meta property="og:title" content="{e(p["title"])} — Ehsan Shahinfar">
  <meta property="og:description" content="{e(p["summary"])}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta name="color-scheme" content="light dark">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="en" href="{alt["en"]}">
  <link rel="alternate" hreflang="de" href="{alt["de"]}">
  <link rel="alternate" hreflang="x-default" href="{alt["en"]}">
  <link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root}styles.css">
  <script>
    try {{
      var t = localStorage.getItem('theme');
      if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t;
    }} catch (e) {{}}
  </script>
</head>
<body>
  <!-- Generated by build.py from projects.json — edit those, not this file. -->
  <a class="skip" href="#main">{ui["skip"]}</a>

  <header class="site-header">
    <div class="wrap bar">
      <a class="brand" href="{home}" aria-label="{ui["home_label"]}">
        <span class="brand-mark" aria-hidden="true">ES</span>
        <span class="brand-name">Ehsan Shahinfar</span>
      </a>
      <nav aria-label="{ui["sections"]}">
        <ul class="nav">
{nav}
        </ul>
      </nav>
      <div class="lang" role="group" aria-label="{ui["language"]}">
        <a href="{en_href}" lang="en"{en_cur}>EN</a>
        <a href="{de_href}" lang="de"{de_cur}>DE</a>
      </div>
      <button class="theme-toggle" type="button" aria-label="{ui["theme"]}">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor"/></svg>
      </button>
    </div>
  </header>

  <main id="main" class="project">
    <section class="hero project-hero" id="top">
      <div class="wrap">
        <a class="back" href="{home}#projects">{ui["back"]}</a>
        <p class="eyebrow">{e(p["tag"])}</p>
        <h1>{e(p["title"])}</h1>
        <p class="lede">{e(p["summary"])}</p>
        <p class="chips">{chips}</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="project-grid">
          <aside class="facts-block">
            <h2>{ui["facts"]}</h2>
            <dl class="facts">
{facts}
            </dl>
          </aside>
          <div class="project-body">
          <section class="what">
            <h2>{ui["scope"]}</h2>
            <ul>
{scope}
            </ul>
          </section>{extra}
          </div>
        </div>{gallery}
      </div>
    </section>

    <nav class="pager" aria-label="{ui["project"]}">
      <div class="wrap">
        <a href="../{prev_p["slug"]}/" rel="prev"><span>← {ui["prev"]}</span><strong>{e(prev_p[lang]["title"])}</strong></a>
        <a href="../{next_p["slug"]}/" rel="next"><span>{ui["next"]} →</span><strong>{e(next_p[lang]["title"])}</strong></a>
      </div>
    </nav>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <span>© <span id="year">2026</span> Ehsan Shahinfar</span>
      <a href="#top">{ui["top"]}</a>
    </div>
  </footer>

  <script src="{root}script.js" defer></script>
</body>
</html>
"""


def main():
    projects = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
    for i, project in enumerate(projects):
        for lang in UI:
            out = ROOT / UI[lang]["home"] / "projects" / project["slug"] / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page(project, lang, i, projects), encoding="utf-8")
            print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
