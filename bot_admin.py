"""
VInaStudy — Bot Admin (Thầy Long)
Quản lý học sinh, gửi tài liệu, xem thống kê

Railway env vars:
    ADMIN_BOT_TOKEN  — token bot thầy Long (@BotFather)
    TELEGRAM_TOKEN   — token bot học sinh
    DATABASE_URL
    ADMIN_ID         — telegram_id của thầy Long
"""

import os, logging, asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import database as db

load_dotenv()
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
HS_BOT_TOKEN    = os.getenv("TELEGRAM_TOKEN")   # bot học sinh để broadcast
ADMIN_ID        = int(os.getenv("ADMIN_ID", "0"))

# ── Menu ──────────────────────────────────────────────────────────────
ADMIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("📤 Gửi tài liệu buổi học"), KeyboardButton("📊 Thống kê lớp")],
    [KeyboardButton("⚠️ Nhắc học sinh nộp bài"), KeyboardButton("👥 Danh sách học sinh")],
    [KeyboardButton("➕ Thêm học sinh"),          KeyboardButton("📋 Báo cáo phụ huynh")],
], resize_keyboard=True)

# State admin
admin_state = {"mode": "menu", "buoi_dang_gui": None}

def is_admin(uid): return uid == ADMIN_ID


# ── Handlers ──────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bạn không có quyền truy cập bot này.")
        return
    await update.message.reply_text(
        "👨‍🏫 Chào thầy Long!\n\nBot quản lý VInaStudy sẵn sàng.",
        reply_markup=ADMIN_MENU,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = (update.message.text or "").strip()

    # ── 📤 Gửi tài liệu buổi học ─────────────────────────────────────
    if text == "📤 Gửi tài liệu buổi học":
        admin_state["mode"] = "chon_buoi_gui"
        buoi_list = "\n".join([f"  {k}. Buổi {k} — {v['ten']}"
                                for k,v in sorted(BUOI_INFO.items())])
        await update.message.reply_text(
            f"📤 Gửi tài liệu buổi nào?\n\n{buoi_list}\n\nNhập số buổi:"
        )
        return

    if admin_state["mode"] == "chon_buoi_gui" and text.isdigit():
        so_buoi = int(text)
        if so_buoi in BUOI_INFO:
            admin_state["mode"] = "gui_tai_lieu"
            admin_state["buoi_dang_gui"] = so_buoi
            await update.message.reply_text(
                f"📤 Gửi tài liệu Buổi {so_buoi} — {BUOI_INFO[so_buoi]['ten']}\n\n"
                f"Gửi lần lượt:\n"
                f"1. Ảnh chụp bảng (có thể nhiều ảnh)\n"
                f"2. Link YouTube (nếu có)\n"
                f"3. Link Zoom buổi tiếp theo (nếu có)\n\n"
                f"Khi xong nhấn /broadcast để gửi cho học sinh."
            )
        return

    # ── Link YouTube ─────────────────────────────────────────────────
    if admin_state["mode"] == "gui_tai_lieu" and text.startswith("http"):
        buoi = admin_state["buoi_dang_gui"]
        if "youtube" in text or "youtu.be" in text:
            # Lưu video URL
            lesson = db.get_lesson(buoi)
            if lesson:
                db.upsert_lesson(buoi, BUOI_INFO[buoi]["ten"], video_url=text)
                db.add_material(lesson["id"], "video", text)
            await update.message.reply_text(f"✅ Đã lưu link YouTube Buổi {buoi}")
        elif "zoom" in text:
            lesson = db.get_lesson(buoi)
            if lesson:
                db.upsert_lesson(buoi, BUOI_INFO[buoi]["ten"], zoom_link=text)
            await update.message.reply_text(f"✅ Đã lưu link Zoom")
        return

    # ── 📊 Thống kê lớp ──────────────────────────────────────────────
    if text == "📊 Thống kê lớp":
        admin_state["mode"] = "chon_buoi_stats"
        await update.message.reply_text("📊 Xem thống kê buổi nào? Nhập số buổi:")
        return

    if admin_state["mode"] == "chon_buoi_stats" and text.isdigit():
        so_buoi = int(text)
        stats   = db.get_stats_lesson(so_buoi)
        chua    = db.get_chua_lam(so_buoi)
        chua_text = "\n".join([f"  • {hs['ho_ten']}" for hs in chua]) or "  (Tất cả đã làm ✅)"

        await update.message.reply_text(
            f"📊 Thống kê Buổi {so_buoi}\n\n"
            f"👥 Đã làm: {stats['so_da_lam']}/{stats['tong_hs']} học sinh\n"
            f"📈 Điểm TB: {stats['diem_tb'] or 0}%\n"
            f"🏆 Giỏi (≥80%): {stats['gioi']}\n"
            f"⭐ Khá (60-80%): {stats['kha']}\n"
            f"📖 Cần cố gắng: {stats['can_co_gang']}\n\n"
            f"⚠️ Chưa làm ({len(chua)} em):\n{chua_text}",
            reply_markup=ADMIN_MENU,
        )
        admin_state["mode"] = "menu"
        return

    # ── ⚠️ Nhắc học sinh nộp bài ─────────────────────────────────────
    if text == "⚠️ Nhắc học sinh nộp bài":
        admin_state["mode"] = "nhac_buoi"
        await update.message.reply_text("⚠️ Nhắc bài buổi nào? Nhập số buổi:")
        return

    if admin_state["mode"] == "nhac_buoi" and text.isdigit():
        so_buoi  = int(text)
        chua     = db.get_chua_lam(so_buoi)
        if not chua:
            await update.message.reply_text("✅ Tất cả đã làm bài rồi!", reply_markup=ADMIN_MENU)
            admin_state["mode"] = "menu"
            return

        hs_bot = Bot(token=HS_BOT_TOKEN)
        ok = 0
        for hs in chua:
            try:
                await hs_bot.send_message(
                    chat_id=hs["telegram_id"],
                    text=f"⏰ Nhắc bài!\n\n"
                         f"Em *{hs['ho_ten']}* chưa làm bài tập Buổi {so_buoi}.\n"
                         f"Vào bot làm bài ngay nhé! 👇\n"
                         f"Nhấn *🏠 Bài tập về nhà* → Buổi {so_buoi}",
                    parse_mode="Markdown",
                )
                ok += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Nhắc {hs['ho_ten']} lỗi: {e}")

        await update.message.reply_text(
            f"✅ Đã nhắc {ok}/{len(chua)} học sinh chưa làm Buổi {so_buoi}",
            reply_markup=ADMIN_MENU,
        )
        admin_state["mode"] = "menu"
        return

    # ── 👥 Danh sách học sinh ─────────────────────────────────────────
    if text == "👥 Danh sách học sinh":
        students = db.get_all_students()
        if not students:
            await update.message.reply_text("Chưa có học sinh nào.", reply_markup=ADMIN_MENU)
            return
        lines = [f"{i+1}. {s['ho_ten']} (Lớp {s['lop']})" for i,s in enumerate(students)]
        await update.message.reply_text(
            f"👥 Danh sách học sinh ({len(students)} em):\n\n" + "\n".join(lines),
            reply_markup=ADMIN_MENU,
        )
        return

    # ── ➕ Thêm học sinh ──────────────────────────────────────────────
    if text == "➕ Thêm học sinh":
        admin_state["mode"] = "them_hs"
        await update.message.reply_text(
            "➕ Thêm học sinh mới\n\n"
            "Nhập theo định dạng:\n"
            "`TelegramID | Họ tên | Lớp`\n\n"
            "Ví dụ: `123456789 | Nguyễn Văn An | 3`",
            parse_mode="Markdown",
        )
        return

    if admin_state["mode"] == "them_hs" and "|" in text:
        parts = [p.strip() for p in text.split("|")]
        if len(parts) >= 2:
            try:
                tid   = int(parts[0])
                hoten = parts[1]
                lop   = parts[2] if len(parts) > 2 else "3"
                hs    = db.add_student(tid, hoten, lop)
                await update.message.reply_text(
                    f"✅ Đã thêm: *{hs['ho_ten']}* (Lớp {hs['lop']})\n"
                    f"Telegram ID: `{tid}`",
                    parse_mode="Markdown",
                    reply_markup=ADMIN_MENU,
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Lỗi: {e}")
        admin_state["mode"] = "menu"
        return

    # ── 📋 Báo cáo phụ huynh ─────────────────────────────────────────
    if text == "📋 Báo cáo phụ huynh":
        students = db.get_all_students()
        hs_bot   = Bot(token=HS_BOT_TOKEN)
        gui_ok   = 0
        thang    = datetime.now().strftime("%m/%Y")

        for hs in students:
            if not hs.get("telegram_ph"): continue
            results = db.get_results_student(hs["telegram_id"], limit=20)
            if not results: continue

            tb = round(sum(r["phan_tram"] for r in results) / len(results))
            lvl = "🏆 Giỏi" if tb>=80 else ("⭐ Khá" if tb>=60 else ("📖 Trung bình" if tb>=40 else "🌱 Cần cố gắng"))

            try:
                await hs_bot.send_message(
                    chat_id=hs["telegram_ph"],
                    text=f"📊 *Báo cáo tháng {thang}*\n"
                         f"Học sinh: *{hs['ho_ten']}*\n\n"
                         f"📝 Số bài đã làm: {len(results)}\n"
                         f"📈 Điểm TB: {tb}%\n"
                         f"🎯 Xếp loại: {lvl}\n\n"
                         f"_VInaStudy — Thầy Nguyễn Thành Long_",
                    parse_mode="Markdown",
                )
                gui_ok += 1
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"Báo cáo PH {hs['ho_ten']}: {e}")

        await update.message.reply_text(
            f"✅ Đã gửi báo cáo cho {gui_ok} phụ huynh",
            reply_markup=ADMIN_MENU,
        )
        return


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Thầy gửi ảnh bảng → lưu + broadcast cho học sinh."""
    if not is_admin(update.effective_user.id): return
    if admin_state["mode"] != "gui_tai_lieu":
        await update.message.reply_text("Nhập số buổi trước nhé! Nhấn '📤 Gửi tài liệu buổi học'")
        return

    buoi    = admin_state["buoi_dang_gui"]
    lesson  = db.get_lesson(buoi)
    if lesson:
        # Lấy file_id ảnh lớn nhất
        file_id = update.message.photo[-1].file_id
        db.add_material(lesson["id"], "anh_bang", file_id)
        await update.message.reply_text(
            f"✅ Đã lưu ảnh bảng Buổi {buoi}\n"
            f"Gửi thêm ảnh khác hoặc /broadcast để phát cho học sinh."
        )


async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gửi tài liệu buổi học cho tất cả học sinh."""
    if not is_admin(update.effective_user.id): return
    buoi = admin_state.get("buoi_dang_gui")
    if not buoi:
        await update.message.reply_text("Chưa chọn buổi nào!")
        return

    students  = db.get_all_students()
    materials = db.get_materials(buoi)
    lesson    = db.get_lesson(buoi)
    hs_bot    = Bot(token=HS_BOT_TOKEN)
    ok = 0

    ten   = BUOI_INFO.get(buoi, {}).get("ten", f"Buổi {buoi}")
    video = lesson.get("video_url", "") if lesson else ""

    for hs in students:
        try:
            # Tin nhắn thông báo
            await hs_bot.send_message(
                chat_id=hs["telegram_id"],
                text=f"📚 *Tài liệu Buổi {buoi} — {ten}*\n\n"
                     f"{'📹 Video: ' + video if video else '📹 Video sẽ có sớm!'}\n\n"
                     f"📝 Nhớ làm bài tập về nhà nhé!\n"
                     f"Nhấn *🏠 Bài tập về nhà* → Buổi {buoi}",
                parse_mode="Markdown",
            )
            # Gửi ảnh bảng
            for mat in materials:
                if mat["loai"] == "anh_bang":
                    await hs_bot.send_photo(
                        chat_id=hs["telegram_id"],
                        photo=mat["url"],
                        caption=f"📸 Ảnh bảng Buổi {buoi}",
                    )
                    await asyncio.sleep(0.05)
            ok += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Broadcast {hs['ho_ten']}: {e}")

    admin_state["mode"] = "menu"
    admin_state["buoi_dang_gui"] = None
    await update.message.reply_text(
        f"✅ Đã gửi tài liệu Buổi {buoi} cho {ok}/{len(students)} học sinh",
        reply_markup=ADMIN_MENU,
    )


# Import BUOI_INFO từ bot chính
BUOI_INFO = {
    2:  {"ten": "Bài Toán Cấu Tạo Số"},
    3:  {"ten": "Viết Số Tự Nhiên Thỏa Mãn Điều Kiện"},
    4:  {"ten": "Dãy Số Cách Đều"},
    5:  {"ten": "Biểu Thức Số"},
    6:  {"ten": "Tính Tổng Dãy Số Ghép Cặp"},
    7:  {"ten": "Tính Tổng Dãy Số Ghép Cặp (Tiếp)"},
    8:  {"ten": "Ôn Tập Dãy Số + Dãy Hình Quy Luật"},
    27: {"ten": "Các Bài Toán Về Thời Gian"},
}


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)


def main():
    if not ADMIN_BOT_TOKEN: raise ValueError("Thiếu ADMIN_BOT_TOKEN")
    db.init_db()

    # Seed lessons vào DB
    for so_buoi, info in BUOI_INFO.items():
        db.upsert_lesson(so_buoi, info["ten"])

    app = Application.builder().token(ADMIN_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(MessageHandler(filters.TEXT  & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_error_handler(error_handler)

    logger.info("VInaStudy Admin Bot dang chay...")
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()
