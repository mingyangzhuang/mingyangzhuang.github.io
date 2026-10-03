#!/usr/bin/env python3
"""Fetch Ming-Yang Zhuang's papers from the ADS library and download arXiv PDFs + sources.

Usage (from the repo root):
    ADS_TOKEN=xxxx python3 tools/fetch_papers.py

Outputs (git-ignored):
    _papers/library.json     metadata for every paper in the ADS library
    _papers/first_author.json  first-author subset (newest first)
    _papers/pdf/<arxiv>.pdf     arXiv PDF of each first-author paper
    _papers/src/<arxiv>.tar.gz  arXiv source (for original figure files)
"""
import json, os, re, sys, time, pathlib
import requests

LIB_ID = "7eLaCipeRIuYIkoZK0YHaA"
ME = "Zhuang, M"          # first_author_norm prefix
OUT = pathlib.Path(__file__).resolve().parent.parent / "_papers"
FL = ("bibcode,title,author,first_author_norm,pub,volume,page,year,pubdate,doi,"
      "identifier,citation_count,doctype,abstract")

def ads(token):
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {token}"
    r = s.get("https://api.adsabs.harvard.edu/v1/search/query",
              params={"q": f"docs(library/{LIB_ID})", "fl": FL, "rows": 2000,
                      "sort": "date desc"}, timeout=60)
    r.raise_for_status()
    return r.json()["response"]["docs"]

def arxiv_id(doc):
    for i in doc.get("identifier", []):
        m = re.match(r"arXiv:(\d{4}\.\d{4,5})", i)
        if m:
            return m.group(1)
    return None

def download(url, path):
    if path.exists() and path.stat().st_size > 0:
        return "cached"
    r = requests.get(url, timeout=120, headers={"User-Agent": "mingyang-homepage/1.0"})
    if r.status_code != 200:
        return f"HTTP {r.status_code}"
    path.write_bytes(r.content)
    time.sleep(3)  # be polite to arXiv
    return f"{len(r.content)//1024} KB"

def main():
    token = os.environ.get("ADS_TOKEN")
    if not token:
        sys.exit("Set ADS_TOKEN first, e.g.  ADS_TOKEN=xxxx python3 tools/fetch_papers.py")
    (OUT / "pdf").mkdir(parents=True, exist_ok=True)
    (OUT / "src").mkdir(parents=True, exist_ok=True)
    docs = ads(token)
    for d in docs:
        d["arxiv"] = arxiv_id(d)
    (OUT / "library.json").write_text(json.dumps(docs, indent=1, ensure_ascii=False))
    first = [d for d in docs if d.get("first_author_norm", "").startswith(ME)]
    (OUT / "first_author.json").write_text(json.dumps(first, indent=1, ensure_ascii=False))
    print(f"{len(docs)} papers in library, {len(first)} first-author")
    for d in first:
        a = d["arxiv"]
        title = d.get("title", ["?"])[0][:70]
        if not a:
            print(f"  [no arXiv] {d['bibcode']}  {title}")
            continue
        p = download(f"https://arxiv.org/pdf/{a}", OUT / "pdf" / f"{a}.pdf")
        s = download(f"https://arxiv.org/e-print/{a}", OUT / "src" / f"{a}.tar.gz")
        print(f"  {a}  pdf:{p}  src:{s}  {title}")
    print(f"Done -> {OUT}")

if __name__ == "__main__":
    main()
