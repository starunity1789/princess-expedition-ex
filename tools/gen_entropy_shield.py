"""3.26：生成「逆熵行星护盾」（building_atb_entropy_shield）的外观与图标。

用法：python gen_entropy_shield.py <群星安装目录> <Guilli's Planet Modifiers and Features 目录> <MOD 根目录>

- 护盾模型与贴图：照搬 Guilli's Planet Modifiers and Features（创意工坊 865040033）的先驱者行星护盾
  （gpm_shielded_planet.mesh + 三张贴图），改名为 atb_entropy_shield_*，与 GPM 同时启用也不会重名
- 护盾是挂在星球位置上的环境物体（ambient object），和 GPM 的做法一样：模型大小固定，所以按星球大小
  （卫星另算）各做一个。大小公式取自 GPM 的先驱者护盾：0.4 × 星球大小 + 0.05；卫星的显示大小是同尺寸
  行星的 MOON_SCALE = 0.7 倍
- 本 MOD 把星体缩小到 1/8（tools/gen_celestial_scale.py 的 BODY），护盾跟着 × CELESTIAL_BODY
- 图标：原版行星护盾发生器图标，颜色加深 55%（RGB × 0.45，透明度不变）

群星或 GPM 更新后重新运行即可。
"""
import shutil
import struct
import sys
from pathlib import Path

from PIL import Image

GAME = Path(sys.argv[1])
GPM = Path(sys.argv[2])
MOD = Path(sys.argv[3])

SIZES = range(1, 41)          # planet_size 1～40（40 以上按 40）
MOON_SCALE = 0.7              # 原版 NGraphics.MOON_SCALE
PLANET_PLANE = -150           # 原版 NGraphics.DEFAULT_PLANET_PLANE
FLAG = "atb_entropy_shield_flag"
BUILDING = "building_atb_entropy_shield"
HEADER = "# 皇女的远征军EX 3.26：逆熵行星护盾的外观。由 tools/gen_entropy_shield.py 生成，请勿手改。\n"


CELESTIAL_BODY = 1 / 8       # 与 tools/gen_celestial_scale.py 的 BODY 一致（星体缩小）


def shield_scale(size: float) -> float:
    return round((0.4 * size + 0.05) * CELESTIAL_BODY, 4)


def key(moon: bool, size: int) -> str:
    return f"atb_entropy_shield_{'moon' if moon else 'planet'}_{size:02d}"


def write(rel: str, text: str) -> None:
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))
    print("generated", rel)


def write_dds(img: Image.Image, path: Path) -> None:
    """与 tools/make_art.py 相同：未压缩 32 位 BGRA DDS，无 mipmap。"""
    img = img.convert("RGBA")
    w, h = img.size
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x8
    header = struct.pack("<4sIIIIIII", b"DDS ", 124, flags, h, w, w * 4, 0, 0)
    header += b"\x00" * 44
    header += struct.pack("<IIIIIIII", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
    r, g, b, a = img.split()
    path.write_bytes(header + Image.merge("RGBA", (b, g, r, a)).tobytes())


# ---------------------------------------------------------------- 模型与贴图（照搬 GPM）
src = GPM / "gfx/models/planets"
dst = MOD / "gfx/models/planets"
dst.mkdir(parents=True, exist_ok=True)
shutil.copyfile(src / "gpm_shielded_planet.mesh", dst / "atb_entropy_shield.mesh")
TEX = {
    "pm_planet_shield_lower_diffuse.dds": "atb_entropy_shield_lower_diffuse.dds",
    "pm_planet_shield_diffuse.dds": "atb_entropy_shield_diffuse.dds",
    "pm_planet_shield_clouds.dds": "atb_entropy_shield_clouds.dds",
}
for a, b in TEX.items():
    shutil.copyfile(src / a, dst / b)
print("copied mesh + 3 textures from GPM")

write("gfx/models/planets/atb_entropy_shield.gfx", HEADER + """# 照搬 GPM 的 gpm_planet_shield_PREC_ambient_mesh（先驱者行星护盾），只改了名字

objectTypes = {
	pdxmesh = {
		name = "atb_entropy_shield_mesh"
		file = "gfx/models/planets/atb_entropy_shield.mesh"
		animation = { id = "idle"	type = "shielded_planet_idle" }
		scale = 1.0

		meshsettings = {
			name = "planet_geosphereShape"
			texture_diffuse = "atb_entropy_shield_lower_diffuse.dds"
			texture_normal = "nonormal.dds"
			texture_specular = "nospec.dds"
			shader = "PdxMeshExtraDimensionalShip"
		}
		meshsettings = {
			name = "polesShape"
			texture_diffuse = "atb_entropy_shield_diffuse.dds"
			texture_normal = "nonormal.dds"
			texture_specular = "nospec.dds"
			shader = "PdxMeshExtraDimensionalShip"
		}
		meshsettings = {
			name = "clouds_geosphereShape"
			texture_diffuse = "atb_entropy_shield_clouds.dds"
			texture_normal = "nonormal.dds"
			texture_specular = "nospec.dds"
		}
		meshsettings = {
			name = "clouds_shadow_geosphereShape"
			texture_diffuse = "atb_entropy_shield_clouds.dds"
			texture_normal = "nonormal.dds"
			texture_specular = "nospec.dds"
			shader = "Collision"	# 用这个着色器把云影藏起来（GPM 原样）
		}
	}
}
""")

# ---------------------------------------------------------------- 实体
pos, scl, amb = [], [], []
for moon in (False, True):
    for s in SIZES:
        k = key(moon, s)
        shown = s * MOON_SCALE if moon else s
        pos.append(f"""entity = {{
	name = "{k}_entity"
	cull_radius = 500
	locator = {{ name = "loc1" position = {{ 0 {PLANET_PLANE} 0 }} rotation = {{ 0 0 0 }} }}
	attach = {{ "loc1" = "{k}_scaling_entity" }}
	scale = 1.0
}}
""")
        scl.append(f"""entity = {{
	name = "{k}_scaling_entity"
	pdxmesh = "atb_entropy_shield_mesh"
	default_state = "idle"
	state = {{ name = "idle" animation = "idle" time_offset = {{ 0 100 }} animation_speed = 0.65 }}
	game_data = {{
		bloom_factor = 1
		uv_animation_speed = 0.65
		uv_animation_direction = {{ 0.0 0.25 }}
	}}
	scale = {shield_scale(shown)}	# {'卫星' if moon else '行星'}大小 {s}
}}
""")
        amb.append(f"""ambient_object = {{
	name = "{k}"
	entity = "{k}_entity"
	selectable = no
	show_name = no
}}
""")

write("gfx/models/planets/atb_entropy_shield_position.asset",
      HEADER + f"# 环境物体在星球的轨道平面上，往下挪 {-PLANET_PLANE}（原版 DEFAULT_PLANET_PLANE）对齐星球\n\n" + "\n".join(pos))
write("gfx/models/planets/atb_entropy_shield_scaling.asset",
      HEADER + "# 护盾大小 = (0.4 × 星球大小 + 0.05) × 1/8（卫星的大小再 × 0.7；1/8 是本 MOD 的星体缩小比例）\n\n" + "\n".join(scl))
write("common/ambient_objects/atb_entropy_shield_ambient_objects.txt", HEADER + "\n" + "\n".join(amb))

# ---------------------------------------------------------------- 脚本效果
def ladder(moon: bool) -> str:
    out = []
    for i, s in enumerate(reversed(SIZES)):
        cond = f"planet_size >= {s}" if s == SIZES[-1] else f"planet_size = {s}"
        if s == SIZES[0]:
            cond = f"planet_size <= {s}"
        kw = "if" if i == 0 else "else_if"
        out.append(f"\t\t{kw} = {{ limit = {{ {cond} }} create_ambient_object = {{ type = \"{key(moon, s)}\" location = this }} }}")
    return "\n".join(out)


write("common/scripted_effects/atb_entropy_shield_effects.txt", HEADER + f"""
# 星系范围：清掉本星系所有逆熵护盾外观，再给每个有该建筑的非人造星球重新挂上
# （环境物体只能按星系找，按星系整体刷新最稳妥）。scope = 星系。人造星球（栖息地、环形世界等）不挂
atb_entropy_shield_refresh_system = {{
	every_system_ambient_object = {{
		limit = {{ has_ambient_object_flag = {FLAG} }}
		destroy_ambient_object = this
	}}
	every_system_planet = {{
		limit = {{
			has_building = {BUILDING}
			is_artificial = no
		}}
		atb_entropy_shield_add_visual = yes
	}}
}}

# scope = 星球：按星球大小挂一个护盾环境物体
atb_entropy_shield_add_visual = {{
	save_event_target_as = atb_entropy_shield_planet
	if = {{
		limit = {{ is_moon = yes }}
{ladder(True)}
	}}
	else = {{
{ladder(False)}
	}}
	last_created_ambient_object = {{
		set_location = {{ target = event_target:atb_entropy_shield_planet }}
		set_ambient_object_flag = {FLAG}
	}}
}}
""")

# ---------------------------------------------------------------- 图标：原版图标加深 55%
icon = Image.open(GAME / "gfx/interface/icons/buildings/building_planetary_shield_generator.dds").convert("RGBA")
r, g, b, a = icon.split()
dark = Image.merge("RGBA", tuple(ch.point(lambda v: round(v * 0.45)) for ch in (r, g, b)) + (a,))
write_dds(dark, MOD / f"gfx/interface/icons/buildings/{BUILDING}.dds")
print(f"generated gfx/interface/icons/buildings/{BUILDING}.dds ({icon.size[0]}x{icon.size[1]})")
