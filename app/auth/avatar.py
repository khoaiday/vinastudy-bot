"""Avatar generation: cartoon filter + character frame composite."""
import io
import base64
import logging
import math
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

from app.config import CHARACTERS

logger = logging.getLogger(__name__)


# ── Cartoon filter (Pillow, no external API needed) ────────────────────

def apply_cartoon_filter(img: Image.Image) -> Image.Image:
    """Chuyển ảnh chụp thành phong cách hoạt hình (posterize + smooth edge)."""
    img = img.convert("RGB")

    # 1. Làm mịn bằng median blur
    smooth = img.filter(ImageFilter.MedianFilter(size=5))

    # 2. Posterize: giảm màu xuống 5 mức → tạo hiệu ứng cartoon màu phẳng
    def posterize(image, levels=5):
        lut = []
        for i in range(256):
            lut.append(int(round(i / 255 * (levels - 1))) * (255 // (levels - 1)))
        lut3 = lut * 3
        return image.point(lut3)

    posterized = posterize(smooth, levels=5)

    # 3. Tăng độ bão hòa màu
    saturated = ImageEnhance.Color(posterized).enhance(1.8)

    # 4. Tăng độ tương phản nhẹ
    contrasted = ImageEnhance.Contrast(saturated).enhance(1.3)

    # 5. Tạo edge (đường viền) từ ảnh gốc
    gray = img.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda p: 0 if p > 30 else 255)   # binary edges

    # 6. Blend: overlay edges lên cartoon
    edges_rgb = edges.convert("RGB")
    result = Image.blend(contrasted, edges_rgb, alpha=0.12)

    return result


def crop_circle(img: Image.Image, size: int = 256) -> Image.Image:
    """Cắt ảnh thành hình tròn với kích thước chuẩn."""
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img_rgba = img.convert("RGBA")
    result.paste(img_rgba, mask=mask)
    return result


def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def make_character_frame(character_type: str, face_img: Image.Image,
                         size: int = 400) -> Image.Image:
    """Ghép ảnh mặt hoạt hình vào khung nhân vật theo theme."""
    cfg = CHARACTERS.get(character_type, CHARACTERS["chien_binh"])
    color  = hex_to_rgb(cfg["color"])
    bg_hex = cfg["bg"]
    bg_rgb = hex_to_rgb(bg_hex)
    emoji  = cfg["emoji"]
    name   = cfg["name"]

    # Tạo canvas
    canvas = Image.new("RGBA", (size, size), (*bg_rgb, 255))
    draw   = ImageDraw.Draw(canvas)

    # --- Background gradient (radial glow) ---
    cx, cy = size // 2, size // 2
    for r in range(cx, 0, -1):
        alpha = int(50 * (1 - r / cx))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, alpha))

    # --- Hexagon frame ---
    def hex_points(cx, cy, r, offset=0):
        return [
            (cx + r * math.cos(math.radians(60*i + offset)),
             cy + r * math.sin(math.radians(60*i + offset)))
            for i in range(6)
        ]

    outer = hex_points(cx, cy - 20, 165, -90)
    inner = hex_points(cx, cy - 20, 158, -90)
    draw.polygon(outer, fill=(*color, 40))
    draw.line(outer + [outer[0]], fill=(*color, 200), width=3)

    # --- Decorative corner lines ---
    for i in range(4):
        angle = math.radians(45 + 90 * i)
        x1 = cx + 170 * math.cos(angle)
        y1 = (cy - 20) + 170 * math.sin(angle)
        x2 = cx + 185 * math.cos(angle)
        y2 = (cy - 20) + 185 * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=(*color, 180), width=2)

    # --- Face circle (160px, centered slightly above midpoint) ---
    face_size  = 160
    face_round = crop_circle(face_img, face_size)
    face_x = (size - face_size) // 2
    face_y = size // 2 - face_size // 2 - 30
    canvas.paste(face_round, (face_x, face_y), face_round)

    # --- Glow ring around face ---
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    fc_x = face_x + face_size // 2
    fc_y = face_y + face_size // 2
    for w in range(8, 0, -1):
        rd.ellipse([fc_x - face_size//2 - w, fc_y - face_size//2 - w,
                    fc_x + face_size//2 + w, fc_y + face_size//2 + w],
                   outline=(*color, 30 * w), width=2)
    canvas = Image.alpha_composite(canvas, ring)
    draw = ImageDraw.Draw(canvas)

    # --- Character name banner ---
    banner_y = face_y + face_size + 16
    banner_h  = 32
    draw.rectangle([cx - 90, banner_y, cx + 90, banner_y + banner_h],
                   fill=(*color, 180), outline=(*color, 255), width=1)
    # Text (fallback to basic if no font)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    txt = name.upper()
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, banner_y + (banner_h - th) // 2),
              txt, fill=(0, 0, 0), font=font)

    # --- XP/Level placeholder bar ---
    bar_y = banner_y + banner_h + 10
    draw.rectangle([cx - 70, bar_y, cx + 70, bar_y + 6],
                   fill=(30, 30, 60), outline=(*color, 100), width=1)
    draw.rectangle([cx - 70, bar_y, cx - 70 + 100, bar_y + 6],
                   fill=(*color, 220))

    # --- Corner dots (cyberpunk decoration) ---
    dots = [(16, 16), (size-16, 16), (16, size-16), (size-16, size-16)]
    for dx, dy in dots:
        draw.ellipse([dx-4, dy-4, dx+4, dy+4], fill=(*color, 180))
        draw.ellipse([dx-7, dy-7, dx+7, dy+7], outline=(*color, 80), width=1)

    return canvas.convert("RGB")


# ── Base64 helpers ──────────────────────────────────────────────────────

def b64_to_image(b64: str) -> Image.Image:
    data = base64.b64decode(b64.split(",")[-1])
    return Image.open(io.BytesIO(data))


def image_to_b64(img: Image.Image, fmt="JPEG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=88)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


# ── Main pipeline ───────────────────────────────────────────────────────

def generate_avatar_pipeline(face_b64: str, character_type: str) -> dict:
    """
    Input:  base64 ảnh mặt học sinh (đã crop hình tròn từ client)
    Output: {
        cartoon_b64: str,   # ảnh mặt hoạt hình
        final_b64:   str,   # avatar hoàn chỉnh (face + character frame)
    }
    """
    try:
        face_img    = b64_to_image(face_b64)
        cartoon     = apply_cartoon_filter(face_img)
        cartoon_b64 = image_to_b64(cartoon)
        final_img   = make_character_frame(character_type, cartoon, size=400)
        final_b64   = image_to_b64(final_img)
        return {"ok": True, "cartoon_b64": cartoon_b64, "final_b64": final_b64}
    except Exception as e:
        logger.error(f"Avatar generation error: {e}")
        return {"ok": False, "error": str(e)}
