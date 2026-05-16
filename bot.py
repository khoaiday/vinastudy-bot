"""
VInaStudy Bot Telegram
Thầy Nguyễn Thành Long — vinastudy.vn

Cài đặt:
    pip install python-telegram-bot==21.0 anthropic python-dotenv

Env vars (Railway Variables):
    TELEGRAM_TOKEN=<token từ @BotFather>
    ANTHROPIC_API_KEY=<key từ console.anthropic.com>
    BASE_URL=https://vinastudy.vn/baitap
"""

import os
import logging
import base64
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY")
CONTENT_DIR    = Path(os.getenv("CONTENT_DIR", "content"))
BASE_URL       = os.getenv("BASE_URL", "https://vinastudy.vn/baitap")

BUOI_CONFIG = {
    2:  {"ten": "Bài Toán Cấu Tạo Số",                   "video": "https://youtu.be/tQPklWVzur8",                "folder": "bai02"},
    3:  {"ten": "Viết Số Tự Nhiên Thỏa Mãn Điều Kiện",   "video": "https://youtu.be/fMegXvbsYPk",                "folder": "bai03"},
    4:  {"ten": "Dãy Số Cách Đều",                        "video": "https://youtu.be/TcJ50kKlyg0",                "folder": "bai04"},
    5:  {"ten": "Biểu Thức Số",                           "video": "https://youtu.be/placeholder_b5",             "folder": "bai05"},
    6:  {"ten": "Tính Tổng Dãy Số Ghép Cặp",             "video": "https://www.youtube.com/watch?v=h1lHS_SGSjA", "folder": "bai06"},
    7:  {"ten": "Tính Tổng Dãy Số Ghép Cặp (Tiếp)",      "video": "https://youtu.be/69v3vUYp3U8",                "folder": "bai07"},
    8:  {"ten": "Ôn Tập Dãy Số + Dãy Hình Quy Luật",     "video": "https://youtu.be/19EXHoiUwTU",                "folder": "bai08"},
    27: {"ten": "Các Bài Toán Về Thời Gian",             "video": "https://www.youtube.com/watch?v=XuH1MmzQOlw", "folder": "bai27"},
}

# BTVN: file HTML tĩnh nằm trong content/lop3/baiXX/bai-tap.html
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

DEFAULT_BUOI = 27
DEFAULT_SYSTEM_PROMPT = """Bạn là thầy Long Vinastudy - trợ lý dạy Toán lớp 3.
Giải từng bước rõ ràng bằng tiếng Việt, thân thiện với học sinh lớp 3."""

_prompt_cache: dict = {}

def load_system_prompt(so_buoi: int) -> str:
    if so_buoi in _prompt_cache:
        return _prompt_cache[so_buoi]
    if so_buoi not in BUOI_CONFIG:
        return DEFAULT_SYSTEM_PROMPT
    path = CONTENT_DIR / "lop3" / BUOI_CONFIG[so_buoi]["folder"] / "system-prompt.txt"
    if path.exists():
        try:
            p = path.read_text(encoding="utf-8")
            _prompt_cache[so_buoi] = p
            return p
        except Exception as e:
            logger.error(f"Lỗi đọc prompt: {e}")
    return DEFAULT_SYSTEM_PROMPT

# ── Menus ─────────────────────────────────────────────────────────────────────

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Bài tập về nhà"),  KeyboardButton("🎯 Kiểm tra năng lực")],
        [KeyboardButton("📊 Bảng điểm"),        KeyboardButton("📹 Xem video")],
        [KeyboardButton("💬 Hỏi bài"),          KeyboardButton("📚 Chọn buổi học")],
        [KeyboardButton("🗑️ Xoá lịch sử")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Chọn chức năng hoặc nhập câu hỏi...",
)

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

# ── State ─────────────────────────────────────────────────────────────────────

user_state: dict = {}

def get_state(uid):
    if uid not in user_state:
        user_state[uid] = {"mode": "menu", "history": [], "buoi": DEFAULT_BUOI}
    return user_state[uid]

def clear_history(uid):
    buoi = user_state.get(uid, {}).get("buoi", DEFAULT_BUOI)
    user_state[uid] = {"mode": "menu", "history": [], "buoi": buoi}

# ── Claude helper ─────────────────────────────────────────────────────────────

async def ask_claude(history, user_message, buoi=DEFAULT_BUOI):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    history.append({"role": "user", "content": user_message})
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
        return "Có lỗi xảy ra, em thử lại sau nhé!"

# ── Handlers ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text(
        f"Chào {update.effective_user.first_name}!\n\n"
        "Đây là bot học Toán của *VInaStudy*\n"
        "Thầy Nguyễn Thành Long\n\n"
        "Chọn chức năng bên dưới để bắt đầu nhé!",
        parse_mode="Markdown", reply_markup=MAIN_MENU,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    text  = update.message.text.strip()
    state = get_state(uid)

    # 🏠 Bài tập về nhà
    if text == "🏠 Bài tập về nhà":
        state["mode"] = "btvn_menu"
        await update.message.reply_text(
            "🏠 *Bài Tập Về Nhà*\n\nChọn buổi học bên dưới.\n_(Buổi mới nhất ở dưới cùng)_ 👇",
            parse_mode="Markdown", reply_markup=BTVN_MENU,
        )
        return

    # Chọn buổi BTVN
    if text.startswith("📖 Buổi "):
        try:
            so_buoi = int(text.split("Buổi ")[1].split(" —")[0])
        except Exception:
            so_buoi = None
        if so_buoi and so_buoi in BTVN_CONFIG:
            state["mode"] = "btvn_chat"
            state["buoi"] = so_buoi
            state["history"] = []
            cfg = BTVN_CONFIG[so_buoi]
            url = f"{BASE_URL}/{cfg['html']}"
            ten = BUOI_CONFIG[so_buoi]["ten"]
            await update.message.reply_text(
                f"🏠 *Bài tập về nhà — Buổi {so_buoi}*\n_{ten}_\n\n"
                f"📋 {cfg['so_cau']} câu bài tập\n"
                f"👉 Làm bài tại đây:\n{url}\n\n"
                f"💬 Nhập câu hỏi nếu cần thầy hướng dẫn!\n"
                f"📹 {BUOI_CONFIG[so_buoi]['video']}",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("🏠 Bài tập về nhà")],
                     [KeyboardButton("🔙 Về menu chính")]],
                    resize_keyboard=True,
                ),
            )
        else:
            await update.message.reply_text("Buổi này chưa có bài tập về nhà.", reply_markup=BTVN_MENU)
        return

    # 🎯 Kiểm tra năng lực
    if text == "🎯 Kiểm tra năng lực":
        await update.message.reply_text(
            "🎯 *Kiểm tra năng lực*\n\n⏳ Tính năng đang phát triển, em quay lại sau nhé!",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
        )
        return

    # 📊 Bảng điểm
    if text == "📊 Bảng điểm":
        await update.message.reply_text(
            "📊 *Bảng điểm*\n\n⏳ Tính năng đang phát triển!",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
        )
        return

    # 📹 Xem video
    if text == "📹 Xem video":
        buoi = state.get("buoi", DEFAULT_BUOI)
        await update.message.reply_text(
            f"📹 *Video — Buổi {buoi}*\n_{BUOI_CONFIG[buoi]['ten']}_\n\n"
            f"🔗 {BUOI_CONFIG[buoi]['video']}",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
        )
        return

    # 💬 Hỏi bài
    if text == "💬 Hỏi bài":
        state["mode"] = "chat"
        buoi = state.get("buoi", DEFAULT_BUOI)
        await update.message.reply_text(
            f"💬 *Hỏi bài — Buổi {buoi}: {BUOI_CONFIG[buoi]['ten']}*\n\n"
            "Gõ bài toán cần giải, thầy Long AI sẽ giải từng bước! 👇",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
        )
        return

    # 📚 Chọn buổi học
    if text == "📚 Chọn buổi học":
        state["mode"] = "chon_buoi"
        await update.message.reply_text(
            "📚 *Chọn buổi học*\n\nEm đang muốn học buổi nào?",
            parse_mode="Markdown", reply_markup=BUOI_MENU,
        )
        return

    # Chọn buổi học cụ thể
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
                f"Đã chuyển sang *Buổi {so_buoi}: {BUOI_CONFIG[so_buoi]['ten']}*\n\n"
                f"Video: {BUOI_CONFIG[so_buoi]['video']}\n\n"
                "Dùng *Hỏi bài* để học nhé!",
                parse_mode="Markdown", reply_markup=MAIN_MENU,
            )
        else:
            await update.message.reply_text("Không tìm thấy buổi này.", reply_markup=MAIN_MENU)
        return

    # 🗑️ Xoá lịch sử
    if text == "🗑️ Xoá lịch sử":
        clear_history(uid)
        await update.message.reply_text("Đã xoá lịch sử hội thoại! Em bắt đầu lại từ đầu nhé 😊", reply_markup=MAIN_MENU)
        return

    # 🔙 Về menu chính
    if text == "🔙 Về menu chính":
        state["mode"] = "menu"
        await update.message.reply_text("Về menu chính!", reply_markup=MAIN_MENU)
        return

    # Chat mode
    if state["mode"] in ("chat", "btvn_chat"):
        await update.message.chat.send_action("typing")
        reply = await ask_claude(state["history"], text, state.get("buoi", DEFAULT_BUOI))
        await update.message.reply_text(reply, reply_markup=MAIN_MENU)
        return

    # Fallback
    await update.message.reply_text(
        "Em chọn chức năng trong menu bên dưới nhé!\nHoặc bấm *Hỏi bài* để hỏi bài toán.",
        parse_mode="Markdown", reply_markup=MAIN_MENU,
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    state = get_state(uid)
    await update.message.chat.send_action("typing")
    try:
        photo      = update.message.photo[-1]
        file       = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        image_data = base64.standard_b64encode(file_bytes).decode("utf-8")
        caption    = update.message.caption or ""
        user_text  = f"Em gửi ảnh bài toán để thầy xem.{' Ghi chú: ' + caption if caption else ''}"
        client     = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        messages   = state["history"] + [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
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
        await update.message.reply_text("Chưa đọc được ảnh, em thử gửi lại nhé!", reply_markup=MAIN_MENU)


async def xoa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text("Đã xoá lịch sử! Em bắt đầu lại nhé 😊", reply_markup=MAIN_MENU)

async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    buoi = get_state(uid).get("buoi", DEFAULT_BUOI)
    await update.message.reply_text(
        f"Video Buổi {buoi} — {BUOI_CONFIG[buoi]['ten']}\n{BUOI_CONFIG[buoi]['video']}",
        reply_markup=MAIN_MENU,
    )

async def btvn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_state(update.effective_user.id)["mode"] = "btvn_menu"
    await update.message.reply_text("Bài Tập Về Nhà — chọn buổi học:", reply_markup=BTVN_MENU)

async def chon_buoi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_state(update.effective_user.id)["mode"] = "chon_buoi"
    await update.message.reply_text("Chọn buổi học:", reply_markup=BUOI_MENU)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not TELEGRAM_TOKEN: raise ValueError("Thiếu TELEGRAM_TOKEN")
    if not ANTHROPIC_KEY:  raise ValueError("Thiếu ANTHROPIC_API_KEY")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("xoa",      xoa))
    app.add_handler(CommandHandler("video",    video_cmd))
    app.add_handler(CommandHandler("btvn",     btvn_cmd))
    app.add_handler(CommandHandler("chonbuoi", chon_buoi_cmd))
    app.add_handler(MessageHandler(filters.TEXT  & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_error_handler(error_handler)

    logger.info("VInaStudy Bot dang chay...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
