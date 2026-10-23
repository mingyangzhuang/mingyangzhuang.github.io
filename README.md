# mingyangzhuang.github.io

Source for my personal academic homepage, published with GitHub Pages.

Live at: **https://mingyangzhuang.github.io**

## What's here

- `index.html` — the whole site (single page: Research, Publications, CV, Contact)
- `style.css` — styling, including automatic light/dark mode
- `assets/` — put your photo here as `photo.jpg` if you want a real headshot instead of the initials avatar

No build step, no dependencies — it's plain HTML/CSS. Just edit and push.

## First-time setup (do this once)

From your own machine (with your GitHub login/SSH key set up), in the folder these files are in:

```bash
git init
git add .
git commit -m "Initial homepage"
git branch -M main
git remote add origin https://github.com/mingyangzhuang/mingyangzhuang.github.io.git
git push -u origin main
```

(If this is already done and you just have new local commits to publish, skip straight to `git push`.)

Then go to the repo's **Settings → Pages** on GitHub. For a repo named `<username>.github.io`,
Pages is usually enabled automatically from the `main` branch; if not, set the source to
`main` / `(root)`. Your site will be live at `https://mingyangzhuang.github.io` within a
minute or two.

## After the first push (making changes)

```bash
git add .
git commit -m "Describe what changed"
git push
```

GitHub Pages rebuilds automatically a few seconds after each push.

## Publication counts (auto-updated from SciX)

- The numbers in the Publications intro (`<span id="n-first">` and `<span id="n-contrib">` in `index.html`)
  are rewritten by `tools/update_pubs.py` from the
  [SciX library](https://scixplorer.org/public-libraries/7eLaCipeRIuYIkoZK0YHaA). Contributed = library size
  without TNS reports, minus first-author papers, minus `MENTORED`, rounded to ten.
- The number of (co-)mentored papers is edited by hand: `MENTORED` in `tools/update_pubs.py` and the text in `index.html`.
- A GitHub Action (`.github/workflows/update-pubs.yml`) runs it on the 1st of every second month and commits
  any change. It needs a repo secret named `ADS_TOKEN` (Settings -> Secrets and variables -> Actions).
  It can also be run manually from the Actions tab.
- Run it by hand: `ADS_TOKEN=xxxx python3 tools/update_pubs.py`
- The **Research Highlights** cards are hand-written HTML (figures in `assets/highlights/`) and are never
  touched by the script.
- `tools/fetch_papers.py` downloads arXiv PDFs/sources into the git-ignored `_papers/` folder.

## Remaining optional touches

- [ ] Add a real photo at `assets/photo.jpg` and swap the placeholder avatar `<div>` in `index.html`
      for `<img class="avatar" src="assets/photo.jpg" alt="Ming-Yang Zhuang">`
- [ ] Add real News/Projects updates over time

## Local preview

Open `index.html` directly in a browser, or serve it locally:

```bash
python3 -m http.server 8000
```

then visit `http://localhost:8000`.
