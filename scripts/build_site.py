#!/usr/bin/env python3
"""Render cant.yaml into a static site at site/.

Output:
  site/index.html   - the catalog, one card per entry
  site/cant.yaml    - the machine-readable catalog, served verbatim
  site/schema/      - the entry schema, served verbatim

No templating dependencies; python3 + pyyaml only.
"""

import html
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"

data = yaml.safe_load((ROOT / "cant.yaml").read_text())
entries = data["entries"]

GENUS_META = {
    "pretext": ("Pretexts", "The user supplies the excuse; the agent adopts it. Countered by gates: contractual behavior no message content can waive."),
    "self-talk": ("Self-talk", "The agent invents the excuse itself. Countered by red-flag lists: if you catch yourself thinking this, stop."),
    "hybrid": ("Hybrids", "A pretext lowers the bar; the agent's own loophole finishes the job. Countered by both, plus structural safety graded on the attempt."),
}

def esc(s):
    return html.escape(str(s).strip())

cards = []
current_genus = None
for e in entries:
    if e["genus"] != current_genus:
        current_genus = e["genus"]
        title, blurb = GENUS_META[current_genus]
        cards.append(
            f'<h2 class="genus genus-{current_genus}" id="{current_genus}">{esc(title)}</h2>'
            f'<p class="genus-blurb">{esc(blurb)}</p>'
        )
    evidence = "".join(
        f'<li><span class="ev-type ev-{ev["type"]}">{esc(ev["type"])}</span> {esc(ev["source"])}</li>'
        for ev in e["evidence"]
    )
    related = ""
    if e.get("related"):
        links = ", ".join(f'<a href="#{rid.lower()}">{esc(rid)}</a>' for rid in e["related"])
        related = f'<p class="related">Related: {links}</p>'
    cards.append(f"""
<article class="entry" id="{e['id'].lower()}">
  <header>
    <span class="eid">{esc(e['id'])}</span>
    <h3>{esc(e['name'])}</h3>
    <span class="chip chip-{e['genus']}">{esc(e['genus'])}</span>
  </header>
  <blockquote class="quote">{esc(e['quote'])}</blockquote>
  <p class="move">{esc(e['move'])}</p>
  <p class="counter"><strong>Counter:</strong> {esc(e['counter'])}</p>
  <details><summary>Evidence</summary><ul class="evidence">{evidence}</ul></details>
  {related}
</article>""")

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalog of Agent Neutralization Techniques (CANT)</title>
<meta name="description" content="A named, evidence-backed catalog of the rationalizations AI agents use to break their own rules. {len(entries)} techniques, edition {esc(data['edition'])}.">
<style>
:root {{
  --ink: #1a2330; --paper: #fbfaf7; --muted: #5b6673;
  --pretext: #9a3b3b; --selftalk: #2c5f7c; --hybrid: #6d4d9c;
  --line: #e3ded4;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font: 17px/1.6 Georgia, 'Times New Roman', serif; color: var(--ink); background: var(--paper); }}
main {{ max-width: 46rem; margin: 0 auto; padding: 3rem 1.25rem 5rem; }}
h1 {{ font-size: 2.1rem; line-height: 1.15; margin: 0 0 .4rem; }}
.subtitle {{ color: var(--muted); font-style: italic; margin-top: 0; }}
.meta {{ font-family: ui-monospace, Menlo, monospace; font-size: .8rem; color: var(--muted); margin: 1.2rem 0 0; }}
.meta a {{ color: inherit; }}
h2.genus {{ margin: 3rem 0 .3rem; padding-top: 1.5rem; border-top: 3px double var(--line); font-size: 1.5rem; }}
.genus-blurb {{ color: var(--muted); margin-top: 0; }}
.entry {{ border: 1px solid var(--line); border-radius: 8px; padding: 1.1rem 1.3rem; margin: 1.1rem 0; background: #fff; }}
.entry header {{ display: flex; align-items: baseline; gap: .7rem; flex-wrap: wrap; }}
.eid {{ font-family: ui-monospace, Menlo, monospace; font-size: .8rem; color: var(--muted); }}
.entry h3 {{ margin: 0; font-size: 1.2rem; flex: 1; }}
.chip {{ font-family: ui-monospace, Menlo, monospace; font-size: .7rem; padding: .15rem .55rem; border-radius: 99px; color: #fff; }}
.chip-pretext {{ background: var(--pretext); }}
.chip-self-talk {{ background: var(--selftalk); }}
.chip-hybrid {{ background: var(--hybrid); }}
.quote {{ margin: .8rem 0; padding: .5rem 1rem; border-left: 3px solid var(--line); font-style: italic; color: #3c4654; }}
.move {{ margin: .6rem 0; }}
.counter {{ margin: .6rem 0; }}
details {{ font-size: .9rem; color: var(--muted); }}
summary {{ cursor: pointer; }}
.evidence {{ margin: .4rem 0 0; padding-left: 1.2rem; }}
.ev-type {{ font-family: ui-monospace, Menlo, monospace; font-size: .7rem; padding: .05rem .4rem; border-radius: 4px; background: var(--line); }}
.ev-captured {{ background: #d8ead8; }}
.related {{ font-size: .85rem; color: var(--muted); margin-bottom: 0; }}
.related a {{ color: var(--selftalk); }}
footer {{ margin-top: 3.5rem; padding-top: 1.2rem; border-top: 1px solid var(--line); font-size: .85rem; color: var(--muted); }}
footer a {{ color: var(--selftalk); }}
</style>
</head>
<body>
<main>
<h1>Catalog of Agent Neutralization Techniques</h1>
<p class="subtitle">CANT: a named, evidence-backed catalog of the rationalizations AI agents use to break their own rules.</p>
<p>AI agents rarely fail because they can't do the job. They fail because something, the user or the agent's own reasoning, supplies a justification that makes breaking the rule feel fine. CANT names those moves so you can write defenses against them by name and test for them by name. The term comes from Sykes &amp; Matza's 1957 criminology paper on techniques of neutralization; the English word <em>cant</em>, insincere stock phrases, is doing exactly the work you think it is.</p>
<p class="meta">Edition {esc(data['edition'])} · {len(entries)} techniques ·
<a href="cant.yaml">cant.yaml</a> ·
<a href="schema/cant-entry.schema.json">schema</a> ·
<a href="https://github.com/kanopi/cant">GitHub</a> ·
CC BY 4.0</p>
{''.join(cards)}
<footer>
<p>Authored by <a href="https://jimbir.ch">Jim Birch</a> at <a href="https://kanopi.com">Kanopi Studios</a>.
Built on Jesse Vincent's <a href="https://github.com/obra/superpowers">Superpowers</a> red-flag pattern and
<a href="https://github.com/addyosmani/agent-skills">Addy Osmani's agent-skills</a> eval model.
Reference harness: <a href="https://github.com/kanopi/skills-plugin-template">kanopi/skills-plugin-template</a>.</p>
</footer>
</main>
</body>
</html>
"""

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
(OUT / "index.html").write_text(page)
shutil.copy(ROOT / "cant.yaml", OUT / "cant.yaml")
shutil.copytree(ROOT / "schema", OUT / "schema")
print(f"site/ built: {len(entries)} entries, edition {data['edition']}")
