"""Avatar generation: PhotoMaker → AnimeGAN2 → PIL fallback."""
import io
import base64
import logging
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

from app.config import CHARACTERS, REPLICATE_API_TOKEN

logger = logging.getLogger(__name__)

# ── Color palette & helpers ──────────────────────────────────────────────────
DARK   = (18,  14,  32)
LIGHT  = (240, 235, 255)
GOLD   = (215, 170,  50)
SILVER = (185, 192, 202)

def _shade(c: tuple, f: float) -> tuple:
    return tuple(max(0, int(x * f)) for x in c)

def _tint(c: tuple, f: float) -> tuple:
    return tuple(min(255, int(x * f)) for x in c)

def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _load_font(size: int = 13):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ── PhotoMaker prompts (công thức: "[mô tả] img, [style], [chất lượng]") ──────
# Token "img" bắt buộc — PhotoMaker dùng nó để neo danh tính khuôn mặt.

_PM_PROMPTS = {
    "chien_binh": (
        "anime manga portrait of a young math warrior img, "
        "glowing cyan energy armor, energy sword, floating math equations and numbers, "
        "fierce heroic expression, dynamic lighting, clean line art, vibrant colors, "
        "detailed anime eyes, high quality illustration"
    ),
    "phu_thuy": (
        "anime manga portrait of a young math mage img, "
        "glowing purple magical robes, crystal staff with math symbols, "
        "floating geometric shapes and numbers, mysterious expression, "
        "magical sparkles, clean line art, vibrant colors, high quality illustration"
    ),
    "xa_thu": (
        "anime manga portrait of a young math ranger img, "
        "glowing green archer armor, energy bow and arrow, "
        "floating math equations, focused determined expression, "
        "forest hints background, clean line art, vibrant colors, "
        "detailed anime eyes, high quality illustration"
    ),
    "hiep_si": (
        "anime manga portrait of a young math knight img, "
        "glowing golden plate armor, shield with math symbols, "
        "brave noble expression, royal golden light, "
        "floating numbers and equations, clean line art, vibrant colors, "
        "high quality illustration"
    ),
}
_PM_NEGATIVE = (
    "ugly, deformed, blurry, low quality, bad anatomy, extra fingers, "
    "old, elderly, wrinkles, nsfw, watermark, realistic photo, photorealistic, "
    "mutation, poorly drawn face, out of frame"
)


def _cartoon_photomaker(img: Image.Image, character_type: str = "chien_binh",
                         gioi_tinh: str = "nam", timeout_sec: int = 65) -> Image.Image:
    """
    PhotoMaker Style (tencentarc/photomaker-style) — Anime portrait.
    Dùng async prediction + polling để kiểm soát timeout,
    tránh block request quá giới hạn Railway (~100s).
    Timeout 65s → worst-case tổng với AnimeGAN2 fallback ≈ 90s < 100s.
    """
    import replicate as _rep
    import httpx
    import os
    import time

    token = os.getenv("REPLICATE_API_TOKEN") or REPLICATE_API_TOKEN
    if not token:
        raise ValueError("REPLICATE_API_TOKEN chưa được cấu hình")
    os.environ["REPLICATE_API_TOKEN"] = token

    # Encode ảnh thành data URI
    img_sq = img.convert("RGB").resize((512, 512), Image.LANCZOS)
    buf = io.BytesIO()
    img_sq.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    # Prompt: thêm giới tính vào cuối để model render đúng
    base_prompt = _PM_PROMPTS.get(character_type, _PM_PROMPTS["chien_binh"])
    gt_tag = "female girl" if gioi_tinh.lower() in ("nu", "nữ", "female") else "male boy"
    prompt = f"{base_prompt}, {gt_tag}"

    # Tạo prediction không chặn (non-blocking)
    prediction = _rep.predictions.create(
        model="tencentarc/photomaker-style",
        input={
            "input_image":          data_uri,
            "prompt":               prompt,
            "negative_prompt":      _PM_NEGATIVE,
            "style_name":           "Anime",
            "num_steps":            50,
            "style_strength_ratio": 35,
            "guidance_scale":       5.0,
            "num_outputs":          1,
        },
    )
    logger.info(f"[avatar] PhotoMaker prediction created id={prediction.id}")

    # Poll cho đến khi xong hoặc hết timeout
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        prediction.reload()
        status = prediction.status
        if status == "succeeded":
            out = prediction.output
            url = str(out[0]) if isinstance(out, list) else str(out)
            if not url.startswith("http"):
                raise ValueError(f"PhotoMaker output không phải URL: {url!r}")
            resp = httpx.get(url, timeout=30)
            resp.raise_for_status()
            result = Image.open(io.BytesIO(resp.content)).convert("RGB")
            logger.info(f"[avatar] PhotoMaker OK ({time.time()-t0:.1f}s): {result.size}")
            return result
        if status in ("failed", "canceled"):
            raise RuntimeError(f"PhotoMaker prediction {status}: {prediction.error}")
        time.sleep(3)

    # Hết timeout → huỷ prediction, raise để fallback AnimeGAN2
    try:
        prediction.cancel()
    except Exception:
        pass
    raise TimeoutError(f"[avatar] PhotoMaker timeout sau {timeout_sec}s → fallback AnimeGAN2")


# ── AnimeGAN2 (fallback) ─────────────────────────────────────────────────────

def _cartoon_ai(img: Image.Image) -> Image.Image:
    """Gọi AnimeGAN2 Hayao qua Replicate — fallback khi PhotoMaker timeout."""
    import replicate
    import httpx
    import os

    token = os.getenv("REPLICATE_API_TOKEN") or REPLICATE_API_TOKEN
    if not token:
        raise ValueError("REPLICATE_API_TOKEN chưa được cấu hình")
    os.environ["REPLICATE_API_TOKEN"] = token

    img_sq = img.convert("RGB").resize((512, 512), Image.LANCZOS)
    buf = io.BytesIO()
    img_sq.save(buf, format="JPEG", quality=95)
    buf.seek(0)

    output = replicate.run(
        "ptran1203/pytorch-animegan:7d44f1878a07e7b5a32af9727c1f6120cac04203d48f3f7b0432e28fa8e5c6b6",
        input={"image": buf, "style": "Hayao"},
    )
    url = str(output[0]) if isinstance(output, list) else str(output)
    if not url.startswith("http"):
        raise ValueError(f"Replicate output không phải URL: {url!r}")

    resp = httpx.get(url, timeout=60)
    resp.raise_for_status()
    result = Image.open(io.BytesIO(resp.content)).convert("RGB")
    logger.info(f"[avatar] AnimeGAN2 OK: {result.size}")
    return result


def _cartoon_pil(img: Image.Image) -> Image.Image:
    """Fallback PIL: tăng độ sắc nét + màu sắc nhẹ."""
    try:
        rgb = img.convert("RGB")
        out = ImageEnhance.Color(rgb).enhance(1.25)
        out = ImageEnhance.Contrast(out).enhance(1.20)
        out = ImageEnhance.Brightness(out).enhance(1.05)
        out = ImageEnhance.Sharpness(out).enhance(1.5)
        return out
    except Exception as e:
        logger.error(f"_cartoon_pil error: {e}", exc_info=True)
        return img.convert("RGB")


def apply_cartoon_filter(img: Image.Image,
                          character_type: str = "chien_binh",
                          gioi_tinh: str = "nam") -> Image.Image:
    """
    Thứ tự ưu tiên:
      1. PhotoMaker Style (tencentarc/photomaker-style)  (~30-65s, timeout 65s)
      2. AnimeGAN2 Hayao                                 (~15-25s)
      3. PIL enhance                                     (instant, always works)
    Worst-case tổng ≈ 90s — dưới giới hạn 100s của Railway.
    """
    import os
    token = os.getenv("REPLICATE_API_TOKEN") or REPLICATE_API_TOKEN
    if token:
        # 1️⃣ PhotoMaker Style
        try:
            result = _cartoon_photomaker(img, character_type=character_type,
                                         gioi_tinh=gioi_tinh, timeout_sec=65)
            logger.info("✅ PhotoMaker thành công")
            return result
        except Exception as e:
            logger.warning(f"⚠️ PhotoMaker thất bại → AnimeGAN2: {e}")

        # 2️⃣ AnimeGAN2 Hayao
        try:
            result = _cartoon_ai(img)
            logger.info("✅ AnimeGAN2 thành công (fallback)")
            return result
        except Exception as e:
            logger.warning(f"⚠️ AnimeGAN2 thất bại → PIL: {e}")

    # 3️⃣ PIL
    logger.info("🎨 PIL portrait-enhance (final fallback)")
    return _cartoon_pil(img)


# ── Circle crop ──────────────────────────────────────────────────────────────

def _crop_circle(img: Image.Image, size: int) -> Image.Image:
    """Crop ảnh thành hình tròn, trả về RGBA (nền trong suốt)."""
    img_sq = img.convert("RGB").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = img_sq.convert("RGBA")
    out.putalpha(mask)
    return out


# ── Body drawing functions ───────────────────────────────────────────────────
# Signature: (draw, cx, y0, y1, color, gt)
#   draw  = ImageDraw.Draw trên canvas RGB
#   cx    = center X
#   y0    = top of body area
#   y1    = bottom of body area
#   color = character RGB color
#   gt    = "nam" | "nu"

def _body_chien_binh(draw, cx, y0, y1, color, gt):
    """Chiến Binh: armor cyan, kiếm năng lượng."""
    c = color
    # ── Torso ──
    w = 52 if gt == "nam" else 44
    draw.polygon([
        (cx - w,     y0 + 18), (cx + w,     y0 + 18),
        (cx + w - 8, y0 + 88), (cx - w + 8, y0 + 88),
    ], fill=_shade(c, 0.70), outline=DARK, width=2)

    # ── Shoulders ──
    sh = 36 if gt == "nam" else 30
    draw.ellipse([cx - w - sh, y0 + 4, cx - w + sh // 2, y0 + 48],
                 fill=c, outline=DARK, width=2)
    draw.ellipse([cx + w - sh // 2, y0 + 4, cx + w + sh, y0 + 48],
                 fill=c, outline=DARK, width=2)

    # ── Chest gem ──
    draw.ellipse([cx - 16, y0 + 30, cx + 16, y0 + 60],
                 fill=_tint(c, 1.5), outline=DARK, width=1)
    draw.ellipse([cx - 9, y0 + 37, cx + 9, y0 + 53], fill=LIGHT)

    # ── Belt ──
    draw.rectangle([cx - w + 8, y0 + 86, cx + w - 8, y0 + 100],
                   fill=GOLD, outline=DARK, width=2)
    draw.rectangle([cx - 10, y0 + 84, cx + 10, y0 + 102],
                   fill=GOLD, outline=DARK, width=2)

    # ── Arms ──
    aw = 25 if gt == "nam" else 20
    draw.polygon([
        (cx - w - sh, y0 + 8), (cx - w, y0 + 8),
        (cx - w + 5, y0 + 78), (cx - w - sh + 8, y0 + 78),
    ], fill=_shade(c, 0.80), outline=DARK, width=1)
    draw.polygon([
        (cx + w, y0 + 8), (cx + w + sh, y0 + 8),
        (cx + w + sh - 8, y0 + 78), (cx + w - 5, y0 + 78),
    ], fill=_shade(c, 0.80), outline=DARK, width=1)

    # ── Legs ──
    leg_top = y0 + 100
    leg_bot = y1 - 22
    lw = 34 if gt == "nam" else 30
    draw.polygon([
        (cx - lw, leg_top), (cx - 6, leg_top),
        (cx - 8, leg_bot),  (cx - lw - 2, leg_bot),
    ], fill=_shade(c, 0.58), outline=DARK, width=1)
    draw.polygon([
        (cx + 6, leg_top),  (cx + lw, leg_top),
        (cx + lw + 2, leg_bot), (cx + 8, leg_bot),
    ], fill=_shade(c, 0.58), outline=DARK, width=1)

    # ── Boots ──
    draw.polygon([
        (cx - lw - 4, leg_bot), (cx - 5, leg_bot),
        (cx - 5, y1),           (cx - lw - 6, y1),
    ], fill=_shade(c, 0.38), outline=DARK, width=2)
    draw.polygon([
        (cx + 5, leg_bot),  (cx + lw + 4, leg_bot),
        (cx + lw + 6, y1),  (cx + 5, y1),
    ], fill=_shade(c, 0.38), outline=DARK, width=2)

    # ── Energy sword (right side) ──
    sw_x = cx + w + sh + 10
    sw_y0 = y0 + 15
    sw_y1 = y0 + 105
    draw.rectangle([sw_x - 3, sw_y0, sw_x + 3, sw_y1],
                   fill=SILVER, outline=DARK, width=1)
    draw.polygon([
        (sw_x - 3, sw_y0), (sw_x + 3, sw_y0), (sw_x, sw_y0 - 22),
    ], fill=_tint(c, 1.6))
    draw.rectangle([sw_x - 9, sw_y1 - 5, sw_x + 9, sw_y1 + 5],
                   fill=GOLD, outline=DARK, width=1)


def _body_phu_thuy(draw, cx, y0, y1, color, gt):
    """Phù Thủy: áo choàng rộng, gậy phép, cầu năng lượng."""
    c = color
    rw_top = 38 if gt == "nam" else 34
    rw_bot = 72 if gt == "nam" else 68

    # ── Áo choàng (trapezoid) ──
    draw.polygon([
        (cx - rw_top, y0 + 18), (cx + rw_top, y0 + 18),
        (cx + rw_bot, y1 - 8),  (cx - rw_bot, y1 - 8),
    ], fill=_shade(c, 0.58), outline=DARK, width=2)

    # ── Lớp áo trong ──
    draw.polygon([
        (cx - 24, y0 + 18), (cx + 24, y0 + 18),
        (cx + 38, y0 + 80), (cx - 38, y0 + 80),
    ], fill=_shade(c, 0.78), outline=DARK, width=1)

    # ── Ngôi sao trang trí ──
    for sx, sy in [(cx - 18, y0 + 48), (cx + 14, y0 + 62), (cx, y0 + 92)]:
        draw.ellipse([sx - 5, sy - 5, sx + 5, sy + 5],
                     fill=_tint(c, 1.4), outline=DARK, width=1)

    # ── Thắt lưng ──
    draw.rectangle([cx - rw_top - 4, y0 + 78, cx + rw_top + 4, y0 + 90],
                   fill=GOLD, outline=DARK, width=2)

    # ── Ống tay rộng ──
    sw = 24 if gt == "nam" else 20
    draw.polygon([
        (cx - rw_top, y0 + 16), (cx - rw_top - sw, y0 + 8),
        (cx - rw_top - sw - 22, y0 + 68), (cx - rw_top - 4, y0 + 74),
    ], fill=_shade(c, 0.68), outline=DARK, width=1)
    draw.polygon([
        (cx + rw_top, y0 + 16), (cx + rw_top + sw, y0 + 8),
        (cx + rw_top + sw + 22, y0 + 68), (cx + rw_top + 4, y0 + 74),
    ], fill=_shade(c, 0.68), outline=DARK, width=1)

    # ── Gậy phép (phải) ──
    sx = cx + rw_top + sw + 30
    draw.rectangle([sx - 2, y0 + 12, sx + 2, y1 - 5],
                   fill=_shade(GOLD, 0.85), outline=DARK, width=1)
    draw.ellipse([sx - 11, y0 + 2, sx + 11, y0 + 24],
                 fill=_tint(c, 1.5), outline=DARK, width=2)
    draw.ellipse([sx - 6, y0 + 7, sx + 6, y0 + 19], fill=LIGHT)

    # ── Cầu năng lượng (trái) ──
    ox = cx - rw_top - sw - 18
    draw.ellipse([ox - 14, y0 + 56, ox + 14, y0 + 84],
                 fill=_tint(c, 1.55), outline=DARK, width=2)
    draw.ellipse([ox - 8, y0 + 62, ox + 8, y0 + 78], fill=LIGHT)


def _body_xa_thu(draw, cx, y0, y1, color, gt):
    """Xạ Thủ: áo giáp xanh lá, cung, bao tên."""
    c = color
    tw = 44 if gt == "nam" else 38

    # ── Torso ──
    draw.polygon([
        (cx - tw, y0 + 16), (cx + tw, y0 + 16),
        (cx + tw - 6, y0 + 86), (cx - tw + 6, y0 + 86),
    ], fill=_shade(c, 0.68), outline=DARK, width=2)

    # ── Shoulder pads (nhỏ hơn) ──
    sp = 28 if gt == "nam" else 24
    draw.ellipse([cx - tw - sp, y0 + 6, cx - tw + sp // 2, y0 + 40],
                 fill=c, outline=DARK, width=2)
    draw.ellipse([cx + tw - sp // 2, y0 + 6, cx + tw + sp, y0 + 40],
                 fill=c, outline=DARK, width=2)

    # ── Logo ngực (tam giác) ──
    draw.polygon([
        (cx, y0 + 28), (cx - 14, y0 + 52), (cx + 14, y0 + 52),
    ], fill=_tint(c, 1.4), outline=DARK, width=1)

    # ── Thắt lưng ──
    draw.rectangle([cx - tw + 6, y0 + 84, cx + tw - 6, y0 + 96],
                   fill=_shade(GOLD, 0.90), outline=DARK, width=1)

    # ── Bao tên (phải) ──
    qx = cx + tw + sp + 8
    draw.rectangle([qx - 7, y0 + 12, qx + 7, y0 + 82],
                   fill=_shade(c, 0.50), outline=DARK, width=1)
    for ay in range(y0 + 20, y0 + 76, 18):
        draw.line([qx - 5, ay, qx + 5, ay], fill=GOLD, width=2)

    # ── Tay ──
    draw.polygon([
        (cx - tw - sp, y0 + 8), (cx - tw, y0 + 8),
        (cx - tw + 4, y0 + 74), (cx - tw - sp + 6, y0 + 74),
    ], fill=_shade(c, 0.78), outline=DARK, width=1)
    draw.polygon([
        (cx + tw, y0 + 8), (cx + tw + sp, y0 + 8),
        (cx + tw + sp - 6, y0 + 74), (cx + tw - 4, y0 + 74),
    ], fill=_shade(c, 0.78), outline=DARK, width=1)

    # ── Chân ──
    leg_top = y0 + 96
    leg_bot = y1 - 24
    lw = 32 if gt == "nam" else 28
    draw.polygon([
        (cx - lw, leg_top), (cx - 5, leg_top),
        (cx - 6, leg_bot),  (cx - lw - 1, leg_bot),
    ], fill=_shade(c, 0.58), outline=DARK, width=1)
    draw.polygon([
        (cx + 5, leg_top),  (cx + lw, leg_top),
        (cx + lw + 1, leg_bot), (cx + 6, leg_bot),
    ], fill=_shade(c, 0.58), outline=DARK, width=1)

    # ── Boots ──
    draw.polygon([
        (cx - lw - 3, leg_bot), (cx - 4, leg_bot),
        (cx - 4, y1),           (cx - lw - 4, y1),
    ], fill=_shade(c, 0.38), outline=DARK, width=2)
    draw.polygon([
        (cx + 4, leg_bot), (cx + lw + 3, leg_bot),
        (cx + lw + 4, y1), (cx + 4, y1),
    ], fill=_shade(c, 0.38), outline=DARK, width=2)

    # ── Cung (trái) ──
    bx = cx - tw - sp - 16
    draw.arc([bx - 12, y0 + 12, bx + 12, y0 + 78],
             start=250, end=110, fill=_shade(GOLD, 1.0), width=4)
    draw.line([bx, y0 + 17, bx, y0 + 73], fill=SILVER, width=1)


def _body_hiep_si(draw, cx, y0, y1, color, gt):
    """Hiệp Sĩ: giáp nặng vàng, khiên, vai rộng."""
    c = color
    tw = 58 if gt == "nam" else 52

    # ── Torso (dày) ──
    draw.polygon([
        (cx - tw, y0 + 14), (cx + tw, y0 + 14),
        (cx + tw - 8, y0 + 96), (cx - tw + 8, y0 + 96),
    ], fill=_shade(c, 0.68), outline=DARK, width=3)

    # ── Pauldrons lớn ──
    ps = 36 if gt == "nam" else 30
    draw.ellipse([cx - tw - ps, y0, cx - tw + ps // 2, y0 + 58],
                 fill=c, outline=DARK, width=3)
    draw.ellipse([cx + tw - ps // 2, y0, cx + tw + ps, y0 + 58],
                 fill=c, outline=DARK, width=3)

    # ── Huy hiệu ngực (chữ thập) ──
    draw.rectangle([cx - 5, y0 + 24, cx + 5, y0 + 70],
                   fill=_tint(c, 1.4), outline=DARK, width=1)
    draw.rectangle([cx - 24, y0 + 40, cx + 24, y0 + 52],
                   fill=_tint(c, 1.4), outline=DARK, width=1)

    # ── Thắt lưng ──
    draw.rectangle([cx - tw + 8, y0 + 94, cx + tw - 8, y0 + 110],
                   fill=GOLD, outline=DARK, width=2)
    draw.rectangle([cx - 12, y0 + 92, cx + 12, y0 + 112],
                   fill=_shade(GOLD, 0.80), outline=DARK, width=2)

    # ── Tay giáp ──
    aw = ps
    draw.polygon([
        (cx - tw - ps, y0 + 4), (cx - tw, y0 + 4),
        (cx - tw + 4, y0 + 82), (cx - tw - ps + 8, y0 + 82),
    ], fill=_shade(c, 0.78), outline=DARK, width=2)
    draw.polygon([
        (cx + tw, y0 + 4), (cx + tw + ps, y0 + 4),
        (cx + tw + ps - 8, y0 + 82), (cx + tw - 4, y0 + 82),
    ], fill=_shade(c, 0.78), outline=DARK, width=2)

    # ── Chân giáp ──
    leg_top = y0 + 110
    leg_bot = y1 - 24
    lw = 42 if gt == "nam" else 38
    draw.polygon([
        (cx - lw, leg_top), (cx - 5, leg_top),
        (cx - 7, leg_bot),  (cx - lw - 2, leg_bot),
    ], fill=_shade(c, 0.62), outline=DARK, width=2)
    draw.polygon([
        (cx + 5, leg_top),  (cx + lw, leg_top),
        (cx + lw + 2, leg_bot), (cx + 7, leg_bot),
    ], fill=_shade(c, 0.62), outline=DARK, width=2)

    # ── Greaves ──
    draw.polygon([
        (cx - lw - 4, leg_bot), (cx - 4, leg_bot),
        (cx - 4, y1),           (cx - lw - 6, y1),
    ], fill=_shade(c, 0.42), outline=DARK, width=2)
    draw.polygon([
        (cx + 4, leg_bot), (cx + lw + 4, leg_bot),
        (cx + lw + 6, y1), (cx + 4, y1),
    ], fill=_shade(c, 0.42), outline=DARK, width=2)

    # ── Khiên (trái) ──
    sx = cx - tw - ps - 22
    sy = y0 + 16
    draw.polygon([
        (sx, sy), (sx - 20, sy + 22), (sx - 20, sy + 58),
        (sx, sy + 75), (sx + 20, sy + 58), (sx + 20, sy + 22),
    ], fill=_shade(c, 0.82), outline=DARK, width=2)
    draw.polygon([
        (sx, sy + 8), (sx - 12, sy + 26), (sx - 12, sy + 52),
        (sx, sy + 65), (sx + 12, sy + 52), (sx + 12, sy + 26),
    ], fill=_tint(c, 1.30), outline=DARK, width=1)


# ── Character card ────────────────────────────────────────────────────────────

def make_character_frame(character_type: str, face_img: Image.Image,
                          gioi_tinh: str = "nam", size: int = 400) -> Image.Image:
    """Tạo thẻ nhân vật: nền tối → vẽ thân → dán ảnh mặt tròn → khung UI."""
    cfg   = CHARACTERS.get(character_type, CHARACTERS["chien_binh"])
    color = hex_to_rgb(cfg["color"])
    name  = cfg["name"]
    gt    = "nu" if gioi_tinh.lower() in ("nu", "nữ", "female", "f") else "nam"

    W, H = size, int(size * 1.35)   # 400 × 540
    cx   = W // 2

    # ── Background ───────────────────────────────────────────────────────
    bg = _shade(color, 0.10)
    canvas = Image.new("RGB", (W, H), bg)

    # Radial glow (concentric ellipses overlay)
    glow_cx, glow_cy = cx, int(H * 0.42)
    for i in range(7, 0, -1):
        alpha_val = int(22 * (i / 7))
        rx = int(W * 0.55 * i / 7)
        ry = int(H * 0.48 * i / 7)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(
            [glow_cx - rx, glow_cy - ry, glow_cx + rx, glow_cy + ry],
            fill=(*color, alpha_val),
        )
        canvas = Image.alpha_composite(canvas.convert("RGBA"), layer).convert("RGB")

    draw = ImageDraw.Draw(canvas)

    # ── Face geometry ─────────────────────────────────────────────────────
    face_r  = int(size * 0.285)      # ~114 px
    face_cx = cx
    face_cy = int(H * 0.265)         # ~143 px from top

    body_y0 = face_cy + face_r - 8   # body start (slight overlap with face)
    body_y1 = H - 52                  # body end (above name banner)

    # ── Draw body ─────────────────────────────────────────────────────────
    body_fn = {
        "chien_binh": _body_chien_binh,
        "phu_thuy":   _body_phu_thuy,
        "xa_thu":     _body_xa_thu,
        "hiep_si":    _body_hiep_si,
    }.get(character_type, _body_chien_binh)

    body_fn(draw, cx, body_y0, body_y1, color, gt)

    # ── Face ring halo ────────────────────────────────────────────────────
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd   = ImageDraw.Draw(ring)
    for r_off, alpha_val in [(face_r + 20, 25), (face_r + 13, 55), (face_r + 6, 100)]:
        rd.ellipse(
            [face_cx - r_off, face_cy - r_off, face_cx + r_off, face_cy + r_off],
            outline=(*color, alpha_val), width=4,
        )
    canvas = Image.alpha_composite(canvas.convert("RGBA"), ring).convert("RGB")
    draw   = ImageDraw.Draw(canvas)

    # ── Paste face circle ─────────────────────────────────────────────────
    face_sz   = face_r * 2
    face_circ = _crop_circle(face_img, face_sz)
    face_x    = face_cx - face_r
    face_y    = face_cy - face_r
    canvas.paste(face_circ.convert("RGB"), (face_x, face_y),
                 mask=face_circ.split()[3])
    draw = ImageDraw.Draw(canvas)

    # Hard border around face circle
    draw.ellipse([face_x, face_y, face_x + face_sz - 1, face_y + face_sz - 1],
                 outline=color, width=4)

    # ── Outer border + corner ornaments ───────────────────────────────────
    draw.rectangle([0, 0, W - 1, H - 1], outline=color, width=4)
    for dx, dy in [(14, 14), (W - 14, 14), (14, H - 14), (W - 14, H - 14)]:
        draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=color)
        draw.ellipse([dx - 9, dy - 9, dx + 9, dy + 9],
                     outline=_tint(color, 1.3), width=1)

    # ── Name banner ───────────────────────────────────────────────────────
    bny, bnh = H - 46, 28
    draw.rectangle([cx - 90, bny, cx + 90, bny + bnh],
                   fill=_shade(color, 0.48), outline=color, width=2)
    font = _load_font(13)
    txt  = name.upper() + (" ♀" if gt == "nu" else " ♂")
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, bny + (bnh - th) // 2), txt, fill=LIGHT, font=font)

    # ── XP bar ────────────────────────────────────────────────────────────
    bar_y = bny + bnh + 6
    draw.rectangle([cx - 70, bar_y, cx + 70, bar_y + 6],
                   fill=_shade(color, 0.25), outline=DARK, width=1)
    draw.rectangle([cx - 70, bar_y, cx + 10, bar_y + 6], fill=color)

    return canvas


# ── Public API ────────────────────────────────────────────────────────────────

def b64_to_image(b64: str) -> Image.Image:
    data = base64.b64decode(b64.split(",")[-1])
    return Image.open(io.BytesIO(data))


def image_to_b64(img: Image.Image, fmt: str = "JPEG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=88)
    b64  = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


def generate_avatar_pipeline(face_b64: str, character_type: str,
                              gioi_tinh: str = "nam") -> dict:
    """
    Pipeline đầy đủ:
      1. Decode base64 → PIL Image
      2. AnimeGAN2 (hoặc PIL fallback) → cartoon face
      3. Vẽ thẻ nhân vật (body + face circle + frame)
    Returns: {"ok": True, "cartoon_b64": ..., "final_b64": ...}
          or {"ok": False, "error": ...}
    """
    # Step 1 – decode
    try:
        face_img = b64_to_image(face_b64)
        logger.info(f"[avatar] step1 decode OK  size={face_img.size}")
    except Exception as e:
        logger.error(f"[avatar] step1 decode FAIL: {e}", exc_info=True)
        return {"ok": False, "error": f"Lỗi đọc ảnh gốc: {e}"}

    # Step 2 – anime filter
    try:
        ai_avatar = apply_cartoon_filter(face_img, character_type, gioi_tinh)
        logger.info(f"[avatar] step2 cartoon OK  size={ai_avatar.size}")
    except Exception as e:
        logger.warning(f"[avatar] step2 cartoon FAIL → dùng ảnh gốc: {e}")
        ai_avatar = face_img.convert("RGB")

    # Step 3 – encode cartoon (dùng luôn làm final, không ghép thân hình)
    try:
        cartoon_b64 = image_to_b64(ai_avatar)
        logger.info("[avatar] step3 encode cartoon OK")
    except Exception as e:
        logger.error(f"[avatar] step3 encode cartoon FAIL: {e}", exc_info=True)
        return {"ok": False, "error": f"Lỗi encode ảnh cartoon: {e}"}

    return {"ok": True, "cartoon_b64": cartoon_b64, "final_b64": cartoon_b64}
