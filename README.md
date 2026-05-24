# 35 Gulf Petroleum — site assets

Public image assets for the company profile page (`index.html`).

## Images (used on the page)

| File | Use |
|------|-----|
| `assets/images/p1_0.jpg` | Hero background |
| `assets/images/p4_1.jpg` | Leadership — Chatchai |
| `assets/images/p4_0.jpg` | Leadership — Dr. Khalid |
| `assets/images/p8_0.jpg` | Rossukon field photo |
| `assets/pdf-images/rossukon_2.png` | Rossukon location map |
| `assets/images/yetagun.png` | Yetagun platforms diagram |

Operations cards use Unsplash URLs embedded in the HTML.

## Standalone HTML

Send customers **`index.html` only** (~1.2 MB). All images are embedded directly in the HTML (no JavaScript required), so they work when the file is opened locally — including on iPhone.

**iPhone tip:** If images still do not appear, the file may be opening in **Quick Look preview** (from Mail or Files), which does not fully support HTML. Ask the recipient to tap **Share → Open in Safari**, or send this link instead:

**https://qailab-qa.github.io/35gulfpetroleum/**

To rebuild after editing: `python build_standalone.py`
