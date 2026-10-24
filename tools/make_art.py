"""Generate Stellaris art assets for the 皇女的远征军 mod from the user's source images."""
import struct
import sys
from pathlib import Path

from PIL import Image

SRC = Path(sys.argv[1])
MOD = Path(sys.argv[2])


def write_dds(img: Image.Image, path: Path) -> None:
    """Uncompressed 32-bit BGRA DDS, legacy header, no mipmaps."""
    img = img.convert("RGBA")
    w, h = img.size
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x8  # CAPS|HEIGHT|WIDTH|PIXELFORMAT|PITCH
    header = struct.pack("<4sIIIIIII", b"DDS ", 124, flags, h, w, w * 4, 0, 0)
    header += b"\x00" * 44  # reserved1
    # pixel format: RGB | ALPHAPIXELS
    header += struct.pack("<IIIIIIII", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)  # caps: TEXTURE
    r, g, b, a = img.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()
    path.write_bytes(header + data)


def fit(img: Image.Image, size: tuple[int, int], pad: float = 0.0) -> Image.Image:
    """Scale to fit inside size (keeping aspect), centered on transparent canvas."""
    img = img.convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    tw, th = int(size[0] * (1 - pad)), int(size[1] * (1 - pad))
    scale = min(tw / img.width, th / img.height)
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(img, ((size[0] - img.width) // 2, (size[1] - img.height) // 2), img)
    return canvas


def crop_ratio(img: Image.Image, size: tuple[int, int], top: int) -> Image.Image:
    """Full-width crop with the target aspect ratio starting at `top`, then resize."""
    w = img.width
    h = round(w * size[1] / size[0])
    top = max(0, min(top, img.height - h))
    return img.crop((0, top, w, top + h)).resize(size, Image.LANCZOS)


relic = Image.open(SRC / "宝物.png")
cover = Image.open(SRC / "封面.png").convert("RGBA")

write_dds(fit(relic, (150, 150), pad=0.06), MOD / "gfx/interface/icons/relics/r_atb_princess_seal.dds")
write_dds(fit(relic, (43, 41), pad=0.02), MOD / "gfx/interface/icons/origins/origin_atb_princess_expedition.dds")
write_dds(fit(relic, (25, 25)), MOD / "gfx/interface/icons/modifiers/mod_atb_princess_seal.dds")
write_dds(crop_ratio(cover, (220, 115), top=0), MOD / "gfx/event_pictures/origins/origin_atb_princess_expedition.dds")
write_dds(crop_ratio(cover, (450, 150), top=60), MOD / "gfx/event_pictures/atb_expedition.dds")

thumb = cover.convert("RGB").resize((512, 512), Image.LANCZOS)
thumb.save(MOD / "thumbnail.png", optimize=True)

# previews for checking
prev = Path(sys.argv[3])
prev.mkdir(exist_ok=True)
crop_ratio(cover, (220, 115), top=0).save(prev / "origin_picture.png")
crop_ratio(cover, (450, 150), top=60).save(prev / "event_picture.png")
fit(relic, (150, 150), pad=0.06).save(prev / "relic.png")
print("ok", (MOD / "thumbnail.png").stat().st_size)
