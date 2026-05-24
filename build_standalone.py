"""Build self-contained index.html — no JS required for images (iPhone-safe)."""
import base64
import io
import re
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent

html = subprocess.check_output(
    ["git", "show", "65de5fa:index.html"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
)

# rel path -> (mime, compress opts)
IMAGES = {
    "hero": ("assets/images/p1_0.jpg", "image/jpeg", {"max_width": 1920, "jpeg_quality": 82}),
    "p4_1": ("assets/images/p4_1.jpg", "image/jpeg", {"max_width": 900, "jpeg_quality": 82}),
    "p4_0": ("assets/images/p4_0.jpg", "image/jpeg", {"max_width": 900, "jpeg_quality": 82}),
    "ops_drilling": ("assets/images/ops-drilling.jpg", "image/jpeg", {"max_width": 900, "jpeg_quality": 80}),
    "ops_exploration": ("assets/images/ops-exploration.jpg", "image/jpeg", {"max_width": 900, "jpeg_quality": 80}),
    "ops_logistics": ("assets/images/ops-logistics.jpg", "image/jpeg", {"max_width": 900, "jpeg_quality": 80}),
    "p8_0": ("assets/images/p8_0.jpg", "image/jpeg", {"max_width": 1400, "jpeg_quality": 82}),
    "rossukon_2": ("assets/pdf-images/rossukon_2.png", "image/jpeg", {"max_width": 1000, "jpeg_quality": 85, "force_jpeg": True}),
    "yetagun": ("assets/images/yetagun.png", "image/jpeg", {"max_width": 1200, "jpeg_quality": 85, "force_jpeg": True}),
}

URL_TO_KEY = {
    "https://raw.githubusercontent.com/qailab-qa/35gulfpetroleum/main/assets/images/p1_0.jpg": "hero",
    "https://raw.githubusercontent.com/qailab-qa/35gulfpetroleum/main/assets/images/p4_1.jpg": "p4_1",
    "https://raw.githubusercontent.com/qailab-qa/35gulfpetroleum/main/assets/images/p4_0.jpg": "p4_0",
    "https://raw.githubusercontent.com/qailab-qa/35gulfpetroleum/main/assets/images/p8_0.jpg": "p8_0",
    "https://raw.githubusercontent.com/qailab-qa/35gulfpetroleum/main/assets/pdf-images/rossukon_2.png": "rossukon_2",
    "https://raw.githubusercontent.com/qailab-qa/35gulfpetroleum/main/assets/images/yetagun.png": "yetagun",
    "https://images.unsplash.com/photo-1513828583688-c52646db42da?w=800&q=80": "ops_drilling",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80": "ops_exploration",
    "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800&q=80": "ops_logistics",
}


def compress_bytes(path: Path, opts: dict) -> tuple[bytes, str]:
    max_width = opts.get("max_width", 1400)
    jpeg_quality = opts.get("jpeg_quality", 82)
    force_jpeg = opts.get("force_jpeg", False)

    img = Image.open(path)
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    buf = io.BytesIO()
    if force_jpeg or path.suffix.lower() in (".jpg", ".jpeg"):
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
        return buf.getvalue(), "image/jpeg"

    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), "image/png"


def to_data_uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


# Download Unsplash cache if missing
for key in ("ops_drilling", "ops_exploration", "ops_logistics"):
    rel, _, _ = IMAGES[key]
    path = ROOT / rel
    if not path.exists():
        url = [u for u, k in URL_TO_KEY.items() if k == key][0]
        print(f"Downloading {rel}...")
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)

# Build compressed data URIs
uris: dict[str, str] = {}
for key, (rel, _mime, opts) in IMAGES.items():
    path = ROOT / rel
    data, mime = compress_bytes(path, opts)
    uris[key] = to_data_uri(data, mime)
    print(f"{key}: {len(data) // 1024} KB ({mime})")

# Hero: embed directly in CSS (works without JavaScript — required for iOS Quick Look)
html = re.sub(
    r"url\('https://raw\.githubusercontent\.com/qailab-qa/35gulfpetroleum/main/assets/images/p1_0\.jpg'\)",
    f"url('{uris['hero']}')",
    html,
)

# Images: embed directly in src (no JS — required for iPhone)
for url, key in URL_TO_KEY.items():
    if key == "hero":
        continue
    pattern = re.compile(
        rf'<img\s+src="{re.escape(url)}"\s+alt="([^"]*)"\s+loading="lazy"\s*/>'
    )
    html = pattern.sub(rf'<img src="{uris[key]}" alt="\1" />', html)

# Scroll-reveal: visible by default
html = html.replace(
    """    .reveal {
      opacity: 0;
      transform: translateY(30px);
      transition: opacity 0.8s ease, transform 0.8s ease;
    }
    .reveal.visible { opacity: 1; transform: none; }""",
    """    .reveal {
      opacity: 1;
      transform: none;
    }
    .reveal.visible { opacity: 1; transform: none; }""",
)

out = ROOT / "index.html"
out.write_text(html, encoding="utf-8")
size_mb = out.stat().st_size / (1024 * 1024)
print(f"Wrote {out} ({size_mb:.2f} MB)")
