import logging
import json
import base64
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes, CallbackQueryHandler

import app.database.crud as crud
from app.config import BASE_URL, BASE_DOMAIN, BUOI_CONFIG, BTVN_CONFIG, DEFAULT_BUOI, ADMIN_ID
from app.services.ai_claude import ask_claude, ask_claude_with_image, danh_gia_nang_luc
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
    """Gửi màn hình yêu cầu đăng ký web."""
    uid = update.effective_user.id
    first_name = update.effective_user.first_name or "Chiến Binh"
    reg_url = f"{BASE_DOMAIN}/register?tg_id={uid}"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("⚔️ Đăng ký tài khoản", url=reg_url)
    ]])
    await update.message.reply_text(
        f"👋 Chào *{first_name}*!\n\n"
        "🔐 Em cần *đăng ký tài khoản* trước khi tham gia Chiến Binh Toán!\n\n"
        "📋 *Các bước:*\n"
        "1️⃣ Nhấn nút bên dưới → đăng nhập Gmail\n"
        "2️⃣ Chọn nhân vật & chụp ảnh đại diện\n"
        "3️⃣ Chờ thầy duyệt *(thường trong 24h)*\n"
        "4️⃣ Bot tự thông báo khi được duyệt ✅\n\n"
        "👇 Nhấn để bắt đầu hành trình!",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def send_pending(update: Update):
    """Gửi thông báo đang chờ duyệt."""
    first_name = update.effective_user.first_name or "Chiến Binh"
    await update.message.reply_text(
        f"⏳ Chào *{first_name}*!\n\n"
        "Hồ sơ của em đang *chờ thầy duyệt* ⚙️\n\n"
        "Thầy sẽ thông báo qua đây ngay khi duyệt xong!\n"
        "Thường trong vòng *24 giờ* 🚀",
        parse_mode="Markdown",
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

def make_main_menu() -> ReplyKeyboardMarkup:
    # Dùng BASE_DOMAIN (web server mới) thay vì BASE_URL cũ
    webapp_url = f"{BASE_DOMAIN}/game"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🗺️ Bản đồ Chiến Dịch", web_app=WebAppInfo(url=webapp_url)), KeyboardButton("🔮 Đánh giá Năng lực")],
            [KeyboardButton("📊 Bảng điểm"), KeyboardButton("📹 Xem bí kíp (Video)")],
            [KeyboardButton("💬 Hỏi Chỉ Huy"), KeyboardButton("📚 Chọn Căn cứ (Buổi)")],
            [KeyboardButton("🏅 Hồ sơ Chiến Binh"), KeyboardButton("🏆 Xếp hạng Bang hội")],
            [KeyboardButton("📅 Lịch học"), KeyboardButton("🗑️ Xoá lịch sử")],
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

async def dangky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect sang web registration thay vì đăng ký cũ."""
    uid = update.effective_user.id
    status = await check_web_status(uid)
    if status == "approved":
        await update.message.reply_text(
            "✅ Em đã có tài khoản và được duyệt rồi!\n\nChọn chức năng bên dưới để bắt đầu nhé! 👇",
            reply_markup=MAIN_MENU,
        )
    elif status == "pending":
        await send_pending(update)
    else:
        await send_login_required(update)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    clear_history(uid)

    # Admin bypass
    if is_admin(uid):
        await update.message.reply_text(
            f"👑 Chào *Thầy*! Menu quản lý đang chạy trên bot admin.\n\n"
            "Đây là bot học sinh — dùng để test giao diện.",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
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
            f"⚔️ Chào mừng *{ten}* trở lại!\n\n"
            "🎓 Học viện Toán *VInaStudy* — Tổng Chỉ huy: Nguyễn Thành Long\n\n"
            "Hãy chọn hành động bên dưới để bắt đầu! 👇",
            parse_mode="Markdown", reply_markup=MAIN_MENU,
        )
    elif status == "pending":
        await send_pending(update)
    else:
        await send_login_required(update)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = (update.message.text or "").strip()

    # ── Login gate (admin bypass) ────────────────────────────────────────
    if not is_admin(uid):
        status = await check_web_status(uid)
        if status in ("not_found", "rejected"):
            await send_login_required(update)
            return
        if status == "pending":
            await send_pending(update)
            return
    # ───────────────────────────────────────────────────────────────────

    state = get_state(uid)

    if text == "🗺️ Bản đồ Chiến Dịch":
        state["mode"] = "btvn_menu"
        await update.message.reply_text("🏠 *Bản đồ Chiến Dịch*\n\nChọn ải để tiêu diệt quái vật.\n_(Ải mới nhất ở dưới cùng)_ 👇", parse_mode="Markdown", reply_markup=BTVN_MENU)
        return

    if text.startswith("📖 Buổi "):
        try:
            so_buoi = int(text.split("Buổi ")[1].split(" —")[0])
        except Exception:
            so_buoi = None

        if so_buoi and so_buoi in BTVN_CONFIG:
            state["buoi"] = so_buoi
            state["mode"] = "btvn_chat"
            state["history"] = []

            cfg = BTVN_CONFIG[so_buoi]
            ten = BUOI_CONFIG[so_buoi]["ten"]
            webapp_url = f"{BASE_DOMAIN}/content/lop3/{cfg.get('folder','')}/bai-tap.html" if cfg.get('folder') else f"{BASE_URL}/{cfg['html']}"

            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text=f"📝 Làm bài — Buổi {so_buoi}", web_app=WebAppInfo(url=webapp_url))]])
            await update.message.reply_text(f"🏠 *Bài tập về nhà — Buổi {so_buoi}*\n_{ten}_\n\n📋 {cfg['so_cau']} câu bài tập\n📹 Video: {BUOI_CONFIG[so_buoi]['video']}\n\n👇 Nhấn nút bên dưới để làm bài:", parse_mode="Markdown", reply_markup=keyboard)
            await update.message.reply_text("💬 Hoặc nhập câu hỏi nếu cần thầy hướng dẫn!", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📝 Làm bài tập")], [KeyboardButton("🔙 Về menu chính")]], resize_keyboard=True))
        else:
            await update.message.reply_text("Buổi này chưa có bài tập.", reply_markup=BTVN_MENU)
        return

    if text == "🔮 Đánh giá Năng lực":
        try:
            db_results = await crud.get_results_student(uid, limit=8)
            if db_results:
                lines = ["📊 *Tổng kết năng lực của em:*\n"]
                for r in db_results:
                    pct = r["phan_tram"]
                    bar = "🟢" if pct >= 80 else ("🟡" if pct >= 60 else ("🟠" if pct >= 40 else "🔴"))
                    ten_buoi = r.get("ten_buoi", f"Buổi {r.get('so_buoi', '?')}")
                    tg = r["thoi_gian"]
                    tg_str = tg.strftime("%d/%m") if hasattr(tg, "strftime") else str(tg)[:10]
                    lines.append(f"{bar} {ten_buoi}: *{r['diem']}/{r['tong_cau']}* ({pct}%) — {tg_str}")
                msg = "\n".join(lines)
            else:
                raise ValueError("no db data")
        except Exception:
            uid_ls = lich_su_hs(uid)
            if not uid_ls:
                msg = "📊 Em chưa làm bài tập nào. Hãy làm *🗺️ Bản đồ Chiến Dịch* trước nhé!"
            else:
                lines = ["📊 *Tổng kết năng lực của em:*\n"]
                for ls in reversed(uid_ls[-8:]):
                    bar = "🟢" if ls["phan_tram"] >= 80 else ("🟡" if ls["phan_tram"] >= 60 else ("🟠" if ls["phan_tram"] >= 40 else "🔴"))
                    lines.append(f"{bar} Buổi {ls['buoi']}: *{ls['diem']}/{ls['tong']}* ({ls['phan_tram']}%) — {ls['thoi_gian']}")
                msg = "\n".join(lines)
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    if text == "📊 Bảng điểm":
        try:
            db_results = await crud.get_results_student(uid, limit=15)
            if db_results:
                lines = ["📋 *Lịch sử bài làm của em:*\n"]
                for i, r in enumerate(db_results, 1):
                    pct = r["phan_tram"]
                    lvl = "🏆" if pct >= 80 else ("⭐" if pct >= 60 else ("📖" if pct >= 40 else "🌱"))
                    ten_buoi = r.get("ten_buoi", f"Buổi {r.get('so_buoi', '?')}")
                    tg = r["thoi_gian"]
                    tg_str = tg.strftime("%d/%m/%Y %H:%M") if hasattr(tg, "strftime") else str(tg)[:16]
                    lines.append(f"{i}. {lvl} {ten_buoi}: *{r['diem']}/{r['tong_cau']}* ({pct}%)\n   📅 {tg_str}")
                msg = "\n".join(lines)
            else:
                raise ValueError("no db data")
        except Exception:
            uid_ls = lich_su_hs(uid)
            if not uid_ls:
                msg = "📋 Em chưa có kết quả nào. Hãy làm bài tập trước nhé!"
            else:
                lines = ["📋 *Lịch sử bài làm của em:*\n"]
                for i, ls in enumerate(reversed(uid_ls), 1):
                    pct = ls["phan_tram"]
                    lvl = "🏆" if pct >= 80 else ("⭐" if pct >= 60 else ("📖" if pct >= 40 else "🌱"))
                    lines.append(f"{i}. {lvl} Buổi {ls['buoi']} — {ls['diem']}/{ls['tong']} ({pct}%)\n   📅 {ls['thoi_gian']}")
                msg = "\n".join(lines)
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    if text == "📹 Xem bí kíp (Video)":
        buoi = state.get("buoi", DEFAULT_BUOI)
        cfg = BUOI_CONFIG[buoi]
        await update.message.reply_text(f"📹 *Video — Buổi {buoi}*\n_{cfg['ten']}_\n\n🔗 {cfg['video']}", parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    if text == "💬 Hỏi Chỉ Huy":
        state["mode"] = "chat"
        buoi = state.get("buoi", DEFAULT_BUOI)
        await update.message.reply_text(f"💬 *Hỏi bài — Buổi {buoi}: {BUOI_CONFIG[buoi]['ten']}*\n\nGõ bài toán cần giải, thầy Long AI sẽ hướng dẫn từng bước! 👇", parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    if text == "📚 Chọn Căn cứ (Buổi)":
        state["mode"] = "chon_buoi"
        await update.message.reply_text("📚 *Chọn buổi học*", parse_mode="Markdown", reply_markup=BUOI_MENU)
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
            await update.message.reply_text(f"✅ Đã chuyển sang *Buổi {so_buoi}: {BUOI_CONFIG[so_buoi]['ten']}*", parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    if text == "📅 Lịch học":
        lines = ["📅 *Lịch học VInaStudy — Lớp 3*\n"]
        for so_buoi, cfg in sorted(BUOI_CONFIG.items()):
            lines.append(f"📘 Buổi {so_buoi}: *{cfg['ten']}*\n   📹 {cfg['video']}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    if text == "🗑️ Xoá lịch sử":
        clear_history(uid)
        await update.message.reply_text("🗑️ Đã xoá lịch sử hội thoại!", reply_markup=MAIN_MENU)
        return

    if text == "🔙 Về menu chính":
        state["mode"] = "menu"
        await update.message.reply_text("🏠 Menu chính!", reply_markup=MAIN_MENU)
        return

    if text == "🏅 Hồ sơ Chiến Binh":
        profile_url = f"{BASE_DOMAIN}/profile?tg_id={uid}"
        # Lấy thống kê game + thông tin nhân vật
        try:
            web_user = await crud.get_web_user_by_telegram_id(uid)
            hs = await crud.get_student(uid)
            ho_ten = (web_user or {}).get("ho_ten") or (hs or {}).get("ho_ten") or update.effective_user.first_name
            char = (web_user or {}).get("character_type", "chien_binh")
            char_names = {"chien_binh":"⚔️ Chiến Binh","phu_thuy":"🔮 Phù Thủy","xa_thu":"🏹 Xạ Thủ","hiep_si":"🛡️ Hiệp Sĩ"}
            has_avatar = bool((web_user or {}).get("avatar_final"))
            avatar_hint = "" if has_avatar else "\n\n📷 _Em chưa có avatar — nhấn nút để tạo ngay!_"
            profile_text = await hien_thi_profile(uid, ho_ten)
            msg = f"{profile_text}\n\n🎭 Nhân vật: *{char_names.get(char, char)}*{avatar_hint}"
        except Exception:
            msg = "🏅 *Hồ sơ Chiến Binh*\n\nNhấn nút bên dưới để xem và chỉnh sửa!"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✏️ Chỉnh sửa hồ sơ & Avatar", url=profile_url)
        ]])
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboard)
        return

    if text == "🏆 Xếp hạng Bang hội":
        lb_url = f"{BASE_DOMAIN}/leaderboard"
        await update.message.reply_text(
            f"🏆 *Bảng Xếp Hạng Chiến Binh*\n\n"
            f"🌐 Xem bảng xếp hạng đẹp tại:\n{lb_url}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏆 Mở Bảng Xếp Hạng", url=lb_url)
            ]]))
        xh = await bang_xep_hang(top_n=10)
        await update.message.reply_text(xh, parse_mode="Markdown", reply_markup=MAIN_MENU)
        return

    if state["mode"] in ("chat", "btvn_chat"):
        await update.message.chat.send_action("typing")
        reply = await ask_claude(state["history"], text, state.get("buoi", DEFAULT_BUOI))
        await update.message.reply_text(reply, reply_markup=MAIN_MENU)
        return

    await update.message.reply_text("Chọn chức năng trong menu nhé! Hoặc bấm *💬 Hỏi bài* để hỏi bài toán.", parse_mode="Markdown", reply_markup=MAIN_MENU)


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
    except Exception as e:
        logger.error(f"Web app data error: {e}")
        await update.message.reply_text("❌ Lỗi nhận kết quả, em thử lại nhé!", reply_markup=MAIN_MENU)
        return

    phan_tram = round(diem / tong * 100) if tong else 0
    luu_ket_qua(uid, buoi, diem, tong, chi_tiet)
    try:
        await crud.save_result(uid, buoi, diem, tong, chi_tiet)
        if checkpoints:
            await crud.save_session_with_checkpoints(uid, buoi, checkpoints)
    except Exception as e:
        logger.warning(f"DB save result: {e}")

    await update.message.reply_text(f"✅ *Hoàn thành Chiến dịch — Ải {buoi}*\n\n📊 Đã tiêu diệt: *{diem}/{tong}* quái vật ({phan_tram}%)\n\n⏳ Đang thu thập chiến lợi phẩm...", parse_mode="Markdown")

    lich_su = lich_su_hs(uid)
    tong_buoi = len(set(r["buoi"] for r in lich_su))
    try:
        game_result = await cap_nhat_gamification(uid, buoi, diem, tong, lich_su[:-1], tong_buoi)
        game_msg = thong_bao_ket_qua_game(game_result, update.effective_user.first_name)
        await update.message.reply_text(f"🎮 *Điểm thưởng*\n\n{game_msg}", parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Gamification error: {e}")

    await update.message.chat.send_action("typing")
    danh_gia = await danh_gia_nang_luc(diem, tong, chi_tiet, buoi, lich_su[:-1])
    await update.message.reply_text(f"🎓 *Đánh giá năng lực*\n\n{danh_gia}\n\n📹 Xem lại: {BUOI_CONFIG.get(buoi, {}).get('video', '')}", parse_mode="Markdown", reply_markup=MAIN_MENU)

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
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_MENU)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)
