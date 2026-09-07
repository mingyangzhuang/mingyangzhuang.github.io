# mingyangzhuang.github.io

Source for my personal academic homepage, published with GitHub Pages.

Live at: **https://mingyangzhuang.github.io**

## What's here

- `index.html` — the whole site (single page: About, Research, Publications, CV, Projects & News, Contact)
- `style.css` — styling, including automatic light/dark mode
- `assets/` — put your photo (`photo.jpg`) and CV (`cv.pdf`) here

No build step, no dependencies — it's plain HTML/CSS. Just edit and push.

## First-time setup (do this once)

This repo was created empty. From your own machine (with your GitHub login/SSH key set up),
in the folder these files are in:

```bash
git init
git add .
git commit -m "Initial homepage"
git branch -M main
git remote add origin https://github.com/mingyangzhuang/mingyangzhuang.github.io.git
git push -u origin main
```

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

## Customize the content

Everything that still needs your real info is marked with an `edit me` tag in `index.html`
(search the file for `edit me` or `EDIT ME`). At minimum:

- [ ] Confirm your name/title in the `<header class="hero">` section
- [ ] Write your real bio/tagline
- [ ] Add a real photo at `assets/photo.jpg`, then swap the placeholder avatar `<div>` for
      `<img class="avatar" src="assets/photo.jpg" alt="Mingyang Zhuang">`
- [ ] Add your real CV as `assets/cv.pdf` (the "Download CV" button already links to it)
- [ ] Fill in your real Google Scholar / ADS / arXiv profile links in the hero links
- [ ] Replace the Research section with your actual research areas
- [ ] Replace the three placeholder publications with your real papers
- [ ] Fill in the CV section (education, positions, awards, skills)
- [ ] Replace the News and Projects placeholders with real updates
- [ ] Update the year range in Education/Positions once known

## Local preview

Open `index.html` directly in a browser, or serve it locally:

```bash
python3 -m http.server 8000
```

then visit `http://localhost:8000`.
