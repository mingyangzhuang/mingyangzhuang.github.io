#!/usr/bin/env python3
"""Update the paper counts in the Publications intro of index.html from the SciX library.

Usage (from the repo root):
    ADS_TOKEN=xxxx python3 tools/update_pubs.py                       # fetch live from SciX
    python3 tools/update_pubs.py --cache _papers/first_author.json    # offline, from a saved export

Rewrites two numbers in index.html:
    <span id="n-first">..</span>    number of first-author papers
    <span id="n-contrib">..</span>  "contributed" papers, rounded to the nearest ten:
                                    (library size without TNS reports) - (first-author) - MENTORED
The number of (co-)mentored papers (MENTORED) is maintained by hand below and in index.html.
The Research Highlights cards are hand-written and never touched. New first-author papers\n(not yet in tools/known_first_author.json) are written to new_papers.md, which the Action posts as an Issue.
"""
import argparse, json, os, pathlib, re, sys

LIB_ID = "7eLaCipeRIuYIkoZK0YHaA"
ME_NORM = "Zhuang, M"               # first_author_norm prefix
MENTORED = 5                        # (co-)mentored papers; update by hand (and the text in index.html)
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
FL = "bibcode,title,first_author_norm,bibstem,doctype,identifier"
KNOWN = ROOT / "tools" / "known_first_author.json"   # papers already seen (arXiv id, else bibcode)
NEW_MD = ROOT / "new_papers.md"                       # written only when new papers appear; the Action turns it into an Issue

EXCLUDE_BIBSTEMS = {"TNSTR", "ATel", "GCN"}
EXCLUDE_DOCTYPES = {"circular", "erratum", "abstract", "proposal", "catalog", "software"}


def fetch(token):
    import requests
    r = requests.get(os.environ.get("SCIX_API_URL", "https://scixplorer.org/v1/search/query"),
                     headers={"Authorization": f"Bearer {token}"},
                     params={"q": f"docs(library/{LIB_ID})", "fl": FL, "rows": 2000}, timeout=60)
    r.raise_for_status()
    return r.json()["response"]["docs"]


def is_tns(d):
    stem = (d.get("bibstem") or [d["bibcode"][4:9].strip(".")])[0]
    return stem == "TNSTR" or "TNSTR" in d["bibcode"]


def is_first_author_paper(d):
    if not d.get("first_author_norm", "").startswith(ME_NORM):
        return False
    stem = (d.get("bibstem") or [d["bibcode"][4:9].strip(".")])[0]
    if stem in EXCLUDE_BIBSTEMS or is_tns(d):
        return False
    return d.get("doctype") not in EXCLUDE_DOCTYPES


def paper_key(d):
    for i in d.get("identifier", []):
        m = re.match(r"arXiv:(\d{4}\.\d{4,5})$", i)
        if m:
            return "arXiv:" + m.group(1)
    return d["bibcode"]


def check_new(papers):
    """Compare first-author papers with KNOWN; write NEW_MD if something is new."""
    known = set(json.load(open(KNOWN))) if KNOWN.exists() else None
    keys = {paper_key(d): d for d in papers}
    if known is None:                      # first run: just record the baseline
        json.dump(sorted(keys), open(KNOWN, "w"), indent=1)
        return
    new = [d for k, d in keys.items() if k not in known]
    if not new:
        return
    lines = ["A new first-author paper appeared in the SciX library. Consider adding a Research Highlight card "
             "to `index.html` (copy an existing `.hl-card`; figures go in `assets/highlights/`).", ""]
    for d in new:
        lines.append(f"- **{d['title'][0]}** — [SciX](https://scixplorer.org/abs/{d['bibcode']}/abstract)")
    NEW_MD.write_text("\n".join(lines) + "\n")
    json.dump(sorted(set(known) | set(keys)), open(KNOWN, "w"), indent=1)
    print(f"{len(new)} new first-author paper(s); wrote {NEW_MD.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", help="read docs from this JSON file instead of the API")
    args = ap.parse_args()
    if args.cache:
        docs = json.load(open(args.cache))
    else:
        token = os.environ.get("ADS_TOKEN")
        if not token:
            sys.exit("Set ADS_TOKEN or pass --cache FILE")
        docs = fetch(token)

    papers = [d for d in docs if is_first_author_paper(d)]
    n_first = len(papers)
    n_lib = sum(1 for d in docs if not is_tns(d))
    if n_first == 0 or n_lib == 0:
        sys.exit("No papers found; refusing to update the counts.")
    n_contrib = max(0, round((n_lib - n_first - MENTORED) / 10)) * 10

    src = INDEX.read_text()
    new = re.sub(r'(<span id="n-first">)[^<]*(</span>)', rf"\g<1>{n_first}\g<2>", src)
    new = re.sub(r'(<span id="n-contrib">)[^<]*(</span>)', rf"\g<1>~{n_contrib}\g<2>", new)
    check_new(papers)
    print(f"library (no TNS): {n_lib}; first-author: {n_first}; contributed ~{n_contrib}")
    if new == src:
        print("No change.")
        return
    INDEX.write_text(new)
    print("Updated index.html.")


if __name__ == "__main__":
    main()
