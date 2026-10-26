"""把三个列强的 LOGO 原图转成群星国旗图标 DDS（128x128，未压缩 BGRA）。

用法：python make_flags.py <LOGO 文件夹> <MOD 根目录>

原图是白色透明的 PNG。群星的国旗图标不会被颜色槽染色，所以白色会原样显示在
纯色底上；底色和图标的对应关系写在 gen_great_powers.py 的 EMPIRES[*]['flag'] 里。
图标尺寸与原版 flags/ 下的一致：128x128、未压缩 32 位 BGRA、无 mipmap。
"""
import struct
import sys
from pathlib import Path

from PIL import Image

SRC = Path(sys.argv[1])
MOD = Path(sys.argv[2])
SIZE = (128, 128)
# 图标在画布内留出的边距比例，避免贴边被 UI 圆角切掉
PAD = 0.06

# 源文件名 -> 输出文件名（与 gen_great_powers.py 的 flag.file 对应）
FLAGS = {
    "LOGO_01_全身焰鹿_白色透明.png": "flag_atbgp_1.dds",   # 燃烧白鹿军团
    "LOGO_02_九重星环_白色透明.png": "flag_atbgp_2.dds",   # 远星同盟组织
    "LOGO_03_皇权晶冠_白色透明.png": "flag_atbgp_3.dds",   # 大君主同盟领地
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


def fit(img: Image.Image) -> Image.Image:
    """按 alpha 的实际边界裁掉空白，再等比缩放居中到画布。"""
    img = img.convert("RGBA")
    box = img.getbbox()
    if box:
        img = img.crop(box)
    inner = (round(SIZE[0] * (1 - 2 * PAD)), round(SIZE[1] * (1 - 2 * PAD)))
    scale = min(inner[0] / img.width, inner[1] / img.height)
    small = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(small, ((SIZE[0] - small.width) // 2, (SIZE[1] - small.height) // 2))
    return canvas


for src_name, out_name in FLAGS.items():
    src = SRC / src_name
    if not src.exists():
        sys.exit(f"缺少原图：{src}")
    write_dds(fit(Image.open(src)), MOD / "flags/atbgp" / out_name)
    print("ok", out_name)
