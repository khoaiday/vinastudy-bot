"""Avatar generation: cartoon filter + full-body character composite (gender-aware)."""
import io
import base64
import logging
import math
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

from app.config import CHARACTERS

logger = logging.getLogger(__name__)

HAIR_COLOR = (28, 14, 4)          # nâu đen — màu tóc mặc định


# ── Cartoon filter ─────────────────────────────────────────────────────

def apply_cartoon_filter(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    smooth = img.filter(ImageFilter.MedianFilter(size=5))

    def posterize(image, levels=5):
        lut = [int(round(i / 255 * (levels-1))) * (255 // (levels-1)) for i in range(256)]
        return image.point(lut * 3)

    posterized = posterize(smooth, levels=5)
    saturated  = ImageEnhance.Color(posterized).enhance(1.8)
    contrasted = ImageEnhance.Contrast(saturated).enhance(1.3)
    gray  = img.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES).point(lambda p: 0 if p > 30 else 255)
    return Image.blend(contrasted, edges.convert("RGB"), alpha=0.12)


def crop_circle(img: Image.Image, size: int = 256) -> Image.Image:
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
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ── Hair (chỉ cho nữ) ──────────────────────────────────────────────────

def _draw_female_hair(draw: ImageDraw.ImageDraw,
                      face_x: int, face_y: int, face_sz: int,
                      color: tuple):
    """Vẽ tóc dài nữ phía sau vòng tròn mặt."""
    hc = HAIR_COLOR
    hw = int(face_sz * 0.18)           # độ dày mái tóc
    # Phần mái tóc trên đầu (rộng hơn mặt một chút)
    draw.ellipse([face_x - hw, face_y - hw,
                  face_x + face_sz + hw, face_y + face_sz * 0.55],
                 fill=hc)
    # Tóc thả hai bên
    draw.ellipse([face_x - hw - 4, face_y + face_sz * 0.2,
                  face_x + int(face_sz * 0.25), face_y + face_sz + 50],
                 fill=hc)
    draw.ellipse([face_x + int(face_sz * 0.75), face_y + face_sz * 0.2,
                  face_x + face_sz + hw + 4, face_y + face_sz + 50],
                 fill=hc)
    # Điểm nhấn màu nhân vật ở đầu tóc
    draw.ellipse([face_x + face_sz // 2 - 6, face_y - hw + 2,
                  face_x + face_sz // 2 + 6, face_y - hw + 14],
                 fill=(*color, 200))


# ── Body: nam ──────────────────────────────────────────────────────────

def _body_chien_binh_nam(draw, cx, bt, bb, color):
    bh = bb - bt
    draw.ellipse([cx-80, bt-8, cx-32, bt+32], fill=(*color, 230))
    draw.ellipse([cx+32, bt-8, cx+80, bt+32], fill=(*color, 230))
    draw.polygon([(cx-48, bt), (cx+48, bt),
                  (cx+38, bt+int(bh*.55)), (cx-38, bt+int(bh*.55))],
                 fill=(*color, 160))
    for i in range(3):
        draw.line([(cx-32, bt+18+i*18), (cx+32, bt+18+i*18)],
                  fill=(*color, 90), width=2)
    by = bt + int(bh*.55)
    draw.rectangle([cx-42, by, cx+42, by+13], fill=(*color, 210))
    draw.rectangle([cx-9, by+2, cx+9, by+10], fill=(*color, 255))
    draw.rectangle([cx-38, by+13, cx-9,  bb], fill=(*color, 110))
    draw.rectangle([cx+9,  by+13, cx+38, bb], fill=(*color, 110))
    # Kiếm
    sx = cx+62
    draw.line([(sx, bt+8), (sx, bb-5)], fill=(*color, 230), width=5)
    draw.polygon([(sx-12, bt+24), (sx+12, bt+24), (sx, bt+8)], fill=(*color, 200))
    draw.line([(sx-18, bt+40), (sx+18, bt+40)], fill=(*color, 200), width=3)
    # Khiên
    shx, shy = cx-68, bt+28
    draw.polygon([(shx-14, shy), (shx+14, shy),
                  (shx+14, shy+52), (shx, shy+70), (shx-14, shy+52)],
                 fill=(*color, 150), outline=(*color, 220), width=2)
    draw.line([(shx, shy+8), (shx, shy+62)], fill=(*color, 90), width=2)
    draw.line([(shx-10, shy+35), (shx+10, shy+35)], fill=(*color, 90), width=2)


def _body_chien_binh_nu(draw, cx, bt, bb, color):
    bh = bb - bt
    # Vai hẹp hơn
    draw.ellipse([cx-65, bt-6, cx-25, bt+26], fill=(*color, 225))
    draw.ellipse([cx+25, bt-6, cx+65, bt+26], fill=(*color, 225))
    # Áo giáp dạng corset — eo thon
    draw.polygon([(cx-38, bt), (cx+38, bt),
                  (cx+28, bt+int(bh*.35)), (cx-28, bt+int(bh*.35))],
                 fill=(*color, 165))
    draw.polygon([(cx-28, bt+int(bh*.35)), (cx+28, bt+int(bh*.35)),
                  (cx+34, bt+int(bh*.55)), (cx-34, bt+int(bh*.55))],
                 fill=(*color, 145))
    for i in range(2):
        draw.line([(cx-24, bt+20+i*18), (cx+24, bt+20+i*18)],
                  fill=(*color, 90), width=2)
    by = bt + int(bh*.55)
    draw.rectangle([cx-36, by, cx+36, by+11], fill=(*color, 210))
    draw.rectangle([cx-8, by+2, cx+8, by+9], fill=(*color, 255))
    # Váy ngắn (chiến đấu)
    draw.polygon([(cx-36, by+11), (cx+36, by+11),
                  (cx+48, by+40), (cx-48, by+40)], fill=(*color, 130))
    # Chân boots
    draw.rectangle([cx-36, by+40, cx-10, bb], fill=(*color, 115))
    draw.rectangle([cx+10, by+40, cx+36, bb], fill=(*color, 115))
    # Kiếm thanh mảnh hơn
    sx = cx+56
    draw.line([(sx, bt+8), (sx, bb-8)], fill=(*color, 230), width=4)
    draw.polygon([(sx-10, bt+22), (sx+10, bt+22), (sx, bt+8)], fill=(*color, 200))
    draw.line([(sx-14, bt+36), (sx+14, bt+36)], fill=(*color, 200), width=2)
    # Khiên tròn nhỏ hơn
    shx, shy = cx-60, bt+35
    draw.ellipse([shx-22, shy, shx+22, shy+44],
                 fill=(*color, 150), outline=(*color, 220), width=2)
    draw.ellipse([shx-8, shy+14, shx+8, shy+30], fill=(*color, 200))


def _body_phu_thuy_nam(draw, cx, bt, bb, color):
    bh = bb - bt
    draw.polygon([(cx-28, bt), (cx+28, bt),
                  (cx+72, bb), (cx-72, bb)], fill=(*color, 150))
    draw.polygon([(cx-28, bt+8), (cx-68, bt+65), (cx-52, bt+70), (cx-16, bt+14)],
                 fill=(*color, 170))
    draw.polygon([(cx+28, bt+8), (cx+68, bt+65), (cx+52, bt+70), (cx+16, bt+14)],
                 fill=(*color, 170))
    draw.polygon([(cx-10, bt), (cx+10, bt), (cx+18, bb), (cx-18, bb)],
                 fill=(*color, 90))
    for sx, sy in [(cx-20, bt+45), (cx+15, bt+30), (cx-5, bt+70)]:
        for angle in range(0, 360, 72):
            r1, r2 = 8, 4
            a1, a2 = math.radians(angle), math.radians(angle+36)
            draw.line([(sx+r1*math.cos(a1), sy+r1*math.sin(a1)),
                       (sx+r2*math.cos(a2), sy+r2*math.sin(a2))],
                      fill=(*color, 180), width=1)
    stx = cx-78
    draw.line([(stx, bt-18), (stx, bb)], fill=(*color, 210), width=4)
    draw.ellipse([stx-14, bt-30, stx+14, bt-4], fill=(*color, 190))
    draw.ellipse([stx-7,  bt-24, stx+7,  bt-10], fill=(255, 255, 200, 200))


def _body_phu_thuy_nu(draw, cx, bt, bb, color):
    bh = bb - bt
    # Váy phù thủy dài, bồng
    draw.polygon([(cx-22, bt), (cx+22, bt),
                  (cx+80, bb), (cx-80, bb)], fill=(*color, 148))
    # Áo thân trên thon hơn
    draw.polygon([(cx-22, bt), (cx+22, bt),
                  (cx+18, bt+int(bh*.38)), (cx-18, bt+int(bh*.38))],
                 fill=(*color, 170))
    # Tay áo bồng
    draw.polygon([(cx-22, bt+5), (cx-72, bt+55), (cx-54, bt+65), (cx-14, bt+12)],
                 fill=(*color, 175))
    draw.polygon([(cx+22, bt+5), (cx+72, bt+55), (cx+54, bt+65), (cx+14, bt+12)],
                 fill=(*color, 175))
    # Dây thắt eo
    ey = bt + int(bh*.38)
    draw.ellipse([cx-20, ey-5, cx+20, ey+5], fill=(*color, 210))
    # Ngôi sao
    for sx, sy in [(cx-18, bt+55), (cx+14, bt+42), (cx, bt+78)]:
        for angle in range(0, 360, 72):
            r1, r2 = 7, 3
            a1, a2 = math.radians(angle), math.radians(angle+36)
            draw.line([(sx+r1*math.cos(a1), sy+r1*math.sin(a1)),
                       (sx+r2*math.cos(a2), sy+r2*math.sin(a2))],
                      fill=(*color, 185), width=1)
    # Gậy tinh tế hơn (bên phải)
    stx = cx+72
    draw.line([(stx, bt-18), (stx, bb)], fill=(*color, 200), width=3)
    draw.ellipse([stx-12, bt-30, stx+12, bt-6], fill=(*color, 190))
    draw.ellipse([stx-5,  bt-24, stx+5,  bt-12], fill=(255, 230, 255, 220))


def _body_xa_thu_nam(draw, cx, bt, bb, color):
    bh = bb - bt
    draw.polygon([(cx-62, bt+5), (cx-28, bt+42), (cx-38, bt+48), (cx-72, bt+14)],
                 fill=(*color, 165))
    draw.polygon([(cx+62, bt+5), (cx+28, bt+42), (cx+38, bt+48), (cx+72, bt+14)],
                 fill=(*color, 165))
    draw.polygon([(cx-28, bt), (cx+28, bt),
                  (cx+22, bt+int(bh*.52)), (cx-22, bt+int(bh*.52))],
                 fill=(*color, 140))
    draw.line([(cx, bt+10), (cx, bt+int(bh*.48))], fill=(*color, 70), width=2)
    by = bt + int(bh*.52)
    draw.rectangle([cx-28, by, cx+28, by+10], fill=(*color, 200))
    draw.rectangle([cx-24, by+10, cx-6,  bb], fill=(*color, 115))
    draw.rectangle([cx+6,  by+10, cx+24, bb], fill=(*color, 115))
    # Ống tên
    draw.rectangle([cx-78, bt+10, cx-60, bt+75], fill=(*color, 130),
                   outline=(*color, 190), width=1)
    for i in range(3):
        draw.line([(cx-78, bt+15+i*12), (cx-60, bt+15+i*12)],
                  fill=(*color, 90), width=1)
    bwx = cx+66
    draw.arc([bwx-18, bt+8, bwx+18, bb-8], start=300, end=60,
             fill=(*color, 220), width=4)
    draw.line([(bwx, bt+8), (bwx, bb-8)], fill=(*color, 160), width=2)
    arr_y = bt + bh//2
    draw.line([(bwx-30, arr_y), (bwx+8, arr_y)], fill=(*color, 200), width=2)
    draw.polygon([(bwx+8, arr_y-5), (bwx+18, arr_y), (bwx+8, arr_y+5)],
                 fill=(*color, 220))


def _body_xa_thu_nu(draw, cx, bt, bb, color):
    bh = bb - bt
    # Áo khoác nhẹ vai hẹp
    draw.polygon([(cx-52, bt+5), (cx-24, bt+38), (cx-32, bt+44), (cx-60, bt+12)],
                 fill=(*color, 162))
    draw.polygon([(cx+52, bt+5), (cx+24, bt+38), (cx+32, bt+44), (cx+60, bt+12)],
                 fill=(*color, 162))
    # Thân áo
    draw.polygon([(cx-22, bt), (cx+22, bt),
                  (cx+16, bt+int(bh*.48)), (cx-16, bt+int(bh*.48))],
                 fill=(*color, 138))
    draw.line([(cx, bt+8), (cx, bt+int(bh*.44))], fill=(*color, 65), width=2)
    by = bt + int(bh*.48)
    draw.rectangle([cx-22, by, cx+22, by+9], fill=(*color, 195))
    # Quần dài
    draw.rectangle([cx-20, by+9, cx-5,  bb], fill=(*color, 118))
    draw.rectangle([cx+5,  by+9, cx+20, bb], fill=(*color, 118))
    # Bao đựng tên bên hông
    draw.rectangle([cx-70, bt+12, cx-55, bt+70], fill=(*color, 128),
                   outline=(*color, 185), width=1)
    for i in range(3):
        draw.line([(cx-70, bt+17+i*12), (cx-55, bt+17+i*12)],
                  fill=(*color, 85), width=1)
    # Cung thanh mảnh
    bwx = cx+60
    draw.arc([bwx-14, bt+10, bwx+14, bb-10], start=300, end=60,
             fill=(*color, 215), width=3)
    draw.line([(bwx, bt+10), (bwx, bb-10)], fill=(*color, 155), width=2)
    arr_y = bt + bh//2
    draw.line([(bwx-24, arr_y), (bwx+6, arr_y)], fill=(*color, 200), width=2)
    draw.polygon([(bwx+6, arr_y-4), (bwx+14, arr_y), (bwx+6, arr_y+4)],
                 fill=(*color, 215))


def _body_hiep_si_nam(draw, cx, bt, bb, color):
    bh = bb - bt
    draw.ellipse([cx-82, bt-12, cx-28, bt+38], fill=(*color, 235))
    draw.ellipse([cx+28, bt-12, cx+82, bt+38], fill=(*color, 235))
    draw.polygon([(cx-52, bt+4), (cx+52, bt+4),
                  (cx+44, bt+int(bh*.62)), (cx-44, bt+int(bh*.62))],
                 fill=(*color, 185))
    draw.line([(cx, bt+14), (cx, bt+int(bh*.58))], fill=(*color, 80), width=2)
    draw.line([(cx-38, bt+int(bh*.3)), (cx+38, bt+int(bh*.3))],
              fill=(*color, 80), width=2)
    by = bt + int(bh*.62)
    draw.rectangle([cx-48, by, cx+48, by+14], fill=(*color, 225))
    draw.rectangle([cx-48, by+14, cx-12, by+44], fill=(*color, 175))
    draw.rectangle([cx+12, by+14, cx+48, by+44], fill=(*color, 175))
    draw.rectangle([cx-40, by+44, cx-10, bb], fill=(*color, 145))
    draw.rectangle([cx+10, by+44, cx+40, bb], fill=(*color, 145))
    shx, shy = cx-72, bt+20
    draw.polygon([(shx-16, shy), (shx+16, shy),
                  (shx+16, shy+58), (shx, shy+78), (shx-16, shy+58)],
                 fill=(*color, 155), outline=(*color, 230), width=2)
    draw.line([(shx, shy+8), (shx, shy+68)], fill=(*color, 95), width=2)
    draw.line([(shx-12, shy+38), (shx+12, shy+38)], fill=(*color, 95), width=2)
    sx = cx+66
    draw.line([(sx, bt+10), (sx, bb-10)], fill=(*color, 235), width=6)
    draw.polygon([(sx-14, bt+28), (sx+14, bt+28), (sx, bt+10)], fill=(*color, 200))
    draw.line([(sx-20, bt+44), (sx+20, bt+44)], fill=(*color, 205), width=3)


def _body_hiep_si_nu(draw, cx, bt, bb, color):
    bh = bb - bt
    # Vai nhỏ hơn
    draw.ellipse([cx-68, bt-10, cx-22, bt+30], fill=(*color, 230))
    draw.ellipse([cx+22, bt-10, cx+68, bt+30], fill=(*color, 230))
    # Áo giáp dạng áo corset + váy giáp
    draw.polygon([(cx-42, bt+4), (cx+42, bt+4),
                  (cx+32, bt+int(bh*.42)), (cx-32, bt+int(bh*.42))],
                 fill=(*color, 182))
    draw.line([(cx, bt+12), (cx, bt+int(bh*.38))], fill=(*color, 78), width=2)
    draw.line([(cx-30, bt+int(bh*.25)), (cx+30, bt+int(bh*.25))],
              fill=(*color, 78), width=2)
    # Váy giáp bồng
    by = bt + int(bh*.42)
    draw.polygon([(cx-32, by), (cx+32, by),
                  (cx+55, by+50), (cx-55, by+50)], fill=(*color, 165))
    draw.polygon([(cx-55, by+50), (cx+55, by+50),
                  (cx+50, by+70), (cx-50, by+70)], fill=(*color, 145))
    # Boots
    draw.rectangle([cx-38, by+70, cx-10, bb], fill=(*color, 140))
    draw.rectangle([cx+10, by+70, cx+38, bb], fill=(*color, 140))
    # Khiên tròn nhỏ gọn
    shx, shy = cx-65, bt+24
    draw.ellipse([shx-20, shy, shx+20, shy+40],
                 fill=(*color, 152), outline=(*color, 225), width=2)
    draw.ellipse([shx-7, shy+12, shx+7, shy+28], fill=(*color, 205))
    # Kiếm một tay
    sx = cx+60
    draw.line([(sx, bt+10), (sx, bb-12)], fill=(*color, 230), width=5)
    draw.polygon([(sx-12, bt+26), (sx+12, bt+26), (sx, bt+10)], fill=(*color, 195))
    draw.line([(sx-16, bt+40), (sx+16, bt+40)], fill=(*color, 200), width=2)


# ── Dispatch table ─────────────────────────────────────────────────────

_BODY_DRAW = {
    ("chien_binh", "nam"): _body_chien_binh_nam,
    ("chien_binh", "nu"):  _body_chien_binh_nu,
    ("phu_thuy",   "nam"): _body_phu_thuy_nam,
    ("phu_thuy",   "nu"):  _body_phu_thuy_nu,
    ("xa_thu",     "nam"): _body_xa_thu_nam,
    ("xa_thu",     "nu"):  _body_xa_thu_nu,
    ("hiep_si",    "nam"): _body_hiep_si_nam,
    ("hiep_si",    "nu"):  _body_hiep_si_nu,
}


# ── Main frame builder ─────────────────────────────────────────────────

def make_character_frame(character_type: str, face_img: Image.Image,
                         gioi_tinh: str = "nam", size: int = 400) -> Image.Image:
    """Ghép mặt học sinh vào toàn thân nhân vật (có phân biệt giới tính)."""
    cfg    = CHARACTERS.get(character_type, CHARACTERS["chien_binh"])
    color  = hex_to_rgb(cfg["color"])
    bg_rgb = hex_to_rgb(cfg["bg"])
    name   = cfg["name"]
    gt     = "nu" if gioi_tinh in ("nu", "nữ", "female", "f") else "nam"

    W, H = size, int(size * 1.35)
    canvas = Image.new("RGBA", (W, H), (*bg_rgb, 255))
    draw   = ImageDraw.Draw(canvas)
    cx     = W // 2

    # Nền glow
    for r in range(W // 2, 0, -4):
        alpha = int(45 * (1 - r / (W // 2)))
        draw.ellipse([cx-r, H//2-r, cx+r, H//2+r], fill=(*color, alpha))

    # Góc trang trí
    for dx, dy in [(14, 14), (W-14, 14), (14, H-14), (W-14, H-14)]:
        draw.ellipse([dx-5, dy-5, dx+5, dy+5], fill=(*color, 190))
        draw.ellipse([dx-8, dy-8, dx+8, dy+8], outline=(*color, 90), width=1)

    # Kích thước đầu
    face_sz = size // 3
    face_x  = cx - face_sz // 2
    face_y  = 18
    face_cx = face_x + face_sz // 2
    face_cy = face_y + face_sz // 2

    # Tóc nữ (vẽ trước mặt để nằm phía sau)
    if gt == "nu":
        _draw_female_hair(draw, face_x, face_y, face_sz, color)

    # Vòng hào quang quanh mặt
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd   = ImageDraw.Draw(ring)
    for w in range(12, 0, -2):
        rd.ellipse([face_cx - face_sz//2 - w, face_cy - face_sz//2 - w,
                    face_cx + face_sz//2 + w, face_cy + face_sz//2 + w],
                   outline=(*color, 22*w), width=2)
    canvas = Image.alpha_composite(canvas, ring)
    draw   = ImageDraw.Draw(canvas)

    # Dán mặt
    face_round = crop_circle(face_img, face_sz)
    canvas.paste(face_round, (face_x, face_y), face_round)

    # Cổ
    neck_top = face_y + face_sz
    neck_bot = neck_top + 18
    draw.rectangle([cx-14, neck_top, cx+14, neck_bot], fill=(*color, 55))

    # Thân nhân vật
    body_top = neck_bot
    body_bot = H - 70
    fn = _BODY_DRAW.get((character_type, gt),
                        _BODY_DRAW.get((character_type, "nam"), _body_chien_binh_nam))
    fn(draw, cx, body_top, body_bot, color)

    # Banner tên
    draw = ImageDraw.Draw(canvas)
    bny, bnh = H - 58, 30
    draw.rectangle([cx-85, bny, cx+85, bny+bnh],
                   fill=(*color, 185), outline=(*color, 255), width=1)
    font = _load_font(13)
    txt  = name.upper() + (" ♀" if gt == "nu" else " ♂")
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx - tw//2, bny + (bnh-th)//2), txt, fill=(0, 0, 0), font=font)

    # Thanh XP
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

def generate_avatar_pipeline(face_b64: str, character_type: str,
                             gioi_tinh: str = "nam") -> dict:
    try:
        face_img    = b64_to_image(face_b64)
        cartoon     = apply_cartoon_filter(face_img)
        cartoon_b64 = image_to_b64(cartoon)
        final_img   = make_character_frame(character_type, cartoon,
                                           gioi_tinh=gioi_tinh, size=400)
        final_b64   = image_to_b64(final_img)
        return {"ok": True, "cartoon_b64": cartoon_b64, "final_b64": final_b64}
    except Exception as e:
        logger.error(f"Avatar generation error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
