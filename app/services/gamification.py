import json
from datetime import datetime, date
import app.database.crud as crud

BADGES = {
    "chao_mung":      {"icon": "🎉", "ten": "Chào mừng",       "mo_ta": "Làm bài tập lần đầu tiên",                  "xp": 50},
    "nguoi_moi":      {"icon": "🔰", "ten": "Người mới",        "mo_ta": "Hoàn thành 1 buổi học",                     "xp": 50},
    "diem_tuyet_voi": {"icon": "💯", "ten": "Tuyệt vời!",       "mo_ta": "Đạt 100% một bài",                          "xp": 100},
    "gioi_toan":      {"icon": "🏆", "ten": "Giỏi toán",        "mo_ta": "Đạt ≥80% trong 3 bài liên tiếp",            "xp": 150},
    "kha_nang":       {"icon": "⭐", "ten": "Khá năng",          "mo_ta": "Đạt ≥60% trong 5 bài",                     "xp": 80},
    "streak_3":       {"icon": "🔥", "ten": "Bắt đầu bốc!",     "mo_ta": "Học 3 ngày liên tiếp",                      "xp": 100},
    "streak_7":       {"icon": "⚡", "ten": "Tuần học siêu!",    "mo_ta": "Học 7 ngày liên tiếp",                      "xp": 200},
    "streak_30":      {"icon": "🌟", "ten": "Học sinh xuất sắc", "mo_ta": "Học 30 ngày liên tiếp",                     "xp": 500},
    "hoan_thanh_5":   {"icon": "📚", "ten": "Ham học",           "mo_ta": "Hoàn thành 5 buổi học",                     "xp": 100},
    "hoan_thanh_10":  {"icon": "📖", "ten": "Chăm chỉ",          "mo_ta": "Hoàn thành 10 buổi học",                    "xp": 200},
    "hoan_thanh_all": {"icon": "🎓", "ten": "Chinh phục tất cả", "mo_ta": "Hoàn thành tất cả các buổi",                "xp": 500},
    "sieu_nhanh":     {"icon": "⚡", "ten": "Siêu nhanh",        "mo_ta": "Làm bài trong cùng 1 ngày sau khi học",     "xp": 80},
    "vuon_len":       {"icon": "📈", "ten": "Vươn lên",          "mo_ta": "Điểm tăng so với lần trước cùng buổi",      "xp": 80},
    "khong_bo_cuoc":  {"icon": "💪", "ten": "Không bỏ cuộc",     "mo_ta": "Làm lại bài sau khi điểm thấp",             "xp": 100},
}

LEVELS = [
    (0,    "🌱", "Học sinh mới"),
    (200,  "📗", "Học sinh tiến bộ"),
    (500,  "📘", "Học sinh khá"),
    (1000, "📙", "Học sinh giỏi"),
    (2000, "🏅", "Học sinh xuất sắc"),
    (3500, "🥇", "Nhà toán học nhỏ"),
    (5000, "👑", "Thiên tài toán học"),
]

def tinh_cap_do(xp: int) -> tuple:
    cap = LEVELS[0]
    for threshold, icon, name in LEVELS:
        if xp >= threshold:
            cap = (threshold, icon, name)
    idx = LEVELS.index(cap)
    if idx + 1 < len(LEVELS):
        next_xp = LEVELS[idx + 1][0]
    else:
        next_xp = None
    return cap[1], cap[2], next_xp

async def cap_nhat_gamification(telegram_id: int, buoi: int, diem: int, tong: int, lich_su: list, tong_buoi_hoan_thanh: int) -> dict:
    g = await crud.get_gamification(telegram_id)
    if not g:
        g = {"xp": 0, "streak": 0, "streak_max": 0, "last_active": None, "badges": "[]"}
    
    if isinstance(g["badges"], str):
        try:
            badges = json.loads(g["badges"])
        except:
            badges = []
    else:
        badges = g["badges"]
        
    phan_tram = round(diem / tong * 100) if tong else 0
    today = date.today().isoformat()

    xp_bai = _tinh_xp(phan_tram, tong)

    streak_truoc = g["streak"]
    last = g.get("last_active")
    if last:
        last_date = date.fromisoformat(last)
        today_date = date.fromisoformat(today)
        delta = (today_date - last_date).days
        if delta == 1:
            g["streak"] += 1
        elif delta > 1:
            g["streak"] = 1
    else:
        g["streak"] = 1
        
    g["streak_max"] = max(g["streak_max"], g["streak"])
    g["last_active"] = today

    g["xp"] += xp_bai

    huy_hieu_moi = _kiem_tra_badges(g, badges, lich_su, phan_tram, tong_buoi_hoan_thanh, buoi)
    for badge_key in huy_hieu_moi:
        if badge_key not in badges:
            badges.append(badge_key)
            g["xp"] += BADGES[badge_key]["xp"]

    await crud.save_gamification(telegram_id, g["xp"], g["streak"], g["streak_max"], g["last_active"], json.dumps(badges))

    icon_cap, ten_cap, next_xp = tinh_cap_do(g["xp"])

    return {
        "xp_bai":      xp_bai,
        "xp_tong":     g["xp"],
        "streak":      g["streak"],
        "streak_tang": g["streak"] > streak_truoc,
        "badges_moi":  huy_hieu_moi,
        "icon_cap":    icon_cap,
        "ten_cap":     ten_cap,
        "next_xp":     next_xp,
    }

def _tinh_xp(phan_tram: int, tong_cau: int) -> int:
    base = 20
    if phan_tram == 100: he_so = 3.0
    elif phan_tram >= 80: he_so = 2.0
    elif phan_tram >= 60: he_so = 1.5
    elif phan_tram >= 40: he_so = 1.0
    else:                 he_so = 0.5
    bonus = max(0, (tong_cau - 5) * 2)
    return round(base * he_so + bonus)

def _kiem_tra_badges(g: dict, badges: list, lich_su: list, phan_tram: int, tong_buoi: int, buoi: int) -> list:
    moi = []
    earned = set(badges)

    def check(key):
        if key not in earned:
            moi.append(key)

    if not lich_su:                              check("chao_mung")
    if tong_buoi >= 1:                           check("nguoi_moi")
    if phan_tram == 100:                         check("diem_tuyet_voi")

    recent = [r for r in lich_su[-3:]] if len(lich_su) >= 2 else []
    if len(recent) >= 2 and all(r["phan_tram"] >= 80 for r in recent) and phan_tram >= 80:
        check("gioi_toan")

    recent5 = [r for r in lich_su[-5:]]
    if len(recent5) >= 4 and all(r["phan_tram"] >= 60 for r in recent5) and phan_tram >= 60:
        check("kha_nang")

    if g["streak"] >= 3:                         check("streak_3")
    if g["streak"] >= 7:                         check("streak_7")
    if g["streak"] >= 30:                        check("streak_30")

    if tong_buoi >= 5:                           check("hoan_thanh_5")
    if tong_buoi >= 10:                          check("hoan_thanh_10")
    if tong_buoi >= len(LEVELS):                 check("hoan_thanh_all")

    lich_su_buoi = [r for r in lich_su if r.get("buoi") == buoi]
    if lich_su_buoi and phan_tram > lich_su_buoi[-1]["phan_tram"]:
        check("vuon_len")

    if lich_su_buoi and lich_su_buoi[-1]["phan_tram"] < 40 and phan_tram >= 40:
        check("khong_bo_cuoc")

    return moi

async def hien_thi_profile(telegram_id: int, ho_ten: str) -> str:
    g = await crud.get_gamification(telegram_id)
    if not g:
        g = {"xp": 0, "streak": 0, "streak_max": 0, "last_active": None, "badges": "[]"}
    
    if isinstance(g["badges"], str):
        try:
            badges = json.loads(g["badges"])
        except:
            badges = []
    else:
        badges = g["badges"]
        
    icon_cap, ten_cap, next_xp = tinh_cap_do(g["xp"])

    if next_xp:
        prev_xp = 0
        for threshold, _, _ in LEVELS:
            if threshold <= g["xp"]:
                prev_xp = threshold
        progress = g["xp"] - prev_xp
        needed = next_xp - prev_xp
        bars = round(progress / needed * 10) if needed else 10
        bar = "█" * bars + "░" * (10 - bars)
        xp_line = f"`{bar}` {g['xp']}/{next_xp} XP"
    else:
        xp_line = f"✨ {g['xp']} XP — Cấp tối đa!"

    streak_line = f"🔥 Streak: *{g['streak']} ngày* (kỷ lục: {g['streak_max']} ngày)"

    if badges:
        badge_icons = " ".join(BADGES[b]["icon"] for b in badges if b in BADGES)
        badge_line = f"🎖 Huy hiệu ({len(badges)}): {badge_icons}"
    else:
        badge_line = "🎖 Huy hiệu: Chưa có — làm bài để nhận nhé!"

    return (
        f"👤 *{ho_ten}*\n"
        f"{icon_cap} Cấp độ: *{ten_cap}*\n\n"
        f"✨ XP: {xp_line}\n"
        f"{streak_line}\n"
        f"{badge_line}"
    )

def thong_bao_ket_qua_game(result: dict, ho_ten: str) -> str:
    lines = []
    lines.append(f"✨ *+{result['xp_bai']} XP* — Tổng: {result['xp_tong']} XP")
    lines.append(f"{result['icon_cap']} Cấp độ: *{result['ten_cap']}*")
    if result["next_xp"]:
        con_lai = result["next_xp"] - result["xp_tong"]
        lines.append(f"   _(Còn {con_lai} XP để lên cấp tiếp!)_")

    if result["streak_tang"]:
        lines.append(f"\n🔥 Streak tăng lên *{result['streak']} ngày* liên tiếp!")
        if result["streak"] == 3:
            lines.append("   💪 Tuyệt vời! Em đang học rất đều!")
        elif result["streak"] == 7:
            lines.append("   🎉 Một tuần không nghỉ! Em thật xuất sắc!")
    else:
        lines.append(f"\n🔥 Streak hiện tại: *{result['streak']} ngày*")

    if result["badges_moi"]:
        lines.append("\n🎖 *Huy hiệu mới mở khóa!*")
        for key in result["badges_moi"]:
            if key in BADGES:
                b = BADGES[key]
                lines.append(f"   {b['icon']} *{b['ten']}* — {b['mo_ta']} (+{b['xp']} XP)")

    return "\n".join(lines)

async def bang_xep_hang(top_n: int = 10) -> str:
    try:
        rows = await crud.get_leaderboard(top_n)
    except Exception:
        return "❌ Chưa có dữ liệu bảng xếp hạng."

    if not rows:
        return "📊 Bảng xếp hạng còn trống — hãy là người đầu tiên!"

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 *Bảng Xếp Hạng VInaStudy*\n"]
    for i, row in enumerate(rows):
        icon_cap, _, _ = tinh_cap_do(row["xp"])
        medal = medals[i] if i < 3 else f"{i+1}."
        lines.append(
            f"{medal} {icon_cap} *{row['ho_ten']}*\n"
            f"   ✨ {row['xp']} XP  🔥 {row['streak']}🌙  🎖 {row['so_huy_hieu']} huy hiệu"
        )

    return "\n".join(lines)
