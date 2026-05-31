import logging
import json
import base64
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes, CallbackQueryHandler

import app.database.crud as crud
from app.config import BASE_URL, BASE_DOMAIN, BUOI_CONFIG, BTVN_CONFIG, DEFAULT_BUOI, ADMIN_ID
from app.services.ai_claude import ask_claude, ask_claude_support, ask_claude_with_image, danh_gia_nang_luc
from app.services.gamification import cap_nhat_gamification, hien_thi_profile, thong_bao_ket_qua_game, bang_xep_hang

logger = logging.getLogger(__name__)


# ── Login gate ────────────────────────────────────────────────────────────

def is_admin(uid: int) -> bool:
    """Admin (thầy) luôn bypass login gate."""
    return ADMIN_ID and uid == ADMIN_ID


async def check_web_status(telegram_id: int) -> str:
    """Kiểm tra trạng thái tài khoản web của học sinh.
    Returns: 'approved' | 'pending' | 'rejected' | 'not_found'
    """
    try:
        user = await crud.get_web_user_by_telegram_id(telegram_id)
        if not user:
            return "not_found"
        return user.get("status", "not_found")
    except Exception as e:
        logger.warning(f"check_web_status error: {e}")
        return "not_found"


async def send_login_required(update: Update):
    """Gửi inline button đăng ký khi user chưa có tài khoản."""
    uid = update.effective_user.id
    first_name = update.effective_user.first_name or "Chiến Binh"
    reg_url = f"{BASE_DOMAIN}/register?tg_id={uid}"
    await update.message.reply_text(
        f"👋 Chào *{first_name}*!\n\n"
        "Em chưa có tài khoản. Nhấn bên dưới để đăng ký và tham gia Chiến Binh Toán! 🚀",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📝 Tạo tài khoản", web_app=WebAppInfo(url=reg_url))
        ]]),
    )


async def send_pending(update: Update):
    """Gửi thông báo đang chờ duyệt."""
    uid = update.effective_user.id
    first_name = update.effective_user.first_name or "Chiến Binh"
    await update.message.reply_text(
        f"⏳ Chào *{first_name}*!\n\n"
        "Hồ sơ đang *chờ thầy duyệt* ⚙️\n"
        "Thầy sẽ thông báo ngay khi xong — thường trong *24 giờ* 🚀",
        parse_mode="Markdown",
        reply_markup=game_kb(),
    )


# ── State ─────────────────────────────────────────────────────────────────

# State
user_state: dict = {}
ket_qua_hs: dict = {}

def get_state(uid):
    if uid not in user_state:
        user_state[uid] = {"mode": "menu", "history": [], "buoi": DEFAULT_BUOI}
    return user_state[uid]

def clear_history(uid):
    buoi = user_state.get(uid, {}).get("buoi", DEFAULT_BUOI)
    user_state[uid] = {"mode": "menu", "history": [], "buoi": buoi}

def luu_ket_qua(user_id: int, buoi: int, diem: int, tong: int, chi_tiet: dict):
    if user_id not in ket_qua_hs:
        ket_qua_hs[user_id] = []
    ket_qua_hs[user_id].append({
        "buoi": buoi,
        "diem": diem,
        "tong": tong,
        "phan_tram": round(diem / tong * 100) if tong else 0,
        "chi_tiet": chi_tiet,
        "thoi_gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })

def lich_su_hs(user_id: int) -> list:
    return ket_qua_hs.get(user_id, [])

# ── Keyboard ──────────────────────────────────────────────────────────────

def game_kb() -> ReplyKeyboardMarkup:
    """Bàn phím thống nhất: 1 nút text → bot check status DB real-time khi nhận."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🎮 Chơi game")]],
        resize_keyboard=True,
    )


# ── Real-time status check khi ấn nút Chơi game ──────────────────────────

async def handle_game_press(update: Update, uid: int):
    """Check trạng thái tài khoản real-time, trả inline button phù hợp."""
    first_name = update.effective_user.first_name or "Chiến Binh"
    status = await check_web_status(uid)

    if status == "approved":
        game_url = f"{BASE_DOMAIN}/game?tg_id={uid}"
        await update.message.reply_text(
            f"✅ *{first_name}* — tài khoản đã được kích hoạt!\n"
            "Nhấn bên dưới để vào chiến đấu ⚔️",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 Vào game ngay!", web_app=WebAppInfo(url=game_url))
            ]]),
        )

    elif status == "pending":
        await update.message.reply_text(
            "⏳ Hồ sơ đang *chờ thầy duyệt* ⚙️\n"
            "Thầy sẽ thông báo ngay khi xong — thường trong *24 giờ* 🚀",
            parse_mode="Markdown",
            reply_markup=game_kb(),
        )

    else:  # not_found / rejected
        reg_url = f"{BASE_DOMAIN}/register?tg_id={uid}"
        await update.message.reply_text(
            f"👋 *{first_name}* chưa có tài khoản!\n"
            "Nhấn bên dưới để đăng ký và tham gia Chiến Binh Toán 🚀",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📝 Tạo tài khoản", web_app=WebAppInfo(url=reg_url))
            ]]),
        )

async def dangky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect sang web registration thay vì đăng ký cũ."""
    await handle_game_press(update, update.effective_user.id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    clear_history(uid)

    # Admin bypass
    if is_admin(uid):
        await update.message.reply_text(
            f"👑 Chào *Thầy*! Menu quản lý đang chạy trên bot admin.\n\n"
            "Đây là bot học sinh — dùng để test giao diện.",
            parse_mode="Markdown", reply_markup=game_kb(),
        )
        return

    status = await check_web_status(uid)

    if status == "approved":
        # Lấy tên từ web_user nếu có
        try:
            web_user = await crud.get_web_user_by_telegram_id(uid)
            ten = web_user["ho_ten"] if web_user and web_user.get("ho_ten") else update.effective_user.first_name
        except Exception:
            ten = update.effective_user.first_name

        await update.message.reply_text(
            f"⚔️ Chào *{ten}*! Sẵn sàng chiến đấu chưa? 💪\n\nNhấn *🎮 Chơi game* bên dưới để vào chiến đấu! 👇",
            parse_mode="Markdown", reply_markup=game_kb(),
        )
    elif status == "pending":
        await send_pending(update)
    else:
        await send_login_required(update)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = (update.message.text or "").strip()

    # ── Nút Chơi game: check DB real-time, TRƯỚC login gate ──────────────
    if text == "🎮 Chơi game":
        await handle_game_press(update, uid)
        return
    # ─────────────────────────────────────────────────────────────────────

    # ── Login gate (admin bypass) ─────────────────────────────────────────
    if not is_admin(uid):
        status = await check_web_status(uid)
        if status in ("not_found", "rejected"):
            await send_login_required(update)
            return
        if status == "pending":
            await send_pending(update)
            return
    # ─────────────────────────────────────────────────────────────────────

    state = get_state(uid)

    # Bot chỉ hỗ trợ các vấn đề liên quan game Chiến Binh Toán
    await update.message.chat.send_action("typing")
    reply = await ask_claude_support(state["history"], text)
    await update.message.reply_text(reply, reply_markup=game_kb())


async def xu_ly_ket_qua_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # WebApp data: không cần gate vì chỉ học sinh có link mới làm được bài
    state = get_state(uid)

    try:
        data = json.loads(update.message.web_app_data.data)
        buoi = data.get("buoi", state.get("buoi", DEFAULT_BUOI))
        diem = data.get("diem", 0)
        tong = data.get("tong", 0)
        chi_tiet = data.get("chi_tiet", {})
        checkpoints = data.get("checkpoints", [])
        try:
            level = int(data.get("level", 1))
        except (ValueError, TypeError):
            level = 1
    except Exception as e:
        logger.error(f"Web app data error: {e}")
        await update.message.reply_text("❌ Lỗi nhận kết quả, em thử lại nhé!", reply_markup=game_kb())
        return

    phan_tram = round(diem / tong * 100) if tong else 0
    luu_ket_qua(uid, buoi, diem, tong, chi_tiet)
    try:
        await crud.save_result(uid, buoi, diem, tong, chi_tiet, level=level)
        if checkpoints:
            await crud.save_session_with_checkpoints(uid, buoi, checkpoints)
    except Exception as e:
        logger.warning(f"DB save result: {e}")

    await update.message.reply_text(f"✅ *Hoàn thành Chiến dịch — Ải {buoi}*\n\n📊 Đã tiêu diệt: *{diem}/{tong}* quái vật ({phan_tram}%)\n\n⏳ Đang thu thập chiến lợi phẩm...", parse_mode="Markdown", reply_markup=game_kb())

    lich_su = lich_su_hs(uid)
    tong_buoi = len(set(r["buoi"] for r in lich_su))
    try:
        game_result = await cap_nhat_gamification(uid, buoi, diem, tong, lich_su[:-1], tong_buoi)
        game_msg = thong_bao_ket_qua_game(game_result, update.effective_user.first_name)
        await update.message.reply_text(f"🎮 *Điểm thưởng*\n\n{game_msg}", parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Gamification error: {e}")

    await update.message.chat.send_action("typing")
    danh_gia = await danh_gia_nang_luc(diem, tong, chi_tiet, buoi, lich_su[:-1],
                                        checkpoints=checkpoints, level=level)
    await update.message.reply_text(f"🎓 *Đánh giá năng lực*\n\n{danh_gia}\n\n📹 Xem lại: {BUOI_CONFIG.get(buoi, {}).get('video', '')}", parse_mode="Markdown", reply_markup=game_kb())

    # ── Kiểm tra thách đấu đang chờ ────────────────────────────────────
    try:
        challenge = await crud.get_pending_challenge(uid, buoi)
        if challenge:
            result = await crud.complete_challenge(challenge["id"], phan_tram)
            c_score = challenge["challenger_score"] or 0
            first_name = update.effective_user.first_name or "Chiến Binh"

            # Lấy tên challenger
            ch_info = await crud.get_student(challenge["challenger_id"])
            ch_name = (ch_info or {}).get("ho_ten", "Đối thủ")

            if result.get("winner_id") == uid:
                await update.message.reply_text(
                    f"⚔️ *Thách đấu hoàn thành!*\n\n"
                    f"🏆 *{first_name} THẮNG!* 🎉\n\n"
                    f"📊 {first_name}: *{phan_tram}%*\n"
                    f"📊 {ch_name}: *{c_score}%*",
                    parse_mode="Markdown")
                # Thông báo cho challenger
                try:
                    await context.bot.send_message(
                        challenge["challenger_id"],
                        f"⚔️ *Kết quả thách đấu — Buổi {buoi}*\n\n"
                        f"😅 *{first_name}* đã nhận thách đấu và thắng!\n"
                        f"📊 {first_name}: *{phan_tram}%*\n"
                        f"📊 Bạn: *{c_score}%*\n\n"
                        f"💪 Luyện tập thêm để lần sau thắng nhé!",
                        parse_mode="Markdown")
                except Exception: pass
            elif result.get("winner_id") == challenge["challenger_id"]:
                await update.message.reply_text(
                    f"⚔️ *Thách đấu hoàn thành!*\n\n"
                    f"😅 *{ch_name} thắng lần này!*\n\n"
                    f"📊 {first_name}: *{phan_tram}%*\n"
                    f"📊 {ch_name}: *{c_score}%*\n\n"
                    f"💪 Luyện tập thêm để rửa hận nhé!",
                    parse_mode="Markdown")
                try:
                    await context.bot.send_message(
                        challenge["challenger_id"],
                        f"⚔️ *{ch_name} THẮNG thách đấu — Buổi {buoi}!* 🏆\n\n"
                        f"📊 {first_name}: *{phan_tram}%*\n"
                        f"📊 Bạn: *{c_score}%*",
                        parse_mode="Markdown")
                except Exception: pass
            else:
                await update.message.reply_text(
                    f"⚔️ *Thách đấu kết thúc — Hòa!* 🤝\n\n"
                    f"Cả hai đều đạt *{phan_tram}%*!", parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Challenge check error: {e}")

    # ── Nút thách đấu bạn học ────────────────────────────────────────────
    try:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("⚔️ Thách đấu bạn học!", callback_data=f"ch_select_{buoi}_{phan_tram}")
        ]])
        await update.message.reply_text(
            "🏅 Muốn thách đấu bạn cùng buổi này không?",
            reply_markup=keyboard)
    except Exception as e:
        logger.warning(f"Challenge button error: {e}")


# ── Challenge callback handlers ───────────────────────────────────────────

async def handle_challenge_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý callback từ nút thách đấu."""
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data  # ch_select_<buoi>_<score> | ch_target_<target>_<buoi>_<score>

    if data.startswith("ch_select_"):
        # Hiển thị danh sách bạn học
        parts = data.split("_")
        buoi, score = int(parts[2]), int(parts[3])
        classmates = await crud.get_active_classmates(uid)
        if not classmates:
            await query.edit_message_text("😕 Chưa có bạn học nào trong hệ thống.")
            return
        btns = []
        for cm in classmates[:10]:
            xp_str = f" ({cm['xp']} XP)" if cm.get("xp") else ""
            btns.append([InlineKeyboardButton(
                f"⚔️ {cm['ho_ten']}{xp_str}",
                callback_data=f"ch_target_{cm['telegram_id']}_{buoi}_{score}"
            )])
        btns.append([InlineKeyboardButton("❌ Thôi", callback_data="ch_cancel")])
        await query.edit_message_text(
            f"⚔️ *Chọn người muốn thách đấu — Buổi {buoi}*\n_(Điểm của bạn: {score}%)_",
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode="Markdown")

    elif data.startswith("ch_target_"):
        parts = data.split("_")
        target_id, buoi, score = int(parts[2]), int(parts[3]), int(parts[4])
        challenger_name = query.from_user.first_name or "Ai đó"

        try:
            await crud.create_challenge(uid, target_id, buoi, score)
            target_info = await crud.get_student(target_id)
            target_name = (target_info or {}).get("ho_ten", "Bạn học")

            await query.edit_message_text(
                f"⚔️ *Đã gửi thách đấu đến {target_name}!*\n\n"
                f"📊 Điểm của bạn: *{score}%*\n"
                f"⏰ Bạn có *24 giờ* để nhận thách đấu.\n"
                f"🔔 Tự động thông báo khi có kết quả!",
                parse_mode="Markdown")

            # Notify target
            try:
                cfg = BUOI_CONFIG.get(buoi, {})
                btvn = BTVN_CONFIG.get(buoi)
                keyboard_target = None
                if btvn and cfg.get("folder"):
                    webapp_url = f"{BASE_DOMAIN}/content/lop3/{cfg['folder']}/bai-tap.html"
                    keyboard_target = InlineKeyboardMarkup([[
                        InlineKeyboardButton("⚔️ Nhận thách đấu!", web_app=WebAppInfo(url=webapp_url))
                    ]])
                await context.bot.send_message(
                    target_id,
                    f"⚔️ *{challenger_name} thách đấu bạn — Buổi {buoi}!*\n\n"
                    f"📖 _{cfg.get('ten', '')}_{chr(10)}"
                    f"📊 Điểm thách đấu: *{score}%*\n\n"
                    f"💪 Bạn có *24 giờ* để làm bài và chứng minh!",
                    parse_mode="Markdown",
                    reply_markup=keyboard_target)
            except Exception as e:
                logger.warning(f"Notify challenge target error: {e}")
                await context.bot.send_message(
                    uid,
                    f"⚠️ Rất tiếc, gửi thất bại! *{target_name}* hiện không thể nhận tin nhắn từ bot (có thể bạn ấy đã tắt bot).",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.warning(f"Create challenge error: {e}")
            await query.edit_message_text("❌ Lỗi tạo thách đấu, thử lại nhé!")

    elif data == "ch_cancel":
        await query.edit_message_text("👍 Không thách đấu lần này.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # ── Login gate (admin bypass) ────────────────────────────────────────
    if not is_admin(uid):
        status = await check_web_status(uid)
        if status == "pending":
            await send_pending(update)
            return
        if status != "approved":
            await send_login_required(update)
            return
    # ───────────────────────────────────────────────────────────────────

    state = get_state(uid)
    await update.message.chat.send_action("typing")
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        img_b64 = base64.standard_b64encode(file_bytes).decode("utf-8")
        caption = update.message.caption or ""
        user_text = f"Em gửi ảnh bài toán.{' Ghi chú: ' + caption if caption else ''}"
        
        reply = await ask_claude_with_image(state["history"], user_text, img_b64, state.get("buoi", DEFAULT_BUOI))
        await update.message.reply_text(reply, reply_markup=game_kb())
    except Exception as e:
        logger.error(f"Photo error: {e}")
        await update.message.reply_text("Chưa đọc được ảnh, em thử lại nhé!", reply_markup=game_kb())

async def xoa_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_history(update.effective_user.id)
    await update.message.reply_text("🗑️ Đã xoá lịch sử!", reply_markup=game_kb())

async def btvn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chuyển sang map.html để chọn bài tập."""
    await update.message.reply_text(
        "🗺️ Chọn bài tập trực tiếp trên *Bản đồ Chiến Dịch* nhé!\n\nNhấn *🎮 Chơi game* để vào map 👇",
        parse_mode="Markdown", reply_markup=game_kb(),
    )

async def chonbuoi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chuyển sang map.html để chọn buổi."""
    await update.message.reply_text(
        "🗺️ Chọn buổi học trực tiếp trên *Bản đồ Chiến Dịch* nhé!\n\nNhấn *🎮 Chơi game* để vào map 👇",
        parse_mode="Markdown", reply_markup=game_kb(),
    )

async def bangdiem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_ls = lich_su_hs(uid)
    if not uid_ls:
        msg = "📋 Em chưa có kết quả nào. Hãy làm bài tập trước nhé!"
    else:
        lines = ["📋 *Lịch sử bài làm:*\n"]
        for i, ls in enumerate(reversed(uid_ls), 1):
            lvl = "🏆" if ls["phan_tram"]>=80 else ("⭐" if ls["phan_tram"]>=60 else ("📖" if ls["phan_tram"]>=40 else "🌱"))
            lines.append(f"{i}. {lvl} Buổi {ls['buoi']} — {ls['diem']}/{ls['tong']} ({ls['phan_tram']}%) | {ls['thoi_gian']}")
        msg = "\n".join(lines)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=game_kb())

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)
