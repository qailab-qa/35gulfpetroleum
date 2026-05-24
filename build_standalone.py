"""Build a self-contained index.html with embedded images (works from file://)."""
import base64
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Source: last URL-based index (mobile-ready) from git
html = subprocess.check_output(
    ["git", "show", "65de5fa:index.html"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
)

IMAGES = {
    "hero": ("assets/images/p1_0.jpg", "image/jpeg"),
    "p4_1": ("assets/images/p4_1.jpg", "image/jpeg"),
    "p4_0": ("assets/images/p4_0.jpg", "image/jpeg"),
    "ops_drilling": ("assets/images/ops-drilling.jpg", "image/jpeg"),
    "ops_exploration": ("assets/images/ops-exploration.jpg", "image/jpeg"),
    "ops_logistics": ("assets/images/ops-logistics.jpg", "image/jpeg"),
    "p8_0": ("assets/images/p8_0.jpg", "image/jpeg"),
    "rossukon_2": ("assets/pdf-images/rossukon_2.png", "image/png"),
    "yetagun": ("assets/images/yetagun.png", "image/png"),
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

# Ensure Unsplash cache files exist (download if missing)
import urllib.request

for key in ("ops_drilling", "ops_exploration", "ops_logistics"):
    rel, _ = IMAGES[key]
    path = ROOT / rel
    if not path.exists():
        url = [u for u, k in URL_TO_KEY.items() if k == key][0]
        print(f"Downloading {rel}...")
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)

# Hero background: placeholder in CSS, applied via JS
html = re.sub(
    r"url\('https://raw\.githubusercontent\.com/qailab-qa/35gulfpetroleum/main/assets/images/p1_0\.jpg'\)",
    "url('')",
    html,
)

# Replace img tags with placeholders (no lazy loading)
for url, key in URL_TO_KEY.items():
    if key == "hero":
        continue
    pattern = re.compile(
        rf'<img\s+src="{re.escape(url)}"\s+alt="([^"]*)"\s+loading="lazy"\s*/>'
    )
    html = pattern.sub(rf'<img data-embedded="{key}" alt="\1" />', html)

# Scroll-reveal: always show content (critical for file:// / shared HTML)
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

html = html.replace(
    "    .leader-card img {",
    """    img[data-embedded] {
      display: block;
      width: 100%;
      min-height: 120px;
      background: var(--bg-muted);
    }
    .leader-card img {""",
)

# Build embedded payload scripts
embed_scripts = []
for key, (rel, mime) in IMAGES.items():
    data = (ROOT / rel).read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    embed_scripts.append(
        f'<script type="text/plain" id="img-{key}" data-mime="{mime}">{b64}</script>'
    )

loader = """
<script>
(function () {
  function dataUri(id) {
    var node = document.getElementById('img-' + id);
    if (!node) return '';
    return 'data:' + node.getAttribute('data-mime') + ';base64,' + node.textContent.trim();
  }

  document.querySelectorAll('[data-embedded]').forEach(function (el) {
    var uri = dataUri(el.getAttribute('data-embedded'));
    if (uri && el.tagName === 'IMG') el.src = uri;
  });

  var heroUri = dataUri('hero');
  var heroBg = document.querySelector('.hero-bg');
  if (heroUri && heroBg) {
    heroBg.style.backgroundImage =
      'linear-gradient(160deg, rgba(214,161,0,0.06) 0%, transparent 45%), ' +
      'radial-gradient(ellipse 80% 60% at 70% 40%, rgba(221,29,33,0.08) 0%, transparent 60%), ' +
      'linear-gradient(to bottom, rgba(12,13,14,0.25) 0%, rgba(12,13,14,0.88) 72%, var(--bg-base) 100%), ' +
      "url('" + heroUri + "')";
    heroBg.style.backgroundPosition = 'center';
    heroBg.style.backgroundSize = 'cover';
    heroBg.style.backgroundRepeat = 'no-repeat';
  }
})();
</script>
"""

html = html.replace("</body>", "\n".join(embed_scripts) + loader + "\n</body>")

out = ROOT / "index.html"
out.write_text(html, encoding="utf-8")
size_mb = out.stat().st_size / (1024 * 1024)
print(f"Wrote {out} ({size_mb:.2f} MB)")
