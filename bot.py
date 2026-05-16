"""
VInaStudy Bot Telegram — Mini App Edition
Thầy Nguyễn Thành Long — vinastudy.vn

pip install python-telegram-bot==21.0 anthropic python-dotenv

Railway env vars:
    TELEGRAM_TOKEN, ANTHROPIC_API_KEY
    BASE_URL=https://[user].github.io/vinastudy-bot
    CONTENT_DIR=content
"""

import os, logging, base64, json
import database as db
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters,
)

load_dotenv()
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY")
CONTENT_DIR    = Path(os.getenv("CONTENT_DIR", "content"))
BASE_URL       = os.getenv("BASE_URL", "https://vinastudy.vn/baitap")

# ── Cấu hình buổi học ────────────────────────────────────────────────
BUOI_CONFIG = {
    2:  {"ten": "Bài Toán Cấu Tạo Số",                 "video": "https://youtu.be/tQPklWVzur8",                "folder": "bai02"},
    3:  {"ten": "Viết Số Tự Nhiên Thỏa Mãn Điều Kiện", "video": "https://youtu.be/fMegXvbsYPk",                "folder": "bai03"},
    4:  {"ten": "Dãy Số Cách Đều",                      "video": "https://youtu.be/TcJ50kKlyg0",                "folder": "bai04"},
    5:  {"ten": "Biểu Thức Số",                         "video": "https://youtu.be/placeholder_b5",             "folder": "bai05"},
    6:  {"ten": "Tính Tổng Dãy Số Ghép Cặp",           "video": "https://www.youtube.com/watch?v=h1lHS_SGSjA", "folder": "bai06"},
    7:  {"ten": "Tính Tổng Dãy Số Ghép Cặp (Tiếp)",    "video": "https://youtu.be/69v3vUYp3U8",                "folder": "bai07"},
    8:  {"ten": "Ôn Tập Dãy Số + Dãy Hình Quy Luật",   "video": "https://youtu.be/19EXHoiUwTU",                "folder": "bai08"},
    27: {"ten": "Các Bài Toán Về Thời Gian",           "video": "https://www.youtube.com/watch?v=XuH1MmzQOlw", "folder": "bai27"},
}

BTVN_CONFIG = {
    2:  {"so_cau": 2,  "html": "content/lop3/bai02/bai-tap.html"},
    3:  {"so_cau": 3,  "html": "content/lop3/bai03/bai-tap.html"},
    4:  {"so_cau": 3,  "html": "content/lop3/bai04/bai-tap.html"},
    5:  {"so_cau": 3,  "html": "content/lop3/bai05/bai-tap.html"},
    6:  {"so_cau": 2,  "html": "content/lop3/bai06/bai-tap.html"},
    7:  {"so_cau": 2,  "html": "content/lop3/bai07/bai-tap.html"},
    8:  {"so_cau": 3,  "html": "content/lop3/bai08/bai-tap.html"},
    27: {"so_cau": 23, "html": "content/lop3/bai27/bai-tap.html"},
}

# Tên dạng bài cho từng buổi (dùng để đánh giá năng lực)
DANG_BAI = {
    2:  ["Cấu tạo số từ chữ số", "Tìm số theo điều kiện"],
    3:  ["Đếm số thỏa mãn điều kiện", "Số tròn chục/trăm", "Tổng chữ số"],
    4:  ["Số hạng dãy số", "Số hạng thứ N", "Đếm số chẵn/lẻ"],
    5:  ["Biểu thức có nhân chia", "Thứ tự phép tính", "Tính nhanh"],
    6:  ["Ghép cặp dãy chẵn", "Tính tổng dãy số"],
    7:  ["Ghép cặp dãy lẻ", "Dãy hình quy luật"],
    8:  ["Ôn tập dãy số", "Dãy hình theo quy luật"],
    27: ["So sánh đơn vị thời gian", "Tính khoảng thời gian",
         "Tính giờ chuyến tàu", "Xác định thứ trong tuần"],
}

DEFAULT_BUOI = 27
_prompt_cache: dict = {}

# ── Lịch sử kết quả học sinh (in-memory, sẽ thay bằng DB sau) ────────
# {user_id: [{"buoi": X, "diem": Y, "tong": Z, "chi_tiet": {...}, "thoi_gian": "..."}]}
ket_qua_hs: dict = {}

def luu_ket_qua(user_id: int, buoi: int, diem: int, tong: int, chi_tiet: dict):
    if user_id not in ket_qua_hs:
        ket_qua_hs[user_id] = []
    ket_qua_hs[user_id].append({
        "buoi": buoi,
        "diem": diem,
        "tong": tong,
        "phan_tram": round(diem / tong * 100) if tong else 0,
        "chi_tiet": chi_tiet,   # {"q1": True, "q2": False, ...}
        "thoi_gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })

def lich_su_hs(user_id: int) -> list:
    return ket_qua_hs.get(user_id, [])

# ── System prompt ─────────────────────────────────────────────────────
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

# ── Claude helper ─────────────────────────────────────────────────────
async def ask_claude(history: list, user_msg: str, buoi: int = DEFAULT_BUOI) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    history.append({"role": "user", "content": user_msg})
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            system=load_system_prompt(buoi), messages=history,
        )
        reply = resp.content[0].text
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"Claude error: {e}")
        return "❌ Có lỗi, em thử lại sau nhé!"

async def danh_gia_nang_luc(user_id: int, buoi: int, diem: int, tong: int, chi_tiet: dict) -> str:
    """Dùng Claude để đánh giá năng lực và đưa ra lời khuyên."""
    phan_tram = round(diem / tong * 100) if tong else 0
    dang_sai = [k for k, v in chi_tiet.items() if not v]
    lich_su = lich_su_hs(user_id)[-5:]  # 5 lần gần nhất

    lich_su_text = ""
    if lich_su:
        for ls in lich_su:
            lich_su_text += f"  - Buổi {ls['buoi']}: {ls['diem']}/{ls['tong']} ({ls['phan_tram']}%) lúc {ls['thoi_gian']}\n"

    prompt = f"""Em học sinh vừa hoàn thành bài tập Buổi {buoi} — {BUOI_CONFIG.get(buoi,{}).get('ten','')}.

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

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=600,
            system=load_system_prompt(buoi),
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    except Exception as e:
        logger.error(f"Claude eval error: {e}")
        return f"✅ Em đạt {diem}/{tong} câu ({phan_tram}%). Cố gắng ôn tập thêm nhé!"

# ── Menus ─────────────────────────────────────────────────────────────
def make_main_menu() -> ReplyKeyboardMarkup:
    webapp_url = f"{BASE_URL}/content/index.html"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("📝 Làm bài tập", web_app=WebAppInfo(url=webapp_url)),
             KeyboardButton("🎯 Kiểm tra năng lực")],
            [KeyboardButton("📊 Bảng điểm"),   KeyboardButton("📹 Xem video")],
            [KeyboardButton("💬 Hỏi bài"),     KeyboardButton("📚 Chọn buổi học")],
            [KeyboardButton("🗑️ Xoá lịch sử")],
        ],
        resize_keyboard=True,
    )

MAIN_MENU = make_main_menu()

def make_btvn_menu():
    rows = [[KeyboardButton(f"📖 Buổi {b} — {BUOI_CONFIG[b]['ten']}")] for b in sorted(BTVN_CONFIG)]
    rows.append([KeyboardButton("🔙 Về menu chính")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def make_buoi_menu():
    rows = [[KeyboardButton(f"📘 Buổi {k}: {v['ten']}")] for k,v in sorted(BUOI_CONFIG.items())]
    rows.append([KeyboardButton("🔙 Về menu chính")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

BTVN_MENU = make_btvn_menu()
BUOI_MENU = make_buoi_menu()

# ── State ─────────────────────────────────────────────────────────────
user_state: dict = {}

def get_state(uid):
    if uid not in user_state:
        user_state[uid] = {"mode": "menu", "history": [], "buoi": DEFAULT_BUOI}
    return user_state[uid]

def clear_history(uid):
    buoi = user_state.get(uid, {}).get("buoi", DEFAULT_BUOI)
    user_state[uid] = {"mode": "menu", "history": [], "buoi": buoi}

# ── Handlers ──────────────────────────────────────────────────────────
async def dangky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Học sinh đăng ký tên: /dangky Nguyễn Văn An"""
    uid  = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text(
            "📝 *Đăng ký học*\n\n"
            "Nhập lệnh kèm tên của em:\n"
            "`/dangky Họ và tên`\n\n"
            "Ví dụ: `/dangky Nguyễn Văn An`",
            parse_mode="Markdown",
        )
        return
    ho_ten = " ".join(args)
    try:
        hs = db.add_student(uid, ho_ten)
        await update.message.reply_text(
            f"✅ Đăng ký thành công!\n\n"
            f"👤 Tên: *{hs['ho_ten']}*\n"
            f"🎓 Lớp: {hs['lop']}\n\n"
            f"Em có thể bắt đầu làm bài tập ngay! 👇",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU,
        )
    except Exception as e:
        logger.error(f"Dangky error: {e}")
        await update.message.reply_text("❌ Lỗi đăng ký, thử lại nhé!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text(
        f"👋 Chào {update.effective_user.first_name}!\n\n"
        "🎓 Bot học Toán *VInaStudy* — Thầy Nguyễn Thành Long\n\n"
        "Chọn chức năng bên dưới để bắt đầu! 👇",
        parse_mode="Markdown", reply_markup=MAIN_MENU,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    text  = (update.message.text or "").strip()
    state = get_state(uid)

    # ── Web App data (kết quả bài tập từ HTML) ────────────────────────
    if update.message.web_app_data:
        await xu_ly_ket_qua_webapp(update, context)
        return

    # ── 🏠 Bài tập về nhà ────────────────────────────────────────────
    if text == "🏠 Bài tập về nhà":
        state["mode"] = "btvn_menu"
        await update.message.reply_text(
            "🏠 *Bài Tập Về Nhà*\n\nChọn buổi học để làm bài.\n_(Buổi mới nhất ở dưới cùng)_ 👇",
            parse_mode="Markdown", reply_markup=BTVN_MENU,
        )
        return

    # ── Chọn buổi BTVN → mở Web App ──────────────────────────────────
    if text.startswith("📖 Buổi "):
        try:
            so_buoi = int(text.split("Buổi ")[1].split(" —")[0])
        except Exception:
            so_buoi = None

        if so_buoi and so_buoi in BTVN_CONFIG:
            state["buoi"] = so_buoi
            state["mode"] = "btvn_chat"
            state["history"] = []

            cfg      = BTVN_CONFIG[so_buoi]
            ten      = BUOI_CONFIG[so_buoi]["ten"]
            webapp_url = f"{BASE_URL}/{cfg['html']}"

            # Nút mở Web App ngay trong Telegram
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text=f"📝 Làm bài — Buổi {so_buoi}",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]])

            await update.message.reply_text(
                f"🏠 *Bài tập về nhà — Buổi {so_buoi}*\n"
                f"_{ten}_\n\n"
                f"📋 {cfg['so_cau']} câu bài tập\n"
                f"📹 Video: {BUOI_CONFIG[so_buoi]['video']}\n\n"
                f"👇 Nhấn nút bên dưới để làm bài:",
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            await update.message.reply_text(
                "💬 Hoặc nhập câu hỏi nếu cần thầy hướng dẫn!",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("📝 Làm bài tập")],
                     [KeyboardButton("🔙 Về menu chính")]],
                    resize_keyboard=True,
                ),
            )
        else:
            await update.message.reply_text("Buổi này chưa có bài tập.", reply_markup=BTVN_MENU)
        return

    # ── 🎯 Kiểm tra năng lực ─────────────────────────────────────────
    if text == "🎯 Kiểm tra năng lực":
        uid_ls = lich_su_hs(uid)
        if not uid_ls:
            msg = "📊 Em chưa làm bài tập nào. Hãy làm *🏠 Bài tập về nhà* trước nhé!"
        else:
            lines = ["📊 *Tổng kết năng lực của em:*\n"]
            for ls in reversed(uid_ls[-8:]):
                bar = "🟢" if ls["phan_tram"]>=80 else ("🟡" if ls["phan_tram"]>=60 else ("🟠" if ls["phan_tram"]>=40 else "🔴"))
                lines.append(f"{bar} Buổi {ls['buoi']}: *{ls['diem']}/{ls['tong']}* ({ls['phan_tram']}%) — {ls['thoi_gian']}")
            msg = "\n".join(lines)
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    # ── 📊 Bảng điểm ─────────────────────────────────────────────────
    if text == "📊 Bảng điểm":
        uid_ls = lich_su_hs(uid)
        if not uid_ls:
            msg = "📋 Em chưa có kết quả nào. Hãy làm bài tập trước nhé!"
        else:
            lines = ["📋 *Lịch sử bài làm của em:*\n"]
            for i, ls in enumerate(reversed(uid_ls), 1):
                pct = ls["phan_tram"]
                lvl = "🏆" if pct>=80 else ("⭐" if pct>=60 else ("📖" if pct>=40 else "🌱"))
                lines.append(f"{i}. {lvl} Buổi {ls['buoi']} — {ls['diem']}/{ls['tong']} ({pct}%)\n   📅 {ls['thoi_gian']}")
            msg = "\n".join(lines)
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    # ── 📹 Xem video ─────────────────────────────────────────────────
    if text == "📹 Xem video":
        buoi = state.get("buoi", DEFAULT_BUOI)
        cfg  = BUOI_CONFIG[buoi]
        await update.message.reply_text(
            f"📹 *Video — Buổi {buoi}*\n_{cfg['ten']}_\n\n🔗 {cfg['video']}",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
        )
        return

    # ── 💬 Hỏi bài ───────────────────────────────────────────────────
    if text == "💬 Hỏi bài":
        state["mode"] = "chat"
        buoi = state.get("buoi", DEFAULT_BUOI)
        await update.message.reply_text(
            f"💬 *Hỏi bài — Buổi {buoi}: {BUOI_CONFIG[buoi]['ten']}*\n\n"
            "Gõ bài toán cần giải, thầy Long AI sẽ hướng dẫn từng bước! 👇",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
        )
        return

    # ── 📚 Chọn buổi học ─────────────────────────────────────────────
    if text == "📚 Chọn buổi học":
        state["mode"] = "chon_buoi"
        await update.message.reply_text(
            "📚 *Chọn buổi học*", parse_mode="Markdown", reply_markup=BUOI_MENU,
        )
        return

    if text.startswith("📘 Buổi "):
        try:
            so_buoi = int(text.split("Buổi ")[1].split(":")[0])
        except Exception:
            so_buoi = None
        if so_buoi and so_buoi in BUOI_CONFIG:
            state["buoi"] = so_buoi
            state["history"] = []
            state["mode"] = "menu"
            await update.message.reply_text(
                f"✅ Đã chuyển sang *Buổi {so_buoi}: {BUOI_CONFIG[so_buoi]['ten']}*",
                parse_mode="Markdown", reply_markup=MAIN_MENU,
            )
        return

    # ── 🗑️ Xoá lịch sử ───────────────────────────────────────────────
    if text == "🗑️ Xoá lịch sử":
        clear_history(uid)
        await update.message.reply_text("🗑️ Đã xoá lịch sử hội thoại!", reply_markup=MAIN_MENU)
        return

    # ── 🔙 Về menu chính ─────────────────────────────────────────────
    if text == "🔙 Về menu chính":
        state["mode"] = "menu"
        await update.message.reply_text("🏠 Menu chính!", reply_markup=MAIN_MENU)
        return

    # ── Chat / hỏi bài ───────────────────────────────────────────────
    if state["mode"] in ("chat", "btvn_chat"):
        await update.message.chat.send_action("typing")
        reply = await ask_claude(state["history"], text, state.get("buoi", DEFAULT_BUOI))
        await update.message.reply_text(reply, reply_markup=MAIN_MENU)
        return

    # Fallback
    await update.message.reply_text(
        "Chọn chức năng trong menu nhé! Hoặc bấm *💬 Hỏi bài* để hỏi bài toán.",
        parse_mode="Markdown", reply_markup=MAIN_MENU,
    )


async def xu_ly_ket_qua_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận kết quả từ Web App HTML, chấm điểm, đánh giá năng lực."""
    uid   = update.effective_user.id
    state = get_state(uid)

    try:
        data     = json.loads(update.message.web_app_data.data)
        buoi     = data.get("buoi", state.get("buoi", DEFAULT_BUOI))
        diem     = data.get("diem", 0)
        tong     = data.get("tong", 0)
        chi_tiet = data.get("chi_tiet", {})   # {"q1": true, "q2": false, ...}
    except Exception as e:
        logger.error(f"Web app data error: {e}")
        await update.message.reply_text("❌ Lỗi nhận kết quả, em thử lại nhé!", reply_markup=MAIN_MENU)
        return

    # Lưu kết quả vào memory + DB
    luu_ket_qua(uid, buoi, diem, tong, chi_tiet)
    try:
        db.save_result(uid, buoi, diem, tong, chi_tiet)
    except Exception as e:
        logger.warning(f"DB save result: {e}")
    phan_tram = round(diem / tong * 100) if tong else 0

    # Thông báo kết quả ngay
    await update.message.reply_text(
        f"✅ *Đã nộp bài — Buổi {buoi}*\n\n"
        f"📊 Điểm: *{diem}/{tong}* câu ({phan_tram}%)\n\n"
        f"⏳ Đang phân tích năng lực...",
        parse_mode="Markdown",
    )

    # Claude đánh giá năng lực
    await update.message.chat.send_action("typing")
    danh_gia = await danh_gia_nang_luc(uid, buoi, diem, tong, chi_tiet)

    await update.message.reply_text(
        f"🎓 *Đánh giá năng lực*\n\n{danh_gia}\n\n"
        f"📹 Xem lại bài giảng: {BUOI_CONFIG.get(buoi,{}).get('video','')}",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU,
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    state = get_state(uid)
    await update.message.chat.send_action("typing")
    try:
        photo      = update.message.photo[-1]
        file       = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        img_b64    = base64.standard_b64encode(file_bytes).decode("utf-8")
        caption    = update.message.caption or ""
        user_text  = f"Em gửi ảnh bài toán.{' Ghi chú: ' + caption if caption else ''}"
        client     = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        messages   = state["history"] + [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
            {"type": "text",  "text": user_text},
        ]}]
        resp  = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024,
                    system=load_system_prompt(state.get("buoi", DEFAULT_BUOI)), messages=messages)
        reply = resp.content[0].text
        state["history"].append({"role": "user",      "content": user_text + " [ảnh]"})
        state["history"].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply, reply_markup=MAIN_MENU)
    except Exception as e:
        logger.error(f"Photo error: {e}")
        await update.message.reply_text("Chưa đọc được ảnh, em thử lại nhé!", reply_markup=MAIN_MENU)


async def xoa_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text("🗑️ Đã xoá lịch sử!", reply_markup=MAIN_MENU)

async def btvn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_state(update.effective_user.id)["mode"] = "btvn_menu"
    await update.message.reply_text("🏠 Chọn buổi học:", reply_markup=BTVN_MENU)

async def chonbuoi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_state(update.effective_user.id)["mode"] = "chon_buoi"
    await update.message.reply_text("📚 Chọn buổi học:", reply_markup=BUOI_MENU)

async def bangdiem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    uid_ls = lich_su_hs(uid)
    if not uid_ls:
        msg = "📋 Em chưa có kết quả nào. Hãy làm bài tập trước nhé!"
    else:
        lines = ["📋 *Lịch sử bài làm:*\n"]
        for i, ls in enumerate(reversed(uid_ls), 1):
            lvl = "🏆" if ls["phan_tram"]>=80 else ("⭐" if ls["phan_tram"]>=60 else ("📖" if ls["phan_tram"]>=40 else "🌱"))
            lines.append(f"{i}. {lvl} Buổi {ls['buoi']} — {ls['diem']}/{ls['tong']} ({ls['phan_tram']}%) | {ls['thoi_gian']}")
        msg = "\n".join(lines)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)


def main():
    if not TELEGRAM_TOKEN: raise ValueError("Thiếu TELEGRAM_TOKEN")
    if not ANTHROPIC_KEY:  raise ValueError("Thiếu ANTHROPIC_API_KEY")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("dangky",    dangky))
    app.add_handler(CommandHandler("xoa",       xoa_cmd))
    app.add_handler(CommandHandler("btvn",      btvn_cmd))
    app.add_handler(CommandHandler("chonbuoi",  chonbuoi_cmd))
    app.add_handler(CommandHandler("bangdiem",  bangdiem_cmd))
    app.add_handler(MessageHandler(filters.TEXT  & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO,                    handle_photo))
    app.add_error_handler(error_handler)

    # Khởi tạo database
    try:
        db.init_db()
        for so_buoi, info in BUOI_CONFIG.items():
            db.upsert_lesson(so_buoi, info["ten"])
        logger.info("✅ DB ready")
    except Exception as e:
        logger.warning(f"DB init warning: {e}")

    logger.info("VInaStudy Bot dang chay...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
