import logging
from app.database.connection import get_pool

logger = logging.getLogger(__name__)

async def init_db():
    """Tạo tất cả bảng nếu chưa có."""
    pool = get_pool()
    if not pool:
        logger.error("❌ Pool is not initialized")
        return

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

    -- Gamification (XP, streak, huy hiệu)
    CREATE TABLE IF NOT EXISTS gamification (
        telegram_id  BIGINT PRIMARY KEY,
        xp           INTEGER DEFAULT 0,
        gold         INTEGER DEFAULT 0,
        level        INTEGER DEFAULT 1,
        role_name    TEXT DEFAULT 'Tân Binh',
        streak       INTEGER DEFAULT 0,
        streak_max   INTEGER DEFAULT 0,
        last_active  TEXT,
        badges       TEXT DEFAULT '[]'
    );

    -- Kho câu hỏi/Quái vật
    CREATE TABLE IF NOT EXISTS questions (
        id            SERIAL PRIMARY KEY,
        lesson_id     INT REFERENCES lessons(id),
        content       TEXT,
        correct_answer TEXT,
        tags          JSONB DEFAULT '[]'
    );

    -- Lượt làm bài (Session)
    CREATE TABLE IF NOT EXISTS sessions (
        id            SERIAL PRIMARY KEY,
        student_id    INT REFERENCES students(id),
        lesson_id     INT REFERENCES lessons(id),
        started_at    TIMESTAMP DEFAULT NOW(),
        completed_at  TIMESTAMP,
        status        TEXT DEFAULT 'in_progress'
    );

    -- Vết Checkpoint (Lịch sử từng câu trả lời)
    CREATE TABLE IF NOT EXISTS checkpoints (
        id                 SERIAL PRIMARY KEY,
        session_id         INT REFERENCES sessions(id),
        question_id        INT REFERENCES questions(id),
        attempt_number     INT DEFAULT 1,
        submitted_answer   TEXT,
        is_correct         BOOLEAN,
        time_spent_seconds INT,
        created_at         TIMESTAMP DEFAULT NOW()
    );

    -- Index
    CREATE INDEX IF NOT EXISTS idx_results_student ON results(student_id);
    CREATE INDEX IF NOT EXISTS idx_results_lesson  ON results(lesson_id);
    """
    try:
        async with pool.acquire() as conn:
            await conn.execute(sql)
        logger.info("✅ Database schema initialized")
    except Exception as e:
        logger.error(f"❌ DB init error: {e}")
        raise
