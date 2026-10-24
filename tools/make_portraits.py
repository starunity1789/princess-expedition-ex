"""把两位元首的高清立绘转成群星肖像 DDS（半身 + 全身，575x380，未压缩 BGRA）。

用法：python make_portraits.py <立绘文件夹> <MOD 根目录> <预览输出文件夹>
半身裁切框按原图人物位置手调，改图后要重新核对 CROPS。
"""
import struct
import sys
from pathlib import Path

from PIL import Image

SRC = Path(sys.argv[1])
MOD = Path(sys.argv[2])
PREV = Path(sys.argv[3])
SIZE = (575, 380)

# 源文件名 -> (肖像文件名, 半身裁切框 x0,y0,x1,y1；比例约 575:380)
CROPS = {
    "融心演算.png": ("rongxin", (172, 242, 982, 777)),
    "泰阿瑞亚-星之心.png": ("taiaria", (75, 0, 885, 535)),
}


def write_dds(img: Image.Image, path: Path) -> None:
    """Uncompressed 32-bit BGRA DDS, legacy header, no mipmaps."""
    img = img.convert("RGBA")
    w, h = img.size
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x8  # CAPS|HEIGHT|WIDTH|PIXELFORMAT|PITCH
    header = struct.pack("<4sIIIIIII", b"DDS ", 124, flags, h, w, w * 4, 0, 0)
    header += b"\x00" * 44  # reserved1
    header += struct.pack("<IIIIIIII", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)  # caps: TEXTURE
    r, g, b, a = img.split()
    path.write_bytes(header + Image.merge("RGBA", (b, g, r, a)).tobytes())


def half_body(img: Image.Image, box) -> Image.Image:
    return img.crop(box).resize(SIZE, Image.LANCZOS)


def full_body(img: Image.Image) -> Image.Image:
    """整张立绘等比缩到画布高度，水平居中，底部对齐。"""
    scale = SIZE[1] / img.height
    small = img.resize((round(img.width * scale), SIZE[1]), Image.LANCZOS)
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(small, ((SIZE[0] - small.width) // 2, 0))
    return canvas


PREV.mkdir(parents=True, exist_ok=True)
for src_name, (key, box) in CROPS.items():
    img = Image.open(SRC / src_name).convert("RGBA")
    for suffix, out in (("", half_body(img, box)), ("_full", full_body(img))):
        write_dds(out, MOD / f"gfx/models/portraits/atbgp/{key}{suffix}.dds")
        bg = Image.new("RGBA", SIZE, (30, 34, 48, 255))
        bg.alpha_composite(out)
        bg.save(PREV / f"{key}{suffix}.png")
print("ok")
