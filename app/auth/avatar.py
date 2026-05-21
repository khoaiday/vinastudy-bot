"""Avatar generation: cartoon filter + full-body character composite."""
import io
import base64
import logging
import math
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

from app.config import CHARACTERS

logger = logging.getLogger(__name__)


# ── Cartoon filter ─────────────────────────────────────────────────────

def apply_cartoon_filter(img: Image.Image) -> Image.Image:
    """Chuyển ảnh chụp thành phong cách hoạt hình (posterize + smooth edge)."""
    img = img.convert("RGB")
    smooth = img.filter(ImageFilter.MedianFilter(size=5))

    def posterize(image, levels=5):
        lut = []
        for i in range(256):
            lut.append(int(round(i / 255 * (levels - 1))) * (255 // (levels - 1)))
        return image.point(lut * 3)

    posterized  = posterize(smooth, levels=5)
    saturated   = ImageEnhance.Color(posterized).enhance(1.8)
    contrasted  = ImageEnhance.Contrast(saturated).enhance(1.3)

    gray  = img.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda p: 0 if p > 30 else 255)
    result = Image.blend(contrasted, edges.convert("RGB"), alpha=0.12)
    return result


def crop_circle(img: Image.Image, size: int = 256) -> Image.Image:
    """Cắt ảnh thành hình tròn."""
    img  = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img.convert("RGBA"), mask=mask)
    return result


def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _load_font(size: int = 13):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ── Body drawing helpers ───────────────────────────────────────────────

def _body_chien_binh(draw, cx, bt, bb, color):
    """Chiến Binh: giáp vai rộng, kiếm bên phải, khiên bên trái."""
    bh = bb - bt
    # Shoulder pads
    draw.ellipse([cx-80, bt-8, cx-32, bt+32], fill=(*color, 230))
    draw.ellipse([cx+32, bt-8, cx+80, bt+32], fill=(*color, 230))
    # Chest plate
    draw.polygon([(cx-48, bt), (cx+48, bt),
                  (cx+38, bt+int(bh*.55)), (cx-38, bt+int(bh*.55))],
                 fill=(*color, 160))
    # Chest lines
    for i in range(3):
        y = bt + 18 + i * 18
        draw.line([(cx-32, y), (cx+32, y)], fill=(*color, 90), width=2)
    # Belt
    by = bt + int(bh * .55)
    draw.rectangle([cx-42, by, cx+42, by+13], fill=(*color, 210))
    draw.rectangle([cx-9, by+2, cx+9, by+10], fill=(*color, 255))
    # Legs
    draw.rectangle([cx-38, by+13, cx-9,  bb], fill=(*color, 110))
    draw.rectangle([cx+9,  by+13, cx+38, bb], fill=(*color, 110))
    # Sword right
    sx = cx + 62
    draw.line([(sx, bt+8), (sx, bb-5)], fill=(*color, 230), width=5)
    draw.polygon([(sx-12, bt+24), (sx+12, bt+24), (sx, bt+8)],
                 fill=(*color, 200))
    draw.line([(sx-18, bt+40), (sx+18, bt+40)], fill=(*color, 200), width=3)
    # Shield left
    shx, shy = cx-68, bt+28
    draw.polygon([(shx-14, shy), (shx+14, shy),
                  (shx+14, shy+52), (shx, shy+70), (shx-14, shy+52)],
                 fill=(*color, 150), outline=(*color, 220), width=2)
    draw.line([(shx, shy+8), (shx, shy+62)], fill=(*color, 90), width=2)
    draw.line([(shx-10, shy+35), (shx+10, shy+35)], fill=(*color, 90), width=2)


def _body_phu_thuy(draw, cx, bt, bb, color):
    """Phù Thủy: áo choàng rộng, gậy phép trái, ngôi sao trang trí."""
    bh = bb - bt
    # Robe (trapezoid, wide bottom)
    draw.polygon([(cx-28, bt), (cx+28, bt),
                  (cx+72, bb), (cx-72, bb)],
                 fill=(*color, 150))
    # Sleeves
    draw.polygon([(cx-28, bt+8), (cx-68, bt+65), (cx-52, bt+70), (cx-16, bt+14)],
                 fill=(*color, 170))
    draw.polygon([(cx+28, bt+8), (cx+68, bt+65), (cx+52, bt+70), (cx+16, bt+14)],
                 fill=(*color, 170))
    # Robe center band
    draw.polygon([(cx-10, bt), (cx+10, bt), (cx+18, bb), (cx-18, bb)],
                 fill=(*color, 90))
    # Magic stars on robe
    for sx, sy in [(cx-20, bt+45), (cx+15, bt+30), (cx-5, bt+70)]:
        for angle in range(0, 360, 72):
            r1, r2 = 8, 4
            a1 = math.radians(angle)
            a2 = math.radians(angle + 36)
            draw.line([(sx + r1*math.cos(a1), sy + r1*math.sin(a1)),
                       (sx + r2*math.cos(a2), sy + r2*math.sin(a2))],
                      fill=(*color, 180), width=1)
    # Staff left
    stx = cx - 78
    draw.line([(stx, bt-18), (stx, bb)], fill=(*color, 210), width=4)
    draw.ellipse([stx-14, bt-30, stx+14, bt-4], fill=(*color, 190))
    draw.ellipse([stx-7,  bt-24, stx+7,  bt-10], fill=(255, 255, 200, 200))


def _body_xa_thu(draw, cx, bt, bb, color):
    """Xạ Thủ: áo nhẹ, mũ trùm, cung bên phải."""
    bh = bb - bt
    # Cape/hood shoulders
    draw.polygon([(cx-62, bt+5), (cx-28, bt+42), (cx-38, bt+48), (cx-72, bt+14)],
                 fill=(*color, 165))
    draw.polygon([(cx+62, bt+5), (cx+28, bt+42), (cx+38, bt+48), (cx+72, bt+14)],
                 fill=(*color, 165))
    # Light vest
    draw.polygon([(cx-28, bt), (cx+28, bt),
                  (cx+22, bt+int(bh*.52)), (cx-22, bt+int(bh*.52))],
                 fill=(*color, 140))
    # Vest detail
    draw.line([(cx, bt+10), (cx, bt+int(bh*.48))], fill=(*color, 70), width=2)
    # Belt
    by = bt + int(bh * .52)
    draw.rectangle([cx-28, by, cx+28, by+10], fill=(*color, 200))
    # Legs
    draw.rectangle([cx-24, by+10, cx-6,  bb], fill=(*color, 115))
    draw.rectangle([cx+6,  by+10, cx+24, bb], fill=(*color, 115))
    # Quiver on back (left)
    draw.rectangle([cx-78, bt+10, cx-60, bt+75], fill=(*color, 130),
                   outline=(*color, 190), width=1)
    for i in range(3):
        draw.line([(cx-78, bt+15+i*12), (cx-60, bt+15+i*12)],
                  fill=(*color, 90), width=1)
    # Bow right
    bwx = cx + 66
    draw.arc([bwx-18, bt+8, bwx+18, bb-8], start=300, end=60,
             fill=(*color, 220), width=4)
    draw.line([(bwx, bt+8), (bwx, bb-8)], fill=(*color, 160), width=2)
    # Arrow nocked
    arr_y = bt + bh // 2
    draw.line([(bwx-30, arr_y), (bwx+8, arr_y)], fill=(*color, 200), width=2)
    draw.polygon([(bwx+8, arr_y-5), (bwx+18, arr_y), (bwx+8, arr_y+5)],
                 fill=(*color, 220))


def _body_hiep_si(draw, cx, bt, bb, color):
    """Hiệp Sĩ: giáp nặng, khiên to bên trái, kiếm bên phải."""
    bh = bb - bt
    # Big pauldrons
    draw.ellipse([cx-82, bt-12, cx-28, bt+38], fill=(*color, 235))
    draw.ellipse([cx+28, bt-12, cx+82, bt+38], fill=(*color, 235))
    # Chest plate
    draw.polygon([(cx-52, bt+4), (cx+52, bt+4),
                  (cx+44, bt+int(bh*.62)), (cx-44, bt+int(bh*.62))],
                 fill=(*color, 185))
    # Chest cross
    draw.line([(cx, bt+14), (cx, bt+int(bh*.58))], fill=(*color, 80), width=2)
    draw.line([(cx-38, bt+int(bh*.3)), (cx+38, bt+int(bh*.3))],
              fill=(*color, 80), width=2)
    # Belt + tassets
    by = bt + int(bh * .62)
    draw.rectangle([cx-48, by, cx+48, by+14], fill=(*color, 225))
    draw.rectangle([cx-48, by+14, cx-12, by+44], fill=(*color, 175))
    draw.rectangle([cx+12, by+14, cx+48, by+44], fill=(*color, 175))
    # Greaves (legs)
    draw.rectangle([cx-40, by+44, cx-10, bb], fill=(*color, 145))
    draw.rectangle([cx+10, by+44, cx+40, bb], fill=(*color, 145))
    # Shield left
    shx, shy = cx-72, bt+20
    draw.polygon([(shx-16, shy), (shx+16, shy),
                  (shx+16, shy+58), (shx, shy+78), (shx-16, shy+58)],
                 fill=(*color, 155), outline=(*color, 230), width=2)
    draw.line([(shx, shy+8), (shx, shy+68)], fill=(*color, 95), width=2)
    draw.line([(shx-12, shy+38), (shx+12, shy+38)], fill=(*color, 95), width=2)
    # Sword right (shorter, thicker)
    sx = cx + 66
    draw.line([(sx, bt+10), (sx, bb-10)], fill=(*color, 235), width=6)
    draw.polygon([(sx-14, bt+28), (sx+14, bt+28), (sx, bt+10)],
                 fill=(*color, 200))
    draw.line([(sx-20, bt+44), (sx+20, bt+44)], fill=(*color, 205), width=3)


_BODY_DRAW = {
    "chien_binh": _body_chien_binh,
    "phu_thuy":   _body_phu_thuy,
    "xa_thu":     _body_xa_thu,
    "hiep_si":    _body_hiep_si,
}


# ── Main frame builder ─────────────────────────────────────────────────

def make_character_frame(character_type: str, face_img: Image.Image,
                         size: int = 400) -> Image.Image:
    """Ghép mặt học sinh (cartoon) vào toàn thân nhân vật game."""
    cfg    = CHARACTERS.get(character_type, CHARACTERS["chien_binh"])
    color  = hex_to_rgb(cfg["color"])
    bg_rgb = hex_to_rgb(cfg["bg"])
    name   = cfg["name"]

    W, H = size, int(size * 1.35)          # portrait 400 × 540
    canvas = Image.new("RGBA", (W, H), (*bg_rgb, 255))
    draw   = ImageDraw.Draw(canvas)
    cx = W // 2

    # ── Background radial glow ──────────────────────────────────────────
    for r in range(W // 2, 0, -4):
        alpha = int(45 * (1 - r / (W // 2)))
        draw.ellipse([cx-r, H//2-r, cx+r, H//2+r], fill=(*color, alpha))

    # ── Corner decorations ──────────────────────────────────────────────
    for dx, dy in [(14, 14), (W-14, 14), (14, H-14), (W-14, H-14)]:
        draw.ellipse([dx-5, dy-5, dx+5, dy+5], fill=(*color, 190))
        draw.ellipse([dx-8, dy-8, dx+8, dy+8], outline=(*color, 90), width=1)

    # ── Face (head) ─────────────────────────────────────────────────────
    face_sz = size // 3                    # ~133 px
    face_x  = cx - face_sz // 2
    face_y  = 18
    face_cx = face_x + face_sz // 2
    face_cy = face_y + face_sz // 2

    # Glow rings
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd   = ImageDraw.Draw(ring)
    for w in range(12, 0, -2):
        rd.ellipse([face_cx - face_sz//2 - w, face_cy - face_sz//2 - w,
                    face_cx + face_sz//2 + w, face_cy + face_sz//2 + w],
                   outline=(*color, 22 * w), width=2)
    canvas = Image.alpha_composite(canvas, ring)
    draw   = ImageDraw.Draw(canvas)

    face_round = crop_circle(face_img, face_sz)
    canvas.paste(face_round, (face_x, face_y), face_round)

    # ── Neck ────────────────────────────────────────────────────────────
    neck_top = face_y + face_sz
    neck_bot = neck_top + 18
    draw.rectangle([cx-16, neck_top, cx+16, neck_bot], fill=(*color, 55))

    # ── Character body ──────────────────────────────────────────────────
    body_top = neck_bot
    body_bot = H - 70
    fn = _BODY_DRAW.get(character_type, _body_chien_binh)
    fn(draw, cx, body_top, body_bot, color)

    # ── Name banner ─────────────────────────────────────────────────────
    draw = ImageDraw.Draw(canvas)          # refresh after body drawing
    bny, bnh = H - 58, 30
    draw.rectangle([cx-85, bny, cx+85, bny+bnh],
                   fill=(*color, 185), outline=(*color, 255), width=1)
    font = _load_font(13)
    txt  = name.upper()
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx - tw//2, bny + (bnh-th)//2), txt, fill=(0, 0, 0), font=font)

    # ── XP bar ──────────────────────────────────────────────────────────
    bar_y = bny + bnh + 8
    draw.rectangle([cx-70, bar_y, cx+70, bar_y+5],
                   fill=(30, 30, 60), outline=(*color, 100), width=1)
    draw.rectangle([cx-70, bar_y, cx-70+100, bar_y+5], fill=(*color, 220))

    return canvas.convert("RGB")


# ── Base64 helpers ──────────────────────────────────────────────────────

def b64_to_image(b64: str) -> Image.Image:
    data = base64.b64decode(b64.split(",")[-1])
    return Image.open(io.BytesIO(data))


def image_to_b64(img: Image.Image, fmt="JPEG") -> str:
    buf  = io.BytesIO()
    img.save(buf, format=fmt, quality=88)
    b64  = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


# ── Main pipeline ───────────────────────────────────────────────────────

def generate_avatar_pipeline(face_b64: str, character_type: str) -> dict:
    """
    Input:  base64 ảnh mặt học sinh
    Output: { cartoon_b64, final_b64 }
    """
    try:
        face_img    = b64_to_image(face_b64)
        cartoon     = apply_cartoon_filter(face_img)
        cartoon_b64 = image_to_b64(cartoon)
        final_img   = make_character_frame(character_type, cartoon, size=400)
        final_b64   = image_to_b64(final_img)
        return {"ok": True, "cartoon_b64": cartoon_b64, "final_b64": final_b64}
    except Exception as e:
        logger.error(f"Avatar generation error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
