from pathlib import Path
from PIL import Image
import re

# ==========================================
# Configuration
# ==========================================

LAYERS_DIR = Path("assets/layers")
BASE_GIF = LAYERS_DIR / "L1.gif"
OUTPUT = Path("assets/banner.gif")

# ==========================================
# Check files
# ==========================================

if not BASE_GIF.exists():
    raise FileNotFoundError(f"Base GIF not found: {BASE_GIF}")

# ==========================================
# Find PNG overlay layers (L2.png, L3.png...)
# ==========================================

pattern = re.compile(r"L(\d+)\.png$", re.IGNORECASE)

overlay_layers = []

for file in LAYERS_DIR.iterdir():
    match = pattern.fullmatch(file.name)
    if match:
        layer = int(match.group(1))
        if layer >= 2:
            overlay_layers.append((layer, file))

overlay_layers.sort(key=lambda x: x[0])

print("Layers found:")
print(f"  L1 -> {BASE_GIF.name}")

for layer, file in overlay_layers:
    print(f"  L{layer} -> {file.name}")

# ==========================================
# Load overlays into memory
# ==========================================

overlay_cache = {}

for _, file in overlay_layers:
    overlay_cache[file] = Image.open(file).convert("RGBA")

# ==========================================
# Process GIF
# ==========================================

gif = Image.open(BASE_GIF)

frames = []

duration = gif.info.get("duration", 33)
loop = gif.info.get("loop", 0)

frame = 0

try:
    while True:

        current = gif.convert("RGBA")

        for _, file in overlay_layers:

            overlay = overlay_cache[file]

            if overlay.size != current.size:
                overlay = overlay.resize(current.size, Image.LANCZOS)

            current = Image.alpha_composite(current, overlay)

        frames.append(current)

        frame += 1
        gif.seek(frame)

except EOFError:
    pass

# ==========================================
# Save output
# ==========================================

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=loop,
    optimize=True,
)

print("\n✅ Banner generated successfully!")
print(f"Frames : {len(frames)}")
print(f"Saved  : {OUTPUT}")
