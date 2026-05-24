"""Avatar generation: PhotoMaker full-body character composite (gender-aware)."""
import io
import base64
import logging
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

from app.config import CHARACTERS, REPLICATE_API_TOKEN

logger = logging.getLogger(__name__)

# ── Color palette & Helpers ────────────────────────────────────────────────
DARK       = (18,  14,  32)
LIGHT      = (240, 235, 255)

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
        "C:\\Windows\\Fonts\\arial.ttf" # Fallback for local testing
    ]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

# ── AI Generation (PhotoMaker) ─────────────────────────────────────────────

def _get_prompt(character_type: str, gt: str) -> str:
    gender_str = "10 year old boy" if gt == "nam" else "10 year old girl"
    
    # Defaults
    armor_desc = "glowing neon armor"
    weapon_desc = "futuristic energy weapon"
    
    if character_type == "chien_binh":
        armor_desc = "glowing bright cyan futuristic armor"
        weapon_desc = "futuristic energy sword"
    elif character_type == "phu_thuy":
        armor_desc = "glowing magical purple robes"
        weapon_desc = "digital math staff"
    elif character_type == "xa_thu":
        armor_desc = "glowing bright green ranger armor"
        weapon_desc = "laser bow and arrow"
    elif character_type == "hiep_si":
        armor_desc = "glowing golden heavy plate armor"
        weapon_desc = "geometry energy shield"

    return f"A close-up manga panel portrait of a {gender_str} math warrior img, upper body shot, head and shoulders, {armor_desc}, holding a {weapon_desc}, bright sunny space galaxy background with colorful floating math equations, 2D comic book art, anime manga style, pencil sketch strokes, cel shaded, vibrant bright pastel colors, halftone patterns"

def _generate_ai_avatar(img: Image.Image, character_type: str, gt: str) -> Image.Image:
    """Gọi PhotoMaker Replicate API để sinh ảnh hoàn chỉnh."""
    import replicate
    import httpx
    import os

    token = os.getenv("REPLICATE_API_TOKEN") or REPLICATE_API_TOKEN
    if not token:
        raise ValueError("REPLICATE_API_TOKEN chưa được cấu hình")
    os.environ["REPLICATE_API_TOKEN"] = token

    # Resize để gửi API nhanh hơn, PhotoMaker khuyên dùng ảnh vuông rõ mặt
    img_resized = img.convert("RGB").resize((512, 512), Image.LANCZOS)
    buf = io.BytesIO()
    img_resized.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    prompt = _get_prompt(character_type, gt)
    
    output = replicate.run(
        "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
        input={
            "input_image": data_uri,
            "prompt": prompt,
            "style_name": "Comic book",
            "style_strength_ratio": 25,
            "negative_prompt": "realistic, photorealistic, 3d, photography, cinematic, real person, photograph, dark, gloomy, sad"
        }
    )

    url = str(output[0]) if isinstance(output, list) else str(output)
    if not url.startswith("http"):
        raise ValueError(f"Replicate output không phải URL: {url!r}")

    resp = httpx.get(url, timeout=60)
    resp.raise_for_status()
    result = Image.open(io.BytesIO(resp.content)).convert("RGB")
    logger.info(f"PhotoMaker output size: {result.size}")
    return result

def _cartoon_pil(img: Image.Image) -> Image.Image:
    """Fallback nếu API lỗi"""
    try:
        rgb = img.convert("RGB")
        out = ImageEnhance.Color(rgb).enhance(1.25)
        out = ImageEnhance.Contrast(out).enhance(1.20)
        return out
    except Exception as e:
        logger.error(f"_cartoon_pil error: {e}", exc_info=True)
        return img.convert("RGB")

def apply_cartoon_filter(img: Image.Image, character_type: str, gioi_tinh: str) -> Image.Image:
    import os
    token = os.getenv("REPLICATE_API_TOKEN") or REPLICATE_API_TOKEN
    gt = "nu" if gioi_tinh.lower() in ("nu", "nữ", "female", "f") else "nam"
    
    if token:
        try:
            result = _generate_ai_avatar(img, character_type, gt)
            logger.info("✅ PhotoMaker thành công")
            return result
        except Exception as e:
            logger.warning(f"⚠️ PhotoMaker thất bại, dùng PIL fallback: {e}")
            
    return _cartoon_pil(img)

# ── Framing ────────────────────────────────────────────────────────────────

def make_character_frame(character_type: str, ai_img: Image.Image, gioi_tinh: str = "nam", size: int = 400) -> Image.Image:
    """Ghép khung UI (tên, thanh XP) đè lên bức ảnh AI đã tạo hoàn chỉnh."""
    cfg    = CHARACTERS.get(character_type, CHARACTERS["chien_binh"])
    color  = hex_to_rgb(cfg["color"])
    name   = cfg["name"]
    gt     = "nu" if gioi_tinh.lower() in ("nu", "nữ", "female", "f") else "nam"

    W, H = size, int(size * 1.35)
    
    # Resize / Crop AI image to fit W x H
    # AI image is usually 1024x1024 (square). We need to crop it to W x H (portrait ratio)
    img_w, img_h = ai_img.size
    target_ratio = W / H
    current_ratio = img_w / img_h
    
    if current_ratio > target_ratio:
        # Image is too wide, crop sides
        new_w = int(img_h * target_ratio)
        left = (img_w - new_w) // 2
        ai_cropped = ai_img.crop((left, 0, left + new_w, img_h))
    else:
        # Image is too tall, crop bottom
        new_h = int(img_w / target_ratio)
        top = 0  # Keep head
        ai_cropped = ai_img.crop((0, top, img_w, top + new_h))
        
    canvas = ai_cropped.resize((W, H), Image.LANCZOS)
    draw = ImageDraw.Draw(canvas)

    # ── Vẽ viền trang trí ──────────────────────────────────────────────
    draw.rectangle([0, 0, W-1, H-1], outline=color, width=4)
    for dx, dy in [(14, 14), (W-14, 14), (14, H-14), (W-14, H-14)]:
        draw.ellipse([dx-5, dy-5, dx+5,  dy+5],  fill=color)
        draw.ellipse([dx-9, dy-9, dx+9,  dy+9],  outline=_tint(color, 1.3), width=1)

    # ── Banner tên ─────────────────────────────────────────────────
    cx = W // 2
    bny, bnh = H - 58, 30
    draw.rectangle([cx-90, bny, cx+90, bny+bnh],
                   fill=_shade(color, 0.50), outline=color, width=2)
    font = _load_font(13)
    txt  = name.upper() + (" ♀" if gt == "nu" else " ♂")
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx - tw//2, bny + (bnh-th)//2), txt, fill=LIGHT, font=font)

    # ── Thanh XP ──────────────────────────────────────────────────
    bar_y = bny + bnh + 8
    draw.rectangle([cx-70, bar_y, cx+70, bar_y+6],
                   fill=_shade(color, 0.30), outline=DARK, width=1)
    draw.rectangle([cx-70, bar_y, cx+10,  bar_y+6], fill=color)

    return canvas

# ── API ────────────────────────────────────────────────────────────────────

def b64_to_image(b64: str) -> Image.Image:
    data = base64.b64decode(b64.split(",")[-1])
    return Image.open(io.BytesIO(data))

def image_to_b64(img: Image.Image, fmt="JPEG") -> str:
    buf  = io.BytesIO()
    img.save(buf, format=fmt, quality=88)
    b64  = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"

def generate_avatar_pipeline(face_b64: str, character_type: str, gioi_tinh: str = "nam") -> dict:
    try:
        face_img = b64_to_image(face_b64)
    except Exception as e:
        return {"ok": False, "error": f"Lỗi đọc ảnh gốc: {e}"}

    try:
        ai_avatar = apply_cartoon_filter(face_img, character_type, gioi_tinh)
    except Exception as e:
        ai_avatar = face_img.convert("RGB")
        logger.warning(f"Cartoon filter error: {e}")

    try:
        cartoon_b64 = image_to_b64(ai_avatar)
    except Exception as e:
        return {"ok": False, "error": f"Lỗi encode AI image: {e}"}

    try:
        final_img = make_character_frame(character_type, ai_avatar, gioi_tinh=gioi_tinh, size=400)
    except Exception as e:
        return {"ok": False, "error": f"Lỗi tạo character frame: {e}"}

    try:
        final_b64 = image_to_b64(final_img)
    except Exception as e:
        return {"ok": False, "error": f"Lỗi encode ảnh cuối: {e}"}

    return {"ok": True, "cartoon_b64": cartoon_b64, "final_b64": final_b64}
