"""Avatar generation: cartoon filter + full-body character composite (gender-aware).

Cartoon pipeline:
  1. Thử AnimeGAN2 qua Replicate API (nếu có REPLICATE_API_TOKEN)
  2. Fallback về PIL filter nâng cao nếu Replicate lỗi / chưa cấu hình

Character frame:
  - Canvas RGB (không RGBA) để tránh lỗi composite over black
  - Body functions dùng màu solid RGB + outline DARK + accent GOLD/SILVER
"""
import io
import base64
import logging
import math
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

from app.config import CHARACTERS, REPLICATE_API_TOKEN

logger = logging.getLogger(__name__)

# ── Color palette ────────────────────────────────────────────────────────
HAIR_COLOR = (28,  14,   4)   # nâu đen — tóc mặc định
DARK       = (18,  14,  32)   # gần đen  — viền / bóng
LIGHT      = (240, 235, 255)  # gần trắng — text / highlight
GOLD       = (215, 170,  50)  # vàng      — belt, trim, phụ kiện
SILVER     = (185, 192, 202)  # bạc       — lưỡi kiếm, mũi tên


def _shade(c: tuple, f: float) -> tuple:
    """Màu tối hơn: f=0.6 → tối 40%."""
    return tuple(max(0, int(x * f)) for x in c)


def _tint(c: tuple, f: float) -> tuple:
    """Màu sáng hơn: f=1.4 → sáng 40%."""
    return tuple(min(255, int(x * f)) for x in c)


def _mix(c1: tuple, c2: tuple, t: float) -> tuple:
    """Pha trộn: t=0→c1, t=1→c2."""
    return tuple(int(a * (1 - t) + b * t) for a, b in zip(c1, c2))


# ══════════════════════════════════════════════════════════════════════
# Cartoon filter — AI (AnimeGAN2 via Replicate)
# ══════════════════════════════════════════════════════════════════════

def _cartoon_ai(img: Image.Image) -> Image.Image:
    """
    Chuyển ảnh mặt → hoạt hình anime bằng AnimeGAN2 (Replicate API).
    Ném exception nếu thất bại để caller fallback về PIL.
    """
    import replicate
    import httpx
    import os

    # Set token (luôn override để đảm bảo đúng giá trị runtime)
    token = os.getenv("REPLICATE_API_TOKEN") or REPLICATE_API_TOKEN
    if not token:
        raise ValueError("REPLICATE_API_TOKEN chưa được cấu hình")
    os.environ["REPLICATE_API_TOKEN"] = token

    # Resize ảnh vào: AnimeGAN2 hoạt động tốt nhất ở 512×512
    img_resized = img.convert("RGB").resize((512, 512), Image.LANCZOS)

    # Encode ảnh sang JPEG bytes
    buf = io.BytesIO()
    img_resized.save(buf, format="JPEG", quality=95)
    buf.seek(0)

    # AnimeGAN2 — style BarbieFace: đẹp nhất cho ảnh chân dung / trẻ em
    # Chỉ truyền image + style — output_size KHÔNG phải parameter hợp lệ của model này
    output = replicate.run(
        "ptran1203/pytorch-animegan:7d44f1878a07e7b5a32af9727c1f6120cac04203d48f3f7b0432e28fa8e5c6b6",
        input={
            "image": buf,
            "style": "BarbieFace",
        }
    )

    # output là URL string hoặc list[URL]
    url = str(output[0]) if isinstance(output, list) else str(output)
    if not url.startswith("http"):
        raise ValueError(f"Replicate output không phải URL: {url!r}")

    # Download ảnh kết quả
    resp = httpx.get(url, timeout=60)
    resp.raise_for_status()
    result = Image.open(io.BytesIO(resp.content)).convert("RGB")
    logger.info(f"AnimeGAN2 output size: {result.size}")
    return result


# ══════════════════════════════════════════════════════════════════════
# Cartoon filter — PIL fallback (không cần internet)
# ══════════════════════════════════════════════════════════════════════

def _cartoon_pil(img: Image.Image) -> Image.Image:
    """
    Portrait enhance nhẹ — fallback khi không có Replicate token.
    Không cố cartoon giả tạo (dễ méo màu da), chỉ làm ảnh đẹp hơn:
    smooth da nhẹ → tăng sắc nét → boost màu/contrast vừa phải.
    Kết quả: ảnh chân dung tự nhiên, sắc nét, phù hợp ghép vào frame.
    """
    rgb = img.convert("RGB")

    # 1. Upscale nếu quá nhỏ (xử lý tốt hơn ở kích thước lớn)
    W, H = rgb.size
    if min(W, H) < 256:
        scale  = 256 / min(W, H)
        rgb    = rgb.resize((int(W * scale), int(H * scale)), Image.LANCZOS)

    # 2. Làm mịn da nhẹ (chỉ 2 lần blur rất nhỏ)
    smooth = rgb.filter(ImageFilter.GaussianBlur(radius=0.8))
    smooth = smooth.filter(ImageFilter.GaussianBlur(radius=0.6))

    # 3. Tăng sắc nét (unsharp mask effect)
    sharp = ImageEnhance.Sharpness(smooth).enhance(2.0)

    # 4. Boost màu & contrast nhẹ (không méo màu da)
    out = ImageEnhance.Color(sharp).enhance(1.25)       # tươi nhẹ
    out = ImageEnhance.Contrast(out).enhance(1.20)      # rõ hơn
    out = ImageEnhance.Brightness(out).enhance(1.05)    # sáng nhẹ

    # 5. Resize về kích thước gốc nếu đã upscale
    if out.size != (W, H):
        out = out.resize((W, H), Image.LANCZOS)

    return out


# ══════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════

def apply_cartoon_filter(img: Image.Image) -> Image.Image:
    # Đọc token tại runtime (không dùng giá trị import-time) để Railway inject kịp
    import os
    token = os.getenv("REPLICATE_API_TOKEN") or REPLICATE_API_TOKEN
    if token:
        try:
            result = _cartoon_ai(img)
            logger.info("✅ Cartoon: AnimeGAN2 (Replicate) thành công")
            return result
        except Exception as e:
            logger.warning(f"⚠️  AnimeGAN2 thất bại, dùng PIL: {e}")
    logger.info("🎨 Cartoon: PIL portrait-enhance (fallback)")
    return _cartoon_pil(img)


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


# ══════════════════════════════════════════════════════════════════════
# Hair (nữ)
# ══════════════════════════════════════════════════════════════════════

def _draw_female_hair(draw: ImageDraw.ImageDraw,
                      face_x: int, face_y: int, face_sz: int,
                      color: tuple):
    hc = HAIR_COLOR
    hw = int(face_sz * 0.18)
    draw.ellipse([face_x - hw, face_y - hw,
                  face_x + face_sz + hw, face_y + face_sz * 0.55],
                 fill=hc, outline=_shade(hc, 0.65), width=1)
    draw.ellipse([face_x - hw - 4, face_y + face_sz * 0.2,
                  face_x + int(face_sz * 0.25), face_y + face_sz + 50],
                 fill=hc, outline=_shade(hc, 0.65), width=1)
    draw.ellipse([face_x + int(face_sz * 0.75), face_y + face_sz * 0.2,
                  face_x + face_sz + hw + 4,    face_y + face_sz + 50],
                 fill=hc, outline=_shade(hc, 0.65), width=1)
    # Điểm nhấn màu nhân vật
    draw.ellipse([face_x + face_sz // 2 - 6, face_y - hw + 2,
                  face_x + face_sz // 2 + 6, face_y - hw + 14],
                 fill=color)


# ══════════════════════════════════════════════════════════════════════
# Body drawing — mỗi hàm nhận (draw, cx, bt, bb, c)
#   c   = character color (RGB tuple)
#   cd  = darker shade (~0.62)
#   cl  = lighter tint (~1.30)
# Tất cả fill dùng RGB solid + outline=DARK để tạo contrast rõ ràng
# ══════════════════════════════════════════════════════════════════════

def _body_chien_binh_nam(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.62), _tint(c, 1.30)

    # ── Vai (pauldron) ─────────────────────────────────────────────────
    draw.ellipse([cx-82, bt-10, cx-28, bt+36], fill=c, outline=DARK, width=2)
    draw.ellipse([cx+28, bt-10, cx+82, bt+36], fill=c, outline=DARK, width=2)
    draw.ellipse([cx-72, bt-2,  cx-42, bt+18], fill=cl)
    draw.ellipse([cx+42, bt-2,  cx+72, bt+18], fill=cl)

    # ── Ngực (áo giáp) ─────────────────────────────────────────────────
    draw.polygon([(cx-50, bt), (cx+50, bt),
                  (cx+40, bt+int(bh*.55)), (cx-40, bt+int(bh*.55))],
                 fill=c, outline=DARK, width=2)
    draw.line([(cx, bt+6), (cx, bt+int(bh*.52))], fill=cd, width=3)
    for i, r in enumerate([.14, .27, .40]):
        y, w = bt + int(bh * r), 44 - i * 6
        draw.line([(cx-w, y), (cx+w, y)], fill=cd, width=2)

    # ── Belt ───────────────────────────────────────────────────────────
    by = bt + int(bh * .55)
    draw.rectangle([cx-44, by, cx+44, by+14], fill=GOLD, outline=DARK, width=1)
    draw.rectangle([cx-8, by+2, cx+8, by+12], fill=cl)

    # ── Chân ───────────────────────────────────────────────────────────
    draw.rectangle([cx-40, by+14, cx-8,  bb-20], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx+8,  by+14, cx+40, bb-20], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx-42, bb-20, cx-6,  bb],    fill=_shade(c, 0.42), outline=DARK, width=1)
    draw.rectangle([cx+6,  bb-20, cx+42, bb],    fill=_shade(c, 0.42), outline=DARK, width=1)
    draw.line([(cx-42, bb-22), (cx-6,  bb-22)], fill=GOLD, width=2)
    draw.line([(cx+6,  bb-22), (cx+42, bb-22)], fill=GOLD, width=2)

    # ── Kiếm (phải) ────────────────────────────────────────────────────
    sx = cx + 68
    draw.polygon([(sx-4, bt+5), (sx+4, bt+5), (sx+2, bb-6), (sx-2, bb-6)],
                 fill=SILVER, outline=DARK, width=1)
    draw.polygon([(sx-4, bt+5), (sx+4, bt+5), (sx, bt-4)], fill=LIGHT)
    draw.rectangle([sx-14, bt+22, sx+14, bt+30], fill=GOLD, outline=DARK, width=1)
    draw.rectangle([sx-4,  bt+30, sx+4,  bt+52], fill=_mix(GOLD, DARK, 0.5), outline=DARK, width=1)

    # ── Khiên (trái) ───────────────────────────────────────────────────
    shx, shy = cx-72, bt+26
    draw.polygon([(shx-18, shy), (shx+18, shy),
                  (shx+18, shy+56), (shx, shy+76), (shx-18, shy+56)],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(shx-12, shy+3), (shx+12, shy+3),
                  (shx+12, shy+50), (shx, shy+66), (shx-12, shy+50)],
                 outline=GOLD, width=1)
    draw.line([(shx, shy+8),  (shx, shy+66)],       fill=cd, width=2)
    draw.line([(shx-12, shy+35), (shx+12, shy+35)], fill=cd, width=2)
    draw.ellipse([shx-6, shy+29, shx+6, shy+41], fill=GOLD, outline=DARK, width=1)


def _body_chien_binh_nu(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.62), _tint(c, 1.30)

    # ── Vai hẹp hơn ────────────────────────────────────────────────────
    draw.ellipse([cx-65, bt-6, cx-24, bt+28], fill=c, outline=DARK, width=2)
    draw.ellipse([cx+24, bt-6, cx+65, bt+28], fill=c, outline=DARK, width=2)
    draw.ellipse([cx-56, bt,   cx-36, bt+14], fill=cl)
    draw.ellipse([cx+36, bt,   cx+56, bt+14], fill=cl)

    # ── Ngực (corset) ──────────────────────────────────────────────────
    draw.polygon([(cx-38, bt), (cx+38, bt),
                  (cx+28, bt+int(bh*.35)), (cx-28, bt+int(bh*.35))],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(cx-28, bt+int(bh*.35)), (cx+28, bt+int(bh*.35)),
                  (cx+34, bt+int(bh*.55)), (cx-34, bt+int(bh*.55))],
                 fill=c, outline=DARK, width=1)
    for i in range(2):
        y = bt + 20 + i * 18
        draw.line([(cx-24, y), (cx+24, y)], fill=cd, width=2)

    # ── Belt ───────────────────────────────────────────────────────────
    by = bt + int(bh * .55)
    draw.rectangle([cx-36, by, cx+36, by+11], fill=GOLD, outline=DARK, width=1)
    draw.rectangle([cx-8,  by+2, cx+8, by+9], fill=cl)

    # ── Váy chiến đấu ──────────────────────────────────────────────────
    draw.polygon([(cx-36, by+11), (cx+36, by+11),
                  (cx+50, by+42), (cx-50, by+42)], fill=c, outline=DARK, width=1)
    # Váy segment lines
    for i in range(1, 4):
        y = by + 11 + i * 10
        x_off = 36 + i * 5
        draw.line([(cx-x_off+2, y), (cx+x_off-2, y)], fill=cd, width=1)

    # ── Boots ──────────────────────────────────────────────────────────
    draw.rectangle([cx-38, by+42, cx-10, bb],    fill=_shade(c, 0.42), outline=DARK, width=1)
    draw.rectangle([cx+10, by+42, cx+38, bb],    fill=_shade(c, 0.42), outline=DARK, width=1)
    draw.line([(cx-38, by+44), (cx-10, by+44)], fill=GOLD, width=2)
    draw.line([(cx+10, by+44), (cx+38, by+44)], fill=GOLD, width=2)

    # ── Kiếm (phải) ────────────────────────────────────────────────────
    sx = cx + 58
    draw.polygon([(sx-3, bt+5), (sx+3, bt+5), (sx+2, bb-8), (sx-2, bb-8)],
                 fill=SILVER, outline=DARK, width=1)
    draw.polygon([(sx-3, bt+5), (sx+3, bt+5), (sx, bt-3)], fill=LIGHT)
    draw.rectangle([sx-12, bt+20, sx+12, bt+27], fill=GOLD, outline=DARK, width=1)
    draw.rectangle([sx-3,  bt+27, sx+3,  bt+46], fill=_mix(GOLD, DARK, 0.5), outline=DARK, width=1)

    # ── Khiên tròn (trái) ──────────────────────────────────────────────
    shx, shy = cx-60, bt+34
    draw.ellipse([shx-22, shy, shx+22, shy+44], fill=c, outline=DARK, width=2)
    draw.ellipse([shx-14, shy+6, shx+14, shy+38], outline=GOLD, width=1)
    draw.ellipse([shx-6,  shy+16, shx+6, shy+28], fill=GOLD, outline=DARK, width=1)


def _body_phu_thuy_nam(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.62), _tint(c, 1.25)

    # ── Áo choàng (robe) ───────────────────────────────────────────────
    draw.polygon([(cx-28, bt), (cx+28, bt),
                  (cx+72, bb), (cx-72, bb)],
                 fill=c, outline=DARK, width=2)
    # Lớp trong áo choàng
    draw.polygon([(cx-10, bt+10), (cx+10, bt+10),
                  (cx+22, bb-4),  (cx-22, bb-4)],
                 fill=cd)

    # ── Tay áo rộng ────────────────────────────────────────────────────
    draw.polygon([(cx-28, bt+8), (cx-70, bt+66), (cx-52, bt+72), (cx-16, bt+14)],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(cx+28, bt+8), (cx+70, bt+66), (cx+52, bt+72), (cx+16, bt+14)],
                 fill=c, outline=DARK, width=2)
    # Cuff tay
    draw.ellipse([cx-74, bt+62, cx-50, bt+76], fill=cl, outline=DARK, width=1)
    draw.ellipse([cx+50, bt+62, cx+74, bt+76], fill=cl, outline=DARK, width=1)

    # ── Thắt lưng ──────────────────────────────────────────────────────
    wy = bt + int(bh * .40)
    draw.rectangle([cx-24, wy, cx+24, wy+10], fill=GOLD, outline=DARK, width=1)

    # ── Ngôi sao phép thuật ────────────────────────────────────────────
    for sx, sy in [(cx-18, bt+50), (cx+15, bt+38), (cx-5, bt+76)]:
        for angle in range(0, 360, 72):
            r1, r2 = 9, 4
            a1, a2 = math.radians(angle), math.radians(angle + 36)
            draw.line([(sx + r1*math.cos(a1), sy + r1*math.sin(a1)),
                       (sx + r2*math.cos(a2), sy + r2*math.sin(a2))],
                      fill=GOLD, width=2)

    # ── Gậy phép (trái) ────────────────────────────────────────────────
    stx = cx - 80
    draw.line([(stx, bt-18), (stx, bb)], fill=_mix(c, DARK, 0.4), width=4)
    draw.line([(stx, bt-18), (stx, bb)], fill=cl, width=1)  # viền sáng
    draw.ellipse([stx-14, bt-30, stx+14, bt-4],  fill=c,     outline=DARK, width=2)
    draw.ellipse([stx-7,  bt-24, stx+7,  bt-10], fill=(255, 255, 180),    outline=DARK, width=1)


def _body_phu_thuy_nu(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.62), _tint(c, 1.25)

    # ── Váy phù thủy bồng ──────────────────────────────────────────────
    draw.polygon([(cx-22, bt), (cx+22, bt),
                  (cx+82, bb), (cx-82, bb)],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(cx-8,  bt+12), (cx+8,  bt+12),
                  (cx+24, bb-4),  (cx-24, bb-4)],
                 fill=cd)

    # ── Thân áo trên ───────────────────────────────────────────────────
    draw.polygon([(cx-22, bt), (cx+22, bt),
                  (cx+18, bt+int(bh*.38)), (cx-18, bt+int(bh*.38))],
                 fill=c, outline=DARK, width=1)

    # ── Tay áo bồng ────────────────────────────────────────────────────
    draw.polygon([(cx-22, bt+5), (cx-74, bt+56), (cx-56, bt+66), (cx-14, bt+12)],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(cx+22, bt+5), (cx+74, bt+56), (cx+56, bt+66), (cx+14, bt+12)],
                 fill=c, outline=DARK, width=2)
    draw.ellipse([cx-78, bt+52, cx-54, bt+70], fill=cl, outline=DARK, width=1)
    draw.ellipse([cx+54, bt+52, cx+78, bt+70], fill=cl, outline=DARK, width=1)

    # ── Dây thắt eo ────────────────────────────────────────────────────
    ey = bt + int(bh * .38)
    draw.ellipse([cx-22, ey-5, cx+22, ey+7], fill=GOLD, outline=DARK, width=1)

    # ── Ngôi sao ───────────────────────────────────────────────────────
    for sx, sy in [(cx-16, bt+55), (cx+14, bt+44), (cx, bt+82)]:
        for angle in range(0, 360, 72):
            r1, r2 = 8, 3
            a1, a2 = math.radians(angle), math.radians(angle + 36)
            draw.line([(sx + r1*math.cos(a1), sy + r1*math.sin(a1)),
                       (sx + r2*math.cos(a2), sy + r2*math.sin(a2))],
                      fill=GOLD, width=2)

    # ── Gậy (phải) ─────────────────────────────────────────────────────
    stx = cx + 74
    draw.line([(stx, bt-18), (stx, bb)], fill=_mix(c, DARK, 0.4), width=3)
    draw.line([(stx, bt-18), (stx, bb)], fill=cl, width=1)
    draw.ellipse([stx-12, bt-30, stx+12, bt-6],  fill=c, outline=DARK, width=2)
    draw.ellipse([stx-5,  bt-24, stx+5,  bt-12], fill=(255, 220, 255), outline=DARK, width=1)


def _body_xa_thu_nam(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.62), _tint(c, 1.28)

    # ── Tay áo da ──────────────────────────────────────────────────────
    draw.polygon([(cx-64, bt+5), (cx-28, bt+44), (cx-38, bt+50), (cx-74, bt+14)],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(cx+64, bt+5), (cx+28, bt+44), (cx+38, bt+50), (cx+74, bt+14)],
                 fill=c, outline=DARK, width=2)

    # ── Thân áo (nhẹ) ──────────────────────────────────────────────────
    draw.polygon([(cx-28, bt), (cx+28, bt),
                  (cx+22, bt+int(bh*.52)), (cx-22, bt+int(bh*.52))],
                 fill=c, outline=DARK, width=2)
    draw.line([(cx, bt+10), (cx, bt+int(bh*.48))], fill=cd, width=2)

    # ── Belt ───────────────────────────────────────────────────────────
    by = bt + int(bh * .52)
    draw.rectangle([cx-28, by, cx+28, by+10], fill=GOLD, outline=DARK, width=1)

    # ── Quần ───────────────────────────────────────────────────────────
    draw.rectangle([cx-24, by+10, cx-6,  bb-16], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx+6,  by+10, cx+24, bb-16], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx-26, bb-16, cx-4,  bb],    fill=_shade(c, 0.40), outline=DARK, width=1)
    draw.rectangle([cx+4,  bb-16, cx+26, bb],    fill=_shade(c, 0.40), outline=DARK, width=1)

    # ── Ống tên (trái) ─────────────────────────────────────────────────
    qx, qy = cx-78, bt+10
    draw.rectangle([qx, qy, qx+18, qy+66],    fill=cd, outline=DARK, width=1)
    draw.rectangle([qx, qy, qx+18, qy+10],    fill=GOLD, outline=DARK, width=1)  # nắp
    for i in range(3):
        draw.line([(qx, qy+18+i*12), (qx+18, qy+18+i*12)], fill=DARK, width=1)
    # Mũi tên nhô ra
    for i in range(3):
        draw.line([(qx+9, qy+8-i*3), (qx+9, qy-8)], fill=SILVER, width=1)

    # ── Cung (phải) ────────────────────────────────────────────────────
    bwx = cx + 68
    draw.arc([bwx-20, bt+6, bwx+20, bb-6], start=300, end=60,
             fill=c, width=4)
    draw.line([(bwx, bt+6), (bwx, bb-6)], fill=cd, width=2)
    # Dây cung
    draw.arc([bwx-8, bt+14, bwx+8, bb-14], start=300, end=60,
             fill=DARK, width=1)
    # Mũi tên đang giương
    arr_y = bt + bh // 2
    draw.line([(bwx-28, arr_y), (bwx+6, arr_y)], fill=SILVER, width=2)
    draw.polygon([(bwx+6, arr_y-5), (bwx+18, arr_y), (bwx+6, arr_y+5)],
                 fill=SILVER, outline=DARK, width=1)
    # Đuôi mũi tên
    draw.line([(bwx-28, arr_y-3), (bwx-22, arr_y)], fill=c, width=2)
    draw.line([(bwx-28, arr_y+3), (bwx-22, arr_y)], fill=c, width=2)


def _body_xa_thu_nu(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.62), _tint(c, 1.28)

    # ── Tay áo nhẹ ─────────────────────────────────────────────────────
    draw.polygon([(cx-54, bt+5), (cx-24, bt+40), (cx-32, bt+46), (cx-62, bt+12)],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(cx+54, bt+5), (cx+24, bt+40), (cx+32, bt+46), (cx+62, bt+12)],
                 fill=c, outline=DARK, width=2)

    # ── Thân áo ────────────────────────────────────────────────────────
    draw.polygon([(cx-22, bt), (cx+22, bt),
                  (cx+16, bt+int(bh*.48)), (cx-16, bt+int(bh*.48))],
                 fill=c, outline=DARK, width=2)
    draw.line([(cx, bt+8), (cx, bt+int(bh*.44))], fill=cd, width=2)

    # ── Belt ───────────────────────────────────────────────────────────
    by = bt + int(bh * .48)
    draw.rectangle([cx-22, by, cx+22, by+9], fill=GOLD, outline=DARK, width=1)

    # ── Quần dài ───────────────────────────────────────────────────────
    draw.rectangle([cx-20, by+9, cx-5,  bb-14], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx+5,  by+9, cx+20, bb-14], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx-22, bb-14, cx-3, bb],    fill=_shade(c, 0.40), outline=DARK, width=1)
    draw.rectangle([cx+3,  bb-14, cx+22, bb],   fill=_shade(c, 0.40), outline=DARK, width=1)

    # ── Ống tên (trái) ─────────────────────────────────────────────────
    qx, qy = cx-72, bt+12
    draw.rectangle([qx, qy, qx+16, qy+58], fill=cd, outline=DARK, width=1)
    draw.rectangle([qx, qy, qx+16, qy+9],  fill=GOLD, outline=DARK, width=1)

    # ── Cung thanh mảnh (phải) ─────────────────────────────────────────
    bwx = cx + 62
    draw.arc([bwx-16, bt+8, bwx+16, bb-8], start=300, end=60, fill=c, width=3)
    draw.line([(bwx, bt+8), (bwx, bb-8)], fill=cd, width=2)
    arr_y = bt + bh // 2
    draw.line([(bwx-22, arr_y), (bwx+4, arr_y)], fill=SILVER, width=2)
    draw.polygon([(bwx+4, arr_y-4), (bwx+14, arr_y), (bwx+4, arr_y+4)],
                 fill=SILVER, outline=DARK, width=1)


def _body_hiep_si_nam(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.60), _tint(c, 1.28)

    # ── Vai lớn (heavy pauldron) ────────────────────────────────────────
    draw.ellipse([cx-86, bt-12, cx-26, bt+42], fill=c, outline=DARK, width=2)
    draw.ellipse([cx+26, bt-12, cx+86, bt+42], fill=c, outline=DARK, width=2)
    draw.ellipse([cx-76, bt-4,  cx-44, bt+22], fill=cl)
    draw.ellipse([cx+44, bt-4,  cx+76, bt+22], fill=cl)
    # Spike vai
    draw.polygon([(cx-56, bt-12), (cx-48, bt-12), (cx-52, bt-28)], fill=GOLD)
    draw.polygon([(cx+48, bt-12), (cx+56, bt-12), (cx+52, bt-28)], fill=GOLD)

    # ── Ngực full plate ────────────────────────────────────────────────
    draw.polygon([(cx-54, bt+4), (cx+54, bt+4),
                  (cx+46, bt+int(bh*.62)), (cx-46, bt+int(bh*.62))],
                 fill=c, outline=DARK, width=2)
    draw.line([(cx, bt+14), (cx, bt+int(bh*.58))], fill=cd, width=3)
    draw.line([(cx-40, bt+int(bh*.30)), (cx+40, bt+int(bh*.30))], fill=cd, width=2)
    draw.line([(cx-36, bt+int(bh*.46)), (cx+36, bt+int(bh*.46))], fill=cd, width=2)
    # Ngực highlight
    draw.ellipse([cx-18, bt+12, cx+18, bt+40], fill=cl)

    # ── Belt + tasset ──────────────────────────────────────────────────
    by = bt + int(bh * .62)
    draw.rectangle([cx-50, by, cx+50, by+14], fill=GOLD, outline=DARK, width=1)
    draw.rectangle([cx-12, by+2, cx+12, by+12], fill=cl)
    # Tasset (giáp đùi)
    draw.rectangle([cx-50, by+14, cx-14, by+46], fill=c, outline=DARK, width=1)
    draw.rectangle([cx+14, by+14, cx+50, by+46], fill=c, outline=DARK, width=1)

    # ── Greaves (ống chân) ─────────────────────────────────────────────
    draw.rectangle([cx-42, by+46, cx-12, bb], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx+12, by+46, cx+42, bb], fill=cd, outline=DARK, width=1)
    draw.line([(cx-42, by+48), (cx-12, by+48)], fill=GOLD, width=2)
    draw.line([(cx+12, by+48), (cx+42, by+48)], fill=GOLD, width=2)

    # ── Khiên lớn (trái) ───────────────────────────────────────────────
    shx, shy = cx-76, bt+20
    draw.polygon([(shx-18, shy), (shx+18, shy),
                  (shx+18, shy+60), (shx, shy+80), (shx-18, shy+60)],
                 fill=c, outline=DARK, width=2)
    draw.polygon([(shx-12, shy+3), (shx+12, shy+3),
                  (shx+12, shy+54), (shx, shy+72), (shx-12, shy+54)],
                 outline=GOLD, width=2)
    draw.line([(shx, shy+10), (shx, shy+70)],        fill=cd, width=2)
    draw.line([(shx-12, shy+40), (shx+12, shy+40)],  fill=cd, width=2)
    draw.ellipse([shx-7, shy+34, shx+7, shy+46],     fill=GOLD, outline=DARK, width=1)

    # ── Giáo / Lance (phải) ────────────────────────────────────────────
    sx = cx + 68
    draw.line([(sx, bt-20), (sx, bb-6)], fill=_mix(c, DARK, 0.4), width=5)
    draw.line([(sx, bt-20), (sx, bb-6)], fill=cl, width=1)
    draw.polygon([(sx-10, bt-18), (sx+10, bt-18), (sx, bt-40)], fill=SILVER, outline=DARK, width=1)
    draw.rectangle([sx-10, bt+26, sx+10, bt+34], fill=GOLD, outline=DARK, width=1)


def _body_hiep_si_nu(draw, cx, bt, bb, c):
    bh = bb - bt
    cd, cl = _shade(c, 0.60), _tint(c, 1.28)

    # ── Vai ────────────────────────────────────────────────────────────
    draw.ellipse([cx-70, bt-10, cx-22, bt+32], fill=c, outline=DARK, width=2)
    draw.ellipse([cx+22, bt-10, cx+70, bt+32], fill=c, outline=DARK, width=2)
    draw.ellipse([cx-62, bt-2,  cx-34, bt+18], fill=cl)
    draw.ellipse([cx+34, bt-2,  cx+62, bt+18], fill=cl)

    # ── Ngực (corset giáp) ─────────────────────────────────────────────
    draw.polygon([(cx-44, bt+4), (cx+44, bt+4),
                  (cx+34, bt+int(bh*.42)), (cx-34, bt+int(bh*.42))],
                 fill=c, outline=DARK, width=2)
    draw.line([(cx, bt+12), (cx, bt+int(bh*.38))], fill=cd, width=2)
    draw.line([(cx-32, bt+int(bh*.25)), (cx+32, bt+int(bh*.25))], fill=cd, width=2)

    # ── Váy giáp bồng ──────────────────────────────────────────────────
    by = bt + int(bh * .42)
    draw.rectangle([cx-36, by, cx+36, by+10], fill=GOLD, outline=DARK, width=1)
    draw.polygon([(cx-34, by+10), (cx+34, by+10),
                  (cx+56, by+52), (cx-56, by+52)],
                 fill=c, outline=DARK, width=1)
    # Váy segments
    for i in range(1, 4):
        y = by + 10 + i * 11
        x_off = 34 + i * 7
        draw.line([(cx-x_off+2, y), (cx+x_off-2, y)], fill=cd, width=1)

    # ── Boots ──────────────────────────────────────────────────────────
    draw.rectangle([cx-40, by+52, cx-10, bb], fill=cd, outline=DARK, width=1)
    draw.rectangle([cx+10, by+52, cx+40, bb], fill=cd, outline=DARK, width=1)
    draw.line([(cx-40, by+54), (cx-10, by+54)], fill=GOLD, width=2)
    draw.line([(cx+10, by+54), (cx+40, by+54)], fill=GOLD, width=2)

    # ── Khiên tròn (trái) ──────────────────────────────────────────────
    shx, shy = cx-66, bt+26
    draw.ellipse([shx-22, shy, shx+22, shy+44], fill=c, outline=DARK, width=2)
    draw.ellipse([shx-15, shy+6, shx+15, shy+38], outline=GOLD, width=2)
    draw.ellipse([shx-6, shy+16, shx+6, shy+28],  fill=GOLD, outline=DARK, width=1)

    # ── Kiếm (phải) ────────────────────────────────────────────────────
    sx = cx + 62
    draw.polygon([(sx-4, bt+5), (sx+4, bt+5), (sx+2, bb-8), (sx-2, bb-8)],
                 fill=SILVER, outline=DARK, width=1)
    draw.polygon([(sx-4, bt+5), (sx+4, bt+5), (sx, bt-4)], fill=LIGHT)
    draw.rectangle([sx-14, bt+22, sx+14, bt+29], fill=GOLD, outline=DARK, width=1)
    draw.rectangle([sx-4,  bt+29, sx+4,  bt+48], fill=_mix(GOLD, DARK, 0.5), outline=DARK, width=1)


# ── Dispatch ───────────────────────────────────────────────────────────────

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


# ══════════════════════════════════════════════════════════════════════
# Main frame builder
# ══════════════════════════════════════════════════════════════════════

def make_character_frame(character_type: str, face_img: Image.Image,
                         gioi_tinh: str = "nam", size: int = 400) -> Image.Image:
    """
    Ghép mặt học sinh vào toàn thân nhân vật.
    Dùng canvas RGB (không RGBA) để tránh lỗi alpha composite over black.
    """
    cfg    = CHARACTERS.get(character_type, CHARACTERS["chien_binh"])
    color  = hex_to_rgb(cfg["color"])
    bg_rgb = hex_to_rgb(cfg["bg"])
    name   = cfg["name"]
    gt     = "nu" if gioi_tinh in ("nu", "nữ", "female", "f") else "nam"

    W, H = size, int(size * 1.35)
    cx   = W // 2

    # ── 1. Canvas RGB nền nhân vật ────────────────────────────────────
    canvas = Image.new("RGB", (W, H), bg_rgb)

    # ── 2. Glow nền (alpha_composite đúng cách) ───────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    glow_cy = H // 2 + 30
    for r in range(W // 2, 4, -6):
        alpha = int(50 * (1 - r / (W // 2)))
        gd.ellipse([cx-r, glow_cy-r, cx+r, glow_cy+r], fill=(*color, alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(canvas)

    # ── 3. Góc trang trí ─────────────────────────────────────────────
    for dx, dy in [(14, 14), (W-14, 14), (14, H-14), (W-14, H-14)]:
        draw.ellipse([dx-5, dy-5, dx+5,  dy+5],  fill=color)
        draw.ellipse([dx-9, dy-9, dx+9,  dy+9],  outline=_tint(color, 1.3), width=1)

    # ── 4. Thông số mặt ──────────────────────────────────────────────
    face_sz = size // 3
    face_x  = cx - face_sz // 2
    face_y  = 18
    face_cx = cx
    face_cy = face_y + face_sz // 2

    # Tóc nữ (vẽ trước để nằm phía sau mặt)
    if gt == "nu":
        _draw_female_hair(draw, face_x, face_y, face_sz, color)

    # ── 5. Vòng hào quang quanh mặt (alpha_composite) ─────────────────
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd   = ImageDraw.Draw(ring)
    rc   = _tint(color, 1.4)
    for w in range(10, 0, -2):
        a = w * 22
        rd.ellipse([face_cx - face_sz//2 - w, face_cy - face_sz//2 - w,
                    face_cx + face_sz//2 + w, face_cy + face_sz//2 + w],
                   outline=(*rc, a), width=2)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), ring).convert("RGB")
    draw   = ImageDraw.Draw(canvas)

    # ── 6. Dán mặt (RGBA → RGB với mask) ─────────────────────────────
    face_round = crop_circle(face_img, face_sz)
    # Paste RGBA onto RGB canvas using alpha channel as mask
    canvas.paste(face_round.convert("RGB"), (face_x, face_y),
                 mask=face_round.split()[3])
    draw = ImageDraw.Draw(canvas)

    # ── 7. Cổ ────────────────────────────────────────────────────────
    neck_top = face_y + face_sz
    neck_bot = neck_top + 16
    skin     = (210, 165, 125)
    draw.rectangle([cx-11, neck_top, cx+11, neck_bot], fill=skin, outline=DARK, width=1)

    # ── 8. Thân nhân vật ─────────────────────────────────────────────
    body_top = neck_bot
    body_bot = H - 70
    fn = _BODY_DRAW.get((character_type, gt),
                        _BODY_DRAW.get((character_type, "nam"), _body_chien_binh_nam))
    fn(draw, cx, body_top, body_bot, color)

    # ── 9. Banner tên ─────────────────────────────────────────────────
    bny, bnh = H - 58, 30
    draw.rectangle([cx-90, bny, cx+90, bny+bnh],
                   fill=_shade(color, 0.50), outline=color, width=2)
    font = _load_font(13)
    txt  = name.upper() + (" ♀" if gt == "nu" else " ♂")
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx - tw//2, bny + (bnh-th)//2), txt, fill=LIGHT, font=font)

    # ── 10. Thanh XP ──────────────────────────────────────────────────
    bar_y = bny + bnh + 8
    draw.rectangle([cx-70, bar_y, cx+70, bar_y+6],
                   fill=_shade(color, 0.30), outline=DARK, width=1)
    draw.rectangle([cx-70, bar_y, cx+10,  bar_y+6], fill=color)

    return canvas


# ══════════════════════════════════════════════════════════════════════
# Base64 helpers
# ══════════════════════════════════════════════════════════════════════

def b64_to_image(b64: str) -> Image.Image:
    data = base64.b64decode(b64.split(",")[-1])
    return Image.open(io.BytesIO(data))


def image_to_b64(img: Image.Image, fmt="JPEG") -> str:
    buf  = io.BytesIO()
    img.save(buf, format=fmt, quality=88)
    b64  = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


# ══════════════════════════════════════════════════════════════════════
# Main pipeline
# ══════════════════════════════════════════════════════════════════════

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
