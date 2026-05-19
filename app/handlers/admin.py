import logging
import asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Bot
from telegram.ext import ContextTypes

import app.database.crud as crud
from app.config import BUOI_CONFIG, ADMIN_ID, TELEGRAM_TOKEN

logger = logging.getLogger(__name__)

ADMIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("📤 Gửi tài liệu buổi học"), KeyboardButton("📊 Thống kê lớp")],
    [KeyboardButton("⚠️ Nhắc học sinh nộp bài"), KeyboardButton("👥 Danh sách học sinh")],
    [KeyboardButton("➕ Thêm học sinh"),          KeyboardButton("📋 Báo cáo phụ huynh")],
], resize_keyboard=True)

admin_state = {"mode": "menu", "buoi_dang_gui": None}

def is_admin(uid): return uid == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bạn không có quyền truy cập bot này.")
        return
    await update.message.reply_text("👨‍🏫 Chào thầy Long!\n\nBot quản lý VInaStudy sẵn sàng.", reply_markup=ADMIN_MENU)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = (update.message.text or "").strip()

    if text == "📤 Gửi tài liệu buổi học":
        admin_state["mode"] = "chon_buoi_gui"
        buoi_list = "\n".join([f"  {k}. Buổi {k} — {v['ten']}" for k,v in sorted(BUOI_CONFIG.items())])
        await update.message.reply_text(f"📤 Gửi tài liệu buổi nào?\n\n{buoi_list}\n\nNhập số buổi:")
        return

    if admin_state["mode"] == "chon_buoi_gui" and text.isdigit():
        so_buoi = int(text)
        if so_buoi in BUOI_CONFIG:
            admin_state["mode"] = "gui_tai_lieu"
            admin_state["buoi_dang_gui"] = so_buoi
            await update.message.reply_text(f"📤 Gửi tài liệu Buổi {so_buoi} — {BUOI_CONFIG[so_buoi]['ten']}\n\nGửi lần lượt:\n1. Ảnh chụp bảng (có thể nhiều ảnh)\n2. Link YouTube (nếu có)\n3. Link Zoom buổi tiếp theo (nếu có)\n\nKhi xong nhấn /broadcast để gửi cho học sinh.")
        return

    if admin_state["mode"] == "gui_tai_lieu" and text.startswith("http"):
        buoi = admin_state["buoi_dang_gui"]
        if "youtube" in text or "youtu.be" in text:
            lesson = await crud.get_lesson(buoi)
            if lesson:
                await crud.upsert_lesson(buoi, BUOI_CONFIG[buoi]["ten"], video_url=text)
                await crud.add_material(lesson["id"], "video", text)
            await update.message.reply_text(f"✅ Đã lưu link YouTube Buổi {buoi}")
        elif "zoom" in text:
            lesson = await crud.get_lesson(buoi)
            if lesson:
                await crud.upsert_lesson(buoi, BUOI_CONFIG[buoi]["ten"], zoom_link=text)
            await update.message.reply_text(f"✅ Đã lưu link Zoom")
        return

    if text == "📊 Thống kê lớp":
        admin_state["mode"] = "chon_buoi_stats"
        await update.message.reply_text("📊 Xem thống kê buổi nào? Nhập số buổi:")
        return

    if admin_state["mode"] == "chon_buoi_stats" and text.isdigit():
        so_buoi = int(text)
        stats = await crud.get_stats_lesson(so_buoi)
        chua = await crud.get_chua_lam(so_buoi)
        chua_text = "\n".join([f"  • {hs['ho_ten']}" for hs in chua]) or "  (Tất cả đã làm ✅)"

        await update.message.reply_text(
            f"📊 Thống kê Buổi {so_buoi}\n\n👥 Đã làm: {stats.get('so_da_lam', 0)}/{stats.get('tong_hs', 0)} học sinh\n📈 Điểm TB: {stats.get('diem_tb') or 0}%\n🏆 Giỏi (≥80%): {stats.get('gioi', 0)}\n⭐ Khá (60-80%): {stats.get('kha', 0)}\n📖 Cần cố gắng: {stats.get('can_co_gang', 0)}\n\n⚠️ Chưa làm ({len(chua)} em):\n{chua_text}",
            reply_markup=ADMIN_MENU,
        )
        admin_state["mode"] = "menu"
        return

    if text == "⚠️ Nhắc học sinh nộp bài":
        admin_state["mode"] = "nhac_buoi"
        await update.message.reply_text("⚠️ Nhắc bài buổi nào? Nhập số buổi:")
        return

    if admin_state["mode"] == "nhac_buoi" and text.isdigit():
        so_buoi = int(text)
        chua = await crud.get_chua_lam(so_buoi)
        if not chua:
            await update.message.reply_text("✅ Tất cả đã làm bài rồi!", reply_markup=ADMIN_MENU)
            admin_state["mode"] = "menu"
            return

        hs_bot = Bot(token=TELEGRAM_TOKEN)
        ok = 0
        for hs in chua:
            try:
                await hs_bot.send_message(
                    chat_id=hs["telegram_id"],
                    text=f"⏰ Nhắc bài!\n\nEm *{hs['ho_ten']}* chưa làm bài tập Buổi {so_buoi}.\nVào bot làm bài ngay nhé! 👇\nNhấn *🏠 Bài tập về nhà* → Buổi {so_buoi}",
                    parse_mode="Markdown",
                )
                ok += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Nhắc {hs['ho_ten']} lỗi: {e}")

        await update.message.reply_text(f"✅ Đã nhắc {ok}/{len(chua)} học sinh chưa làm Buổi {so_buoi}", reply_markup=ADMIN_MENU)
        admin_state["mode"] = "menu"
        return

    if text == "👥 Danh sách học sinh":
        students = await crud.get_all_students()
        if not students:
            await update.message.reply_text("Chưa có học sinh nào.", reply_markup=ADMIN_MENU)
            return
        lines = [f"{i+1}. {s['ho_ten']} (Lớp {s['lop']})" for i,s in enumerate(students)]
        await update.message.reply_text(f"👥 Danh sách học sinh ({len(students)} em):\n\n" + "\n".join(lines), reply_markup=ADMIN_MENU)
        return

    if text == "➕ Thêm học sinh":
        admin_state["mode"] = "them_hs"
        await update.message.reply_text("➕ Thêm học sinh mới\n\nNhập theo định dạng:\n`TelegramID | Họ tên | Lớp`\n\nVí dụ: `123456789 | Nguyễn Văn An | 3`", parse_mode="Markdown")
        return

    if admin_state["mode"] == "them_hs" and "|" in text:
        parts = [p.strip() for p in text.split("|")]
        if len(parts) >= 2:
            try:
                tid = int(parts[0])
                hoten = parts[1]
                lop = parts[2] if len(parts) > 2 else "3"
                hs = await crud.add_student(tid, hoten, lop)
                await update.message.reply_text(f"✅ Đã thêm: *{hs['ho_ten']}* (Lớp {hs['lop']})\nTelegram ID: `{tid}`", parse_mode="Markdown", reply_markup=ADMIN_MENU)
            except Exception as e:
                await update.message.reply_text(f"❌ Lỗi: {e}")
        admin_state["mode"] = "menu"
        return

    if text == "📋 Báo cáo phụ huynh":
        students = await crud.get_all_students()
        hs_bot = Bot(token=TELEGRAM_TOKEN)
        gui_ok = 0
        thang = datetime.now().strftime("%m/%Y")

        for hs in students:
            if not hs.get("telegram_ph"): continue
            results = await crud.get_results_student(hs["telegram_id"], limit=20)
            if not results: continue

            tb = round(sum(r["phan_tram"] for r in results) / len(results))
            lvl = "🏆 Giỏi" if tb>=80 else ("⭐ Khá" if tb>=60 else ("📖 Trung bình" if tb>=40 else "🌱 Cần cố gắng"))

            try:
                await hs_bot.send_message(
                    chat_id=hs["telegram_ph"],
                    text=f"📊 *Báo cáo tháng {thang}*\nHọc sinh: *{hs['ho_ten']}*\n\n📝 Số bài đã làm: {len(results)}\n📈 Điểm TB: {tb}%\n🎯 Xếp loại: {lvl}\n\n_VInaStudy — Thầy Nguyễn Thành Long_",
                    parse_mode="Markdown",
                )
                gui_ok += 1
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"Báo cáo PH {hs['ho_ten']}: {e}")

        await update.message.reply_text(f"✅ Đã gửi báo cáo cho {gui_ok} phụ huynh", reply_markup=ADMIN_MENU)
        return

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if admin_state["mode"] != "gui_tai_lieu":
        await update.message.reply_text("Nhập số buổi trước nhé! Nhấn '📤 Gửi tài liệu buổi học'")
        return

    buoi = admin_state["buoi_dang_gui"]
    lesson = await crud.get_lesson(buoi)
    if lesson:
        file_id = update.message.photo[-1].file_id
        await crud.add_material(lesson["id"], "anh_bang", file_id)
        await update.message.reply_text(f"✅ Đã lưu ảnh bảng Buổi {buoi}\nGửi thêm ảnh khác hoặc /broadcast để phát cho học sinh.")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    buoi = admin_state.get("buoi_dang_gui")
    if not buoi:
        await update.message.reply_text("Chưa chọn buổi nào!")
        return

    students = await crud.get_all_students()
    materials = await crud.get_materials(buoi)
    lesson = await crud.get_lesson(buoi)
    hs_bot = Bot(token=TELEGRAM_TOKEN)
    ok = 0

    ten = BUOI_CONFIG.get(buoi, {}).get("ten", f"Buổi {buoi}")
    video = lesson.get("video_url", "") if lesson else ""

    for hs in students:
        try:
            await hs_bot.send_message(
                chat_id=hs["telegram_id"],
                text=f"📚 *Tài liệu Buổi {buoi} — {ten}*\n\n{'📹 Video: ' + video if video else '📹 Video sẽ có sớm!'}\n\n📝 Nhớ làm bài tập về nhà nhé!\nNhấn *🏠 Bài tập về nhà* → Buổi {buoi}",
                parse_mode="Markdown",
            )
            for mat in materials:
                if mat["loai"] == "anh_bang":
                    await hs_bot.send_photo(chat_id=hs["telegram_id"], photo=mat["url"], caption=f"📸 Ảnh bảng Buổi {buoi}")
                    await asyncio.sleep(0.05)
            ok += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Broadcast {hs['ho_ten']}: {e}")

    admin_state["mode"] = "menu"
    admin_state["buoi_dang_gui"] = None
    await update.message.reply_text(f"✅ Đã gửi tài liệu Buổi {buoi} cho {ok}/{len(students)} học sinh", reply_markup=ADMIN_MENU)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)
