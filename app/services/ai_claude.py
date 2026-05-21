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

    # Xu hướng so với lần trước cùng buổi
    lich_su_cung_buoi = [r for r in lich_su if r.get("buoi") == buoi]
    if lich_su_cung_buoi:
        lan_truoc = lich_su_cung_buoi[-1]["phan_tram"]
        xu_huong = "tăng 📈" if phan_tram > lan_truoc else ("giảm 📉" if phan_tram < lan_truoc else "giữ nguyên ➡️")
        trend_text = f"Lần trước cùng buổi: {lan_truoc}% → lần này: {phan_tram}% ({xu_huong})"
    else:
        trend_text = "Lần đầu làm buổi này"

    overall_text = ""
    if len(lich_su) >= 2:
        recent = lich_su[-5:]
        avg_recent = round(sum(r["phan_tram"] for r in recent) / len(recent))
        overall_text = f"Điểm TB 5 bài gần nhất: {avg_recent}%"

    lich_su_text = ""
    for ls in lich_su[-5:]:
        lich_su_text += f"  - Buổi {ls['buoi']}: {ls['diem']}/{ls['tong']} ({ls['phan_tram']}%)\n"

    ten_buoi = BUOI_CONFIG.get(buoi, {}).get("ten", "")
    dang_bai = ", ".join(DANG_BAI.get(buoi, []))

    prompt = f"""Em học sinh vừa hoàn thành bài tập Buổi {buoi} — {ten_buoi}.

KẾT QUẢ:
- Điểm: {diem}/{tong} câu ({phan_tram}%)
- Câu sai: {", ".join(dang_sai) if dang_sai else "Không có (làm đúng hết!)"}
- Dạng bài buổi này: {dang_bai}

SO SÁNH:
- {trend_text}
{("- " + overall_text) if overall_text else ""}

LỊCH SỬ GẦN ĐÂY:
{lich_su_text if lich_su_text else "  (Chưa có lịch sử)"}

Hãy viết đánh giá ngắn gọn gồm 4 phần:
1. Nhận xét kết quả (1-2 câu, thân thiện với học sinh lớp 3, có khen ngợi)
2. Mức năng lực: 🌱 Mức 1 (<40%) / 📖 Mức 2 (40-60%) / ⭐ Mức 3 (60-80%) / 🏆 Mức 4 (≥80%)
3. Kiến thức cần cải thiện (nêu cụ thể dựa vào câu sai và dạng bài, bỏ qua nếu không có câu sai)
4. 2-3 lời khuyên ôn tập cụ thể

Viết bằng tiếng Việt, thân thiện, dùng emoji, không quá 200 chữ."""

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


async def phan_tich_hoc_sinh(ho_ten: str, results: list) -> str:
    if not results:
        return f"❌ Chưa có dữ liệu bài tập của {ho_ten}."

    tong_bai = len(results)
    diem_tb = round(sum(r["phan_tram"] for r in results) / tong_bai)
    best = max(results, key=lambda r: r["phan_tram"])
    worst = min(results, key=lambda r: r["phan_tram"])

    xu_huong = ""
    if len(results) >= 3:
        dau = [r["phan_tram"] for r in results[-3:]]   # bài cũ nhất
        cuoi = [r["phan_tram"] for r in results[:3]]    # bài mới nhất
        if sum(cuoi) > sum(dau):
            xu_huong = "cải thiện tốt 📈"
        elif sum(cuoi) < sum(dau):
            xu_huong = "có dấu hiệu giảm 📉"
        else:
            xu_huong = "ổn định ➡️"

    ket_qua_text = "\n".join([
        f"  - Buổi {r['so_buoi']} ({r.get('ten_buoi', '')}): {r['phan_tram']}% ({r['diem']}/{r['tong_cau']})"
        for r in results[:10]
    ])

    prompt = f"""Phân tích hồ sơ học sinh để báo cáo với giáo viên:

HỌC SINH: {ho_ten}
TỔNG BÀI: {tong_bai} | ĐIỂM TB: {diem_tb}% | XU HƯỚNG: {xu_huong}
CAO NHẤT: Buổi {best["so_buoi"]} — {best["phan_tram"]}%
THẤP NHẤT: Buổi {worst["so_buoi"]} — {worst["phan_tram"]}%

CHI TIẾT (mới nhất trước):
{ket_qua_text}

Viết phân tích ngắn gọn (150-200 chữ) gồm:
1. Nhận xét tổng quan học lực
2. Điểm mạnh / yếu nổi bật
3. 2-3 gợi ý cụ thể cho giáo viên

Viết bằng tiếng Việt, chuyên nghiệp."""

    try:
        resp = await client.messages.create(
            model="claude-sonnet-4-6", max_tokens=800,
            system="Bạn là chuyên gia tư vấn giáo dục, hỗ trợ giáo viên phân tích năng lực học sinh lớp 3.",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return f"📊 {ho_ten}: {tong_bai} bài, TB {diem_tb}%"
