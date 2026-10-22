#!/usr/bin/env python3
"""Regenerate the first-author publication list in index.html from the ADS library.

Usage (from the repo root):
    ADS_TOKEN=xxxx python3 tools/update_pubs.py            # fetch live from ADS
    python3 tools/update_pubs.py --cache _papers/first_author.json   # offline, from a saved ADS export

Only the block between <!-- BEGIN AUTO PUBS --> and <!-- END AUTO PUBS --> and the
first-author count inside <span id="n-first">..</span> are rewritten. The hand-written
"Research Highlights" cards above the list are never touched.
"""
import argparse, html, json, os, pathlib, re, sys

LIB_ID = "7eLaCipeRIuYIkoZK0YHaA"
ME_NORM = "Zhuang, M"                 # ADS first_author_norm prefix
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
FL = "bibcode,title,author,first_author_norm,pub,bibstem,volume,page,year,pubdate,doi,identifier,doctype"

# Papers shown as highlight cards -> anchor id of the card in index.html.
# Keys are an ADS bibcode or "arXiv:<id>" (the arXiv form keeps matching after the
# paper is published and its bibcode changes).
HIGHLIGHTS = {
    "arXiv:2609.38373": "hl-at2026abck",
    "arXiv:2609.06985": "hl-nexus-transients",
    "2026ApJ...999...31Z": "hl-nexus-lrds",
    "2024ApJ...962...93Z": "hl-cosmosweb",
    "2023NatAs...7.1376Z": "hl-natas",
}
# Excluded from the list (bibstem or doctype).
EXCLUDE_BIBSTEMS = {"TNSTR", "ATel", "GCN"}
EXCLUDE_DOCTYPES = {"circular", "erratum", "abstract", "proposal", "catalog", "software"}

JOURNALS = {
    "The Astrophysical Journal": "ApJ",
    "The Astrophysical Journal Letters": "ApJL",
    "The Astrophysical Journal Supplement Series": "ApJS",
    "Monthly Notices of the Royal Astronomical Society": "MNRAS",
    "Nature Astronomy": "Nature Astronomy",
    "Nature": "Nature",
    "Science": "Science",
    "The Astronomical Journal": "AJ",
    "Astronomy and Astrophysics": "A&amp;A",
    "Annual Review of Astronomy and Astrophysics": "ARA&amp;A",
}
TEX = {r"\lesssim": "≲", r"\gtrsim": "≳", r"\sim": "~", r"\approx": "≈", r"\leq": "≤",
       r"\geq": "≥", r"\lambda": "λ", r"\alpha": "α", r"\beta": "β", r"\,": " "}


def fetch_ads(token):
    import requests
    r = requests.get(os.environ.get("SCIX_API_URL", "https://scixplorer.org/v1/search/query"),
                     headers={"Authorization": f"Bearer {token}"},
                     params={"q": f"docs(library/{LIB_ID})", "fl": FL, "rows": 2000,
                             "sort": "date desc"}, timeout=60)
    r.raise_for_status()
    return r.json()["response"]["docs"]


def arxiv_id(d):
    for i in d.get("identifier", []):
        m = re.match(r"arXiv:(\d{4}\.\d{4,5})$", i)
        if m:
            return m.group(1)
    return None


def clean_title(t):
    def math(m):
        s = m.group(1)
        for k, v in TEX.items():
            s = s.replace(k, v)
        s = re.sub(r"\s*=\s*", " = ", s)
        return f"<i>{s}</i>" if re.fullmatch(r"[A-Za-z]", s) else s.replace("z", "<i>z</i>", 1)
    t = html.escape(t, quote=False)
    t = re.sub(r"\$([^$]+)\$", math, t)
    t = re.sub(r"(?<![\w>])z(?= ?[≲≳<>=~])", "<i>z</i>", t)
    return t


def short_name(a):
    """'Zhuang, Ming-Yang' -> 'M.-Y. Zhuang'; 'Pierel, Justin D. R.' -> 'J. D. R. Pierel'."""
    if "," not in a:
        return a
    last, first = [s.strip() for s in a.split(",", 1)]
    parts = []
    for word in first.replace(".", ". ").split():
        sub = [w[0] + "." for w in word.split("-") if w]
        parts.append("-".join(sub))
    return (" ".join(parts) + " " + last).strip()


def authors_html(auth):
    names = [html.escape(short_name(a)) for a in auth]
    if names:
        names[0] = f'<span class="me">{names[0]}</span>'
    if len(names) > 4:
        return ", ".join(names[:3]) + ", et al."
    return ", ".join(names)


def venue(d):
    a = arxiv_id(d)
    pub = d.get("pub", "")
    if d.get("doctype") == "eprint" or pub.startswith("arXiv"):
        return f"arXiv:{a}" if a else "arXiv"
    j = JOURNALS.get(pub, html.escape(pub))
    page = (d.get("page") or [""])[0]
    bits = [j] + [x for x in (d.get("volume"), page) if x]
    return ", ".join(bits)


def highlight_anchor(d):
    a = arxiv_id(d)
    for key, anchor in HIGHLIGHTS.items():
        if d["bibcode"] == key or (a and key == f"arXiv:{a}"):
            return anchor
    return None


def item_html(d):
    a = arxiv_id(d)
    journal_doi = next((x for x in d.get("doi", []) if not x.startswith("10.48550")), None)
    links = [f'<a href="https://scixplorer.org/abs/{d["bibcode"]}/abstract">SciX</a>']
    if a:
        links.append(f'<a href="https://arxiv.org/abs/{a}">arXiv</a>')
    if journal_doi:
        links.append(f'<a href="https://doi.org/{journal_doi}">Journal</a>')
    anchor = highlight_anchor(d)
    badge = f'<a class="venue-badge" href="#{anchor}">Highlight</a> ' if anchor else ""
    return f"""        <div class="pub-item">
          <div class="pub-year">{d.get("year", "")}</div>
          <div>
            <p class="pub-title">{clean_title(d["title"][0])}</p>
            <p class="pub-authors">{authors_html(d.get("author", []))}</p>
            <p class="pub-venue">{badge}{venue(d)}</p>
            <div class="pub-links">{" ".join(links)}</div>
          </div>
        </div>"""


def is_first_author_paper(d):
    if not d.get("first_author_norm", "").startswith(ME_NORM):
        return False
    stem = (d.get("bibstem") or [d["bibcode"][4:9].strip(".")])[0]
    if stem in EXCLUDE_BIBSTEMS or "TNSTR" in d["bibcode"]:
        return False
    return d.get("doctype") not in EXCLUDE_DOCTYPES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", help="read ADS docs from this JSON file instead of the API")
    args = ap.parse_args()
    if args.cache:
        docs = json.load(open(args.cache))
    else:
        token = os.environ.get("ADS_TOKEN")
        if not token:
            sys.exit("Set ADS_TOKEN or pass --cache FILE")
        docs = fetch_ads(token)
    papers = [d for d in docs if is_first_author_paper(d)]
    papers.sort(key=lambda d: d.get("pubdate", ""), reverse=True)
    if not papers:
        sys.exit("No first-author papers found; refusing to wipe the list.")

    block = "\n\n".join(item_html(d) for d in papers)
    src = INDEX.read_text()
    if "<!-- BEGIN AUTO PUBS -->" not in src:
        sys.exit("Markers <!-- BEGIN/END AUTO PUBS --> not found in index.html")
    new = re.sub(r"(<!-- BEGIN AUTO PUBS -->).*?(<!-- END AUTO PUBS -->)",
                 lambda m: m.group(1) + "\n" + block + "\n" + m.group(2), src, flags=re.S)
    new = re.sub(r'(<span id="n-first">)\d+(</span>)', rf"\g<1>{len(papers)}\g<2>", new)
    if new == src:
        print(f"No change ({len(papers)} first-author papers).")
        return
    INDEX.write_text(new)
    print(f"Updated index.html with {len(papers)} first-author papers.")


if __name__ == "__main__":
    main()
