import json
import logging
from app.database.connection import get_pool

logger = logging.getLogger(__name__)

# ── Students ──────────────────────────────────────────────────────────

async def add_student(telegram_id: int, ho_ten: str, lop: str = "3", telegram_ph: int = None) -> dict:
    sql = """
        INSERT INTO students (telegram_id, ho_ten, lop, telegram_ph)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (telegram_id) DO UPDATE
            SET ho_ten = EXCLUDED.ho_ten,
                lop    = EXCLUDED.lop
        RETURNING *
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, telegram_id, ho_ten, lop, telegram_ph)
    return dict(row) if row else None

async def get_student(telegram_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM students WHERE telegram_id=$1", telegram_id)
    return dict(row) if row else None

async def get_all_students() -> list:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM students WHERE active=TRUE ORDER BY ho_ten")
    return [dict(r) for r in rows]

async def search_student_by_name(name: str) -> list:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT telegram_id, ho_ten, lop FROM students WHERE active=TRUE AND ho_ten ILIKE $1 ORDER BY ho_ten",
            f"%{name}%"
        )
    return [dict(r) for r in rows]

# ── Lessons ───────────────────────────────────────────────────────────

async def upsert_lesson(so_buoi: int, ten: str, zoom_link: str = None,
                        ngay_hoc=None, video_url: str = None) -> dict:
    sql = """
        INSERT INTO lessons (so_buoi, ten, zoom_link, ngay_hoc, video_url)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (so_buoi) DO UPDATE
            SET ten       = EXCLUDED.ten,
                zoom_link = COALESCE(EXCLUDED.zoom_link, lessons.zoom_link),
                ngay_hoc  = COALESCE(EXCLUDED.ngay_hoc,  lessons.ngay_hoc),
                video_url = COALESCE(EXCLUDED.video_url, lessons.video_url)
        RETURNING *
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, so_buoi, ten, zoom_link, ngay_hoc, video_url)
    return dict(row)

async def get_lesson(so_buoi: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM lessons WHERE so_buoi=$1", so_buoi)
    return dict(row) if row else None

# ── Materials ─────────────────────────────────────────────────────────

async def add_material(lesson_id: int, loai: str, url: str):
    sql = "INSERT INTO materials (lesson_id, loai, url) VALUES ($1, $2, $3)"
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(sql, lesson_id, loai, url)

async def get_materials(so_buoi: int) -> list:
    sql = """
        SELECT m.* FROM materials m
        JOIN lessons l ON m.lesson_id = l.id
        WHERE l.so_buoi = $1
        ORDER BY m.ngay_gui DESC
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, so_buoi)
    return [dict(r) for r in rows]

# ── Results ───────────────────────────────────────────────────────────

async def save_result(telegram_id: int, so_buoi: int,
                      diem: int, tong_cau: int,
                      chi_tiet: dict, nhan_xet_ai: str = None) -> dict:
    phan_tram = round(diem / tong_cau * 100) if tong_cau else 0
    pool = get_pool()
    async with pool.acquire() as conn:
        st = await conn.fetchrow("SELECT id FROM students WHERE telegram_id=$1", telegram_id)
        if not st:
            return None
        student_id = st["id"]

        ls = await conn.fetchrow("SELECT id FROM lessons WHERE so_buoi=$1", so_buoi)
        lesson_id = ls["id"] if ls else None

        sql = """
            INSERT INTO results
                (student_id, lesson_id, diem, tong_cau, phan_tram, chi_tiet, nhan_xet_ai)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        row = await conn.fetchrow(sql, student_id, lesson_id, diem, tong_cau, phan_tram, json.dumps(chi_tiet), nhan_xet_ai)
    return dict(row) if row else None

async def get_results_student(telegram_id: int, limit: int = 10) -> list:
    sql = """
        SELECT r.*, l.so_buoi, l.ten as ten_buoi
        FROM results r
        JOIN students s ON r.student_id = s.id
        LEFT JOIN lessons l ON r.lesson_id = l.id
        WHERE s.telegram_id = $1
        ORDER BY r.thoi_gian DESC
        LIMIT $2
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, telegram_id, limit)
    return [dict(r) for r in rows]

async def get_student_results_summary(telegram_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        st = await conn.fetchrow("SELECT id, ho_ten FROM students WHERE telegram_id=$1", telegram_id)
        if not st:
            return None
        rows = await conn.fetch("""
            SELECT l.so_buoi, l.ten as ten_buoi, r.diem, r.tong_cau, r.phan_tram, r.thoi_gian
            FROM results r
            JOIN lessons l ON r.lesson_id = l.id
            WHERE r.student_id = $1
            ORDER BY r.thoi_gian DESC
        """, st["id"])
    return {
        "ho_ten": st["ho_ten"],
        "results": [dict(r) for r in rows],
    }

async def get_chua_lam(so_buoi: int) -> list:
    sql = """
        SELECT s.telegram_id, s.ho_ten
        FROM students s
        WHERE s.active = TRUE
          AND s.id NOT IN (
              SELECT r.student_id FROM results r
              JOIN lessons l ON r.lesson_id = l.id
              WHERE l.so_buoi = $1
          )
        ORDER BY s.ho_ten
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, so_buoi)
    return [dict(r) for r in rows]

# ── Checkpoints & Sessions ──────────────────────────────────────────────

async def save_session_with_checkpoints(telegram_id: int, so_buoi: int, checkpoints: list):
    pool = get_pool()
    async with pool.acquire() as conn:
        st = await conn.fetchrow("SELECT id FROM students WHERE telegram_id=$1", telegram_id)
        if not st: return None
        student_id = st["id"]

        ls = await conn.fetchrow("SELECT id FROM lessons WHERE so_buoi=$1", so_buoi)
        lesson_id = ls["id"] if ls else None

        async with conn.transaction():
            # Tạo session
            session_id = await conn.fetchval("""
                INSERT INTO sessions (student_id, lesson_id, completed_at, status)
                VALUES ($1, $2, NOW(), 'completed')
                RETURNING id
            """, student_id, lesson_id)
            
            # Insert checkpoints
            if checkpoints:
                vals = []
                for cp in checkpoints:
                    vals.append((
                        session_id, 
                        cp.get('question_id'), 
                        cp.get('attempt_number', 1), 
                        str(cp.get('submitted_answer', '')), 
                        bool(cp.get('is_correct', False)), 
                        int(cp.get('time_spent_seconds', 0))
                    ))
                
                await conn.copy_records_to_table(
                    'checkpoints',
                    columns=['session_id', 'question_id', 'attempt_number', 'submitted_answer', 'is_correct', 'time_spent_seconds'],
                    records=vals
                )
            
            return session_id

async def get_student_checkpoint_stats(telegram_id: int) -> dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        st = await conn.fetchrow("SELECT id, ho_ten FROM students WHERE telegram_id=$1", telegram_id)
        if not st: return None
        
        # Thống kê grit (tổng số lần retry trung bình)
        grit_row = await conn.fetchrow("""
            SELECT AVG(attempt_number) as avg_attempts, MAX(attempt_number) as max_attempts 
            FROM checkpoints c
            JOIN sessions s ON c.session_id = s.id
            WHERE s.student_id = $1
        """, st["id"])
        
        # Thống kê time spent (trung bình cho các câu đúng ở lần 1)
        time_row = await conn.fetchrow("""
            SELECT AVG(time_spent_seconds) as avg_time 
            FROM checkpoints c
            JOIN sessions s ON c.session_id = s.id
            WHERE s.student_id = $1 AND c.is_correct = TRUE AND c.attempt_number = 1
        """, st["id"])
        
        return {
            "ho_ten": st["ho_ten"],
            "avg_attempts": round(float(grit_row["avg_attempts"] or 1), 2),
            "max_attempts": grit_row["max_attempts"] or 1,
            "avg_time": round(float(time_row["avg_time"] or 0), 2)
        }

# ── Gamification ──────────────────────────────────────────────────────

async def get_gamification(telegram_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT xp, gold, level, role_name, streak, streak_max, last_active, badges "
            "FROM gamification WHERE telegram_id = $1",
            telegram_id
        )
    if row:
        return dict(row)
    return None

async def save_gamification(telegram_id: int, xp: int, gold: int, level: int, role_name: str, streak: int,
                            streak_max: int, last_active: str, badges: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO gamification (telegram_id, xp, gold, level, role_name, streak, streak_max, last_active, badges)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (telegram_id) DO UPDATE SET
                xp          = EXCLUDED.xp,
                gold        = EXCLUDED.gold,
                level       = EXCLUDED.level,
                role_name   = EXCLUDED.role_name,
                streak      = EXCLUDED.streak,
                streak_max  = EXCLUDED.streak_max,
                last_active = EXCLUDED.last_active,
                badges      = EXCLUDED.badges
        """, telegram_id, xp, gold, level, role_name, streak, streak_max, last_active, badges)

async def get_leaderboard(top_n: int = 10) -> list:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                s.ho_ten,
                g.xp,
                g.streak,
                g.streak_max,
                COALESCE(json_array_length(g.badges::json), 0) AS so_huy_hieu
            FROM gamification g
            JOIN students s ON s.telegram_id = g.telegram_id
            ORDER BY g.xp DESC
            LIMIT $1
        """, top_n)
    return [dict(r) for r in rows]

async def get_leaderboard_group(telegram_ids: list, top_n: int = 10) -> list:
    if not telegram_ids:
        return []
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT s.ho_ten, g.xp, g.streak
            FROM gamification g
            JOIN students s ON s.telegram_id = g.telegram_id
            WHERE g.telegram_id = ANY($1)
            ORDER BY g.xp DESC
            LIMIT $2
        """, telegram_ids, top_n)
    return [dict(r) for r in rows]

async def get_stats_lesson(so_buoi: int) -> dict:
    sql = """
        SELECT
            COUNT(DISTINCT r.student_id)              AS so_da_lam,
            ROUND(AVG(r.phan_tram))                   AS diem_tb,
            COUNT(*) FILTER (WHERE r.phan_tram >= 80) AS gioi,
            COUNT(*) FILTER (WHERE r.phan_tram >= 60
                              AND r.phan_tram < 80)   AS kha,
            COUNT(*) FILTER (WHERE r.phan_tram < 60)  AS can_co_gang
        FROM results r
        JOIN lessons l ON r.lesson_id = l.id
        WHERE l.so_buoi = $1
    """
    tong_sql = "SELECT COUNT(*) as tong FROM students WHERE active=TRUE"
    pool = get_pool()
    async with pool.acquire() as conn:
        stats_row = await conn.fetchrow(sql, so_buoi)
        stats = dict(stats_row) if stats_row else {}
        tong_row = await conn.fetchrow(tong_sql)
        stats["tong_hs"] = tong_row["tong"] if tong_row else 0
    return stats


# ── Web Users (Google OAuth) ───────────────────────────────────────────

def _row_to_web_user(row) -> dict | None:
    if not row:
        return None
    d = dict(row)
    # Bỏ avatar_original (lớn, không cần trả về toàn bộ)
    d.pop("avatar_original", None)
    # Chuyển datetime → string để JSON serialize được
    for k, v in d.items():
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
    return d


async def get_web_user_by_telegram_id(telegram_id: int) -> dict | None:
    pool = get_pool()
    if not pool:
        return None
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM web_users WHERE telegram_id=$1", telegram_id)
    return _row_to_web_user(row)


async def upsert_web_user(google_id: str, email: str, display_name: str = "") -> dict:
    sql = """
        INSERT INTO web_users (google_id, email, ho_ten)
        VALUES ($1, $2, $3)
        ON CONFLICT (google_id) DO UPDATE
            SET email   = EXCLUDED.email
        RETURNING *
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, google_id, email, display_name)
    return _row_to_web_user(row)


async def get_web_user_by_google_id(google_id: str) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM web_users WHERE google_id=$1", google_id)
    return _row_to_web_user(row)


async def get_web_user_by_id(user_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM web_users WHERE id=$1", user_id)
    return _row_to_web_user(row)


async def get_web_users_by_status(status: str) -> list:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM web_users WHERE status=$1 ORDER BY created_at DESC",
            status)
    return [_row_to_web_user(r) for r in rows]


async def get_all_web_users() -> list:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM web_users ORDER BY created_at DESC")
    return [_row_to_web_user(r) for r in rows]


async def update_web_user_profile(google_id: str, ho_ten: str, lop: str,
                                   character_type: str, avatar_original: str,
                                   avatar_cartoon: str, avatar_final: str):
    sql = """
        UPDATE web_users SET
            ho_ten          = $2,
            lop             = $3,
            character_type  = $4,
            avatar_original = $5,
            avatar_cartoon  = $6,
            avatar_final    = $7
        WHERE google_id = $1
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(sql, google_id, ho_ten, lop, character_type,
                           avatar_original, avatar_cartoon, avatar_final)


async def patch_web_user(google_id: str, updates: dict):
    allowed = {"ho_ten", "lop", "character_type",
               "avatar_original", "avatar_cartoon", "avatar_final", "telegram_id"}
    fields  = {k: v for k, v in updates.items() if k in allowed}
    if not fields:
        return
    cols  = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    vals  = list(fields.values())
    pool  = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            f"UPDATE web_users SET {cols} WHERE google_id=$1",
            google_id, *vals)


async def approve_web_user(user_id: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE web_users SET status='approved', approved_at=NOW() WHERE id=$1",
            user_id)


async def reject_web_user(user_id: int, reason: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE web_users SET status='rejected', rejection_reason=$2 WHERE id=$1",
            user_id, reason)


async def sync_web_user_to_student(user_id: int):
    """Sau khi approve, tạo hoặc cập nhật record trong bảng students."""
    pool = get_pool()
    async with pool.acquire() as conn:
        wu = await conn.fetchrow(
            "SELECT * FROM web_users WHERE id=$1", user_id)
        if not wu or not wu["telegram_id"]:
            return
        await conn.execute("""
            INSERT INTO students (telegram_id, ho_ten, lop, active)
            VALUES ($1, $2, $3, TRUE)
            ON CONFLICT (telegram_id) DO UPDATE
                SET ho_ten = EXCLUDED.ho_ten,
                    lop    = EXCLUDED.lop,
                    active = TRUE
        """, wu["telegram_id"], wu["ho_ten"], wu["lop"])
