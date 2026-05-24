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

Send customers **`index.html` only** (~4 MB). All images are embedded inside the file and loaded via JavaScript, so they display when the file is opened locally on any computer — no internet connection or `assets` folder required.

To rebuild after editing the site: `python build_standalone.py`
