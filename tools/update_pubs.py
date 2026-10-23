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
The Research Highlights cards are hand-written and never touched.
"""
import argparse, json, os, pathlib, re, sys

LIB_ID = "7eLaCipeRIuYIkoZK0YHaA"
ME_NORM = "Zhuang, M"               # first_author_norm prefix
MENTORED = 5                        # (co-)mentored papers; update by hand (and the text in index.html)
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
FL = "bibcode,first_author_norm,bibstem,doctype,identifier"

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

    n_first = sum(1 for d in docs if is_first_author_paper(d))
    n_lib = sum(1 for d in docs if not is_tns(d))
    if n_first == 0 or n_lib == 0:
        sys.exit("No papers found; refusing to update the counts.")
    n_contrib = max(0, round((n_lib - n_first - MENTORED) / 10)) * 10

    src = INDEX.read_text()
    new = re.sub(r'(<span id="n-first">)[^<]*(</span>)', rf"\g<1>{n_first}\g<2>", src)
    new = re.sub(r'(<span id="n-contrib">)[^<]*(</span>)', rf"\g<1>~{n_contrib}\g<2>", new)
    print(f"library (no TNS): {n_lib}; first-author: {n_first}; contributed ~{n_contrib}")
    if new == src:
        print("No change.")
        return
    INDEX.write_text(new)
    print("Updated index.html.")


if __name__ == "__main__":
    main()
