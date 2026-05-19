import logging
from anthropic import AsyncAnthropic
from app.config import ANTHROPIC_KEY, BUOI_CONFIG, DANG_BAI, CONTENT_DIR

logger = logging.getLogger(__name__)
client = AsyncAnthropic(api_key=ANTHROPIC_KEY)

_prompt_cache: dict = {}

def load_system_prompt(so_buoi: int) -> str:
    if so_buoi in _prompt_cache:
        return _prompt_cache[so_buoi]
    if so_buoi in BUOI_CONFIG:
        path = CONTENT_DIR / "lop3" / BUOI_CONFIG[so_buoi]["folder"] / "system-prompt.txt"
        if path.exists():
            try:
                p = path.read_text(encoding="utf-8")
                _prompt_cache[so_buoi] = p
                return p
            except Exception as e:
                logger.error(f"Lỗi đọc prompt: {e}")
    return "Bạn là thầy Long Vinastudy - trợ lý dạy Toán lớp 3. Giải từng bước bằng tiếng Việt."

async def ask_claude(history: list, user_msg: str, buoi: int) -> str:
    history.append({"role": "user", "content": user_msg})
    try:
        resp = await client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            system=load_system_prompt(buoi), messages=history,
        )
        reply = resp.content[0].text
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"Claude error: {e}")
        return "❌ Có lỗi, em thử lại sau nhé!"

async def ask_claude_with_image(history: list, user_text: str, img_b64: str, buoi: int) -> str:
    try:
        messages = history + [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
            {"type": "text",  "text": user_text},
        ]}]
        resp = await client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            system=load_system_prompt(buoi), messages=messages
        )
        reply = resp.content[0].text
        history.append({"role": "user", "content": user_text + " [ảnh]"})
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"Claude error image: {e}")
        return "❌ Có lỗi xử lý ảnh, em thử lại sau nhé!"

async def danh_gia_nang_luc(diem: int, tong: int, chi_tiet: dict, buoi: int, lich_su: list) -> str:
    phan_tram = round(diem / tong * 100) if tong else 0
    dang_sai = [k for k, v in chi_tiet.items() if not v]
    
    lich_su_text = ""
    if lich_su:
        for ls in lich_su[-5:]:
            lich_su_text += f"  - Buổi {ls['buoi']}: {ls['diem']}/{ls['tong']} ({ls['phan_tram']}%) lúc {ls.get('thoi_gian', '')}\n"

    prompt = f"""Em học sinh vừa hoàn thành bài tập Buổi {buoi} — {BUOI_CONFIG.get(buoi,{{}}).get('ten','')}.

KẾT QUẢ:
- Điểm: {diem}/{tong} câu ({phan_tram}%)
- Câu sai: {', '.join(dang_sai) if dang_sai else 'Không có'}
- Dạng bài của buổi: {', '.join(DANG_BAI.get(buoi, []))}

LỊCH SỬ 5 LẦN GẦN NHẤT:
{lich_su_text if lich_su_text else '  (Chưa có lịch sử)'}

Hãy:
1. Nhận xét ngắn gọn về kết quả (1-2 câu, thân thiện với học sinh lớp 3)
2. Xác định mức năng lực: 🌱Mức 1 (0-40%) / 📖Mức 2 (40-60%) / ⭐Mức 3 (60-80%) / 🏆Mức 4 (80-100%)
3. Chỉ ra kiến thức còn hổng (nếu có câu sai)
4. Lời khuyên ôn tập cụ thể (2-3 gợi ý ngắn)

Trả lời bằng tiếng Việt, thân thiện, ngắn gọn, dùng emoji."""

    try:
        resp = await client.messages.create(
            model="claude-sonnet-4-6", max_tokens=600,
            system=load_system_prompt(buoi),
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    except Exception as e:
        logger.error(f"Claude eval error: {e}")
        return f"✅ Em đạt {diem}/{tong} câu ({phan_tram}%). Cố gắng ôn tập thêm nhé!"
