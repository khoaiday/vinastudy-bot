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

# ── Gamification ──────────────────────────────────────────────────────

async def get_gamification(telegram_id: int) -> dict | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT xp, streak, streak_max, last_active, badges "
            "FROM gamification WHERE telegram_id = $1",
            telegram_id
        )
    if row:
        return {
            "xp":          row["xp"],
            "streak":      row["streak"],
            "streak_max":  row["streak_max"],
            "last_active": row["last_active"],
            "badges":      row["badges"],
        }
    return None

async def save_gamification(telegram_id: int, xp: int, streak: int,
                            streak_max: int, last_active: str, badges: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO gamification (telegram_id, xp, streak, streak_max, last_active, badges)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (telegram_id) DO UPDATE SET
                xp          = EXCLUDED.xp,
                streak      = EXCLUDED.streak,
                streak_max  = EXCLUDED.streak_max,
                last_active = EXCLUDED.last_active,
                badges      = EXCLUDED.badges
        """, telegram_id, xp, streak, streak_max, last_active, badges)

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
