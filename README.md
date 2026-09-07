# mingyangzhuang.github.io

Source for my personal academic homepage, published with GitHub Pages.

Live at: **https://mingyangzhuang.github.io**

## What's here

- `index.html` — the whole site (single page: About, Research, Publications, CV, Projects & News, Contact)
- `style.css` — styling, including automatic light/dark mode
- `assets/cv.pdf` — CV, linked from the "Download CV" button
- `assets/` — also put your photo here as `photo.jpg` if you want a real headshot instead of the initials avatar

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

## Remaining optional touches

- [ ] Add a real photo at `assets/photo.jpg` and swap the placeholder avatar `<div>` in `index.html`
      for `<img class="avatar" src="assets/photo.jpg" alt="Ming-Yang Zhuang">`
- [ ] Keep `assets/cv.pdf` up to date as your CV changes
- [ ] Add more publications / update the "Selected Publications" list as new papers come out
      (the full list stays available via the ADS library link)
- [ ] Add real News/Projects updates over time

## Local preview

Open `index.html` directly in a browser, or serve it locally:

```bash
python3 -m http.server 8000
```

then visit `http://localhost:8000`.
