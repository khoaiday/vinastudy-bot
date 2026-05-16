"""
VInaStudy — Database Layer
PostgreSQL via psycopg2
"""

import os
import logging
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Tạo tất cả bảng nếu chưa có."""
    sql = """
    -- Học sinh
    CREATE TABLE IF NOT EXISTS students (
        id            SERIAL PRIMARY KEY,
        telegram_id   BIGINT UNIQUE NOT NULL,
        ho_ten        TEXT NOT NULL,
        lop           TEXT DEFAULT '3',
        telegram_ph   BIGINT,          -- telegram_id phụ huynh
        ngay_tao      TIMESTAMP DEFAULT NOW(),
        active        BOOLEAN DEFAULT TRUE
    );

    -- Buổi học
    CREATE TABLE IF NOT EXISTS lessons (
        id          SERIAL PRIMARY KEY,
        so_buoi     INT UNIQUE NOT NULL,
        ten         TEXT NOT NULL,
        zoom_link   TEXT,
        ngay_hoc    DATE,
        video_url   TEXT,
        active      BOOLEAN DEFAULT TRUE
    );

    -- Tài liệu buổi học (ảnh bảng, pdf, video)
    CREATE TABLE IF NOT EXISTS materials (
        id          SERIAL PRIMARY KEY,
        lesson_id   INT REFERENCES lessons(id),
        loai        TEXT,   -- 'anh_bang' | 'video' | 'pdf'
        url         TEXT,
        ngay_gui    TIMESTAMP DEFAULT NOW()
    );

    -- Kết quả làm bài BTVN (từ HTML5 quiz)
    CREATE TABLE IF NOT EXISTS results (
        id          SERIAL PRIMARY KEY,
        student_id  INT REFERENCES students(id),
        lesson_id   INT REFERENCES lessons(id),
        diem        INT NOT NULL,
        tong_cau    INT NOT NULL,
        phan_tram   INT,
        chi_tiet    JSONB,   -- {"q1": true, "q2": false, ...}
        nhan_xet_ai TEXT,
        thoi_gian   TIMESTAMP DEFAULT NOW()
    );

    -- Index
    CREATE INDEX IF NOT EXISTS idx_results_student ON results(student_id);
    CREATE INDEX IF NOT EXISTS idx_results_lesson  ON results(lesson_id);
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ DB init error: {e}")
        raise


# ── Students ──────────────────────────────────────────────────────────

def add_student(telegram_id: int, ho_ten: str, lop: str = "3", telegram_ph: int = None) -> dict:
    sql = """
        INSERT INTO students (telegram_id, ho_ten, lop, telegram_ph)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO UPDATE
            SET ho_ten = EXCLUDED.ho_ten,
                lop    = EXCLUDED.lop
        RETURNING *
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (telegram_id, ho_ten, lop, telegram_ph))
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def get_student(telegram_id: int) -> dict | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE telegram_id=%s", (telegram_id,))
            row = cur.fetchone()
    return dict(row) if row else None


def get_all_students() -> list:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE active=TRUE ORDER BY ho_ten")
            return [dict(r) for r in cur.fetchall()]


# ── Lessons ───────────────────────────────────────────────────────────

def upsert_lesson(so_buoi: int, ten: str, zoom_link: str = None,
                  ngay_hoc=None, video_url: str = None) -> dict:
    sql = """
        INSERT INTO lessons (so_buoi, ten, zoom_link, ngay_hoc, video_url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (so_buoi) DO UPDATE
            SET ten       = EXCLUDED.ten,
                zoom_link = COALESCE(EXCLUDED.zoom_link, lessons.zoom_link),
                ngay_hoc  = COALESCE(EXCLUDED.ngay_hoc,  lessons.ngay_hoc),
                video_url = COALESCE(EXCLUDED.video_url, lessons.video_url)
        RETURNING *
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (so_buoi, ten, zoom_link, ngay_hoc, video_url))
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def get_lesson(so_buoi: int) -> dict | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM lessons WHERE so_buoi=%s", (so_buoi,))
            row = cur.fetchone()
    return dict(row) if row else None


# ── Materials ─────────────────────────────────────────────────────────

def add_material(lesson_id: int, loai: str, url: str):
    sql = "INSERT INTO materials (lesson_id, loai, url) VALUES (%s, %s, %s)"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (lesson_id, loai, url))
        conn.commit()


def get_materials(so_buoi: int) -> list:
    sql = """
        SELECT m.* FROM materials m
        JOIN lessons l ON m.lesson_id = l.id
        WHERE l.so_buoi = %s
        ORDER BY m.ngay_gui DESC
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (so_buoi,))
            return [dict(r) for r in cur.fetchall()]


# ── Results ───────────────────────────────────────────────────────────

def save_result(telegram_id: int, so_buoi: int,
                diem: int, tong_cau: int,
                chi_tiet: dict, nhan_xet_ai: str = None) -> dict:
    """Lưu kết quả quiz. Tự tạo student/lesson nếu chưa có."""
    phan_tram = round(diem / tong_cau * 100) if tong_cau else 0

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Lấy student_id
            cur.execute("SELECT id FROM students WHERE telegram_id=%s", (telegram_id,))
            st = cur.fetchone()
            if not st:
                return None   # HS chưa đăng ký
            student_id = st["id"]

            # Lấy lesson_id
            cur.execute("SELECT id FROM lessons WHERE so_buoi=%s", (so_buoi,))
            ls = cur.fetchone()
            lesson_id = ls["id"] if ls else None

            sql = """
                INSERT INTO results
                    (student_id, lesson_id, diem, tong_cau, phan_tram, chi_tiet, nhan_xet_ai)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            cur.execute(sql, (
                student_id, lesson_id, diem, tong_cau,
                phan_tram, json.dumps(chi_tiet), nhan_xet_ai,
            ))
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def get_results_student(telegram_id: int, limit: int = 10) -> list:
    sql = """
        SELECT r.*, l.so_buoi, l.ten as ten_buoi
        FROM results r
        JOIN students s ON r.student_id = s.id
        LEFT JOIN lessons l ON r.lesson_id = l.id
        WHERE s.telegram_id = %s
        ORDER BY r.thoi_gian DESC
        LIMIT %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (telegram_id, limit))
            return [dict(r) for r in cur.fetchall()]


def get_chua_lam(so_buoi: int) -> list:
    """Danh sách HS chưa làm bài buổi X."""
    sql = """
        SELECT s.telegram_id, s.ho_ten
        FROM students s
        WHERE s.active = TRUE
          AND s.id NOT IN (
              SELECT r.student_id FROM results r
              JOIN lessons l ON r.lesson_id = l.id
              WHERE l.so_buoi = %s
          )
        ORDER BY s.ho_ten
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (so_buoi,))
            return [dict(r) for r in cur.fetchall()]


def get_stats_lesson(so_buoi: int) -> dict:
    """Thống kê kết quả cả lớp cho 1 buổi."""
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
        WHERE l.so_buoi = %s
    """
    tong_sql = "SELECT COUNT(*) as tong FROM students WHERE active=TRUE"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (so_buoi,))
            stats = dict(cur.fetchone())
            cur.execute(tong_sql)
            stats["tong_hs"] = cur.fetchone()["tong"]
    return stats
