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

    -- ── Web users (Google OAuth) ──────────────────────────────────────
    CREATE TABLE IF NOT EXISTS web_users (
        id               SERIAL PRIMARY KEY,
        google_id        VARCHAR(120) UNIQUE NOT NULL,
        email            VARCHAR(255) UNIQUE NOT NULL,
        ho_ten           VARCHAR(100),
        lop              VARCHAR(10) DEFAULT '3',
        character_type   VARCHAR(30) DEFAULT 'chien_binh',
        avatar_original  TEXT,        -- base64 ảnh gốc
        avatar_cartoon   TEXT,        -- base64 ảnh hoạt hình
        avatar_final     TEXT,        -- base64 avatar cuối (face + frame)
        telegram_id      BIGINT,
        status           VARCHAR(20)  DEFAULT 'pending',
        rejection_reason TEXT,
        created_at       TIMESTAMPTZ  DEFAULT NOW(),
        approved_at      TIMESTAMPTZ,
        approved_by      VARCHAR(50)
    );

    -- ── Web sessions (JWT refresh store) ─────────────────────────────
    CREATE TABLE IF NOT EXISTS web_sessions (
        id         VARCHAR(64) PRIMARY KEY,
        google_id  VARCHAR(120) NOT NULL,
        data       JSONB DEFAULT '{}',
        expires_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_web_users_status     ON web_users(status);
    CREATE INDEX IF NOT EXISTS idx_web_users_email      ON web_users(email);
    CREATE INDEX IF NOT EXISTS idx_web_users_telegram   ON web_users(telegram_id);
    CREATE INDEX IF NOT EXISTS idx_web_sessions_gid   ON web_sessions(google_id);
    CREATE INDEX IF NOT EXISTS idx_web_sessions_exp   ON web_sessions(expires_at);
    """
    migration = """
    ALTER TABLE web_users ADD COLUMN IF NOT EXISTS gioi_tinh VARCHAR(10) DEFAULT 'nam';

    -- Thêm level vào results để biết học sinh chơi level nào
    ALTER TABLE results ADD COLUMN IF NOT EXISTS level INT DEFAULT 1;

    -- Thêm question_num (số thứ tự câu 1-N) vào checkpoints, không dùng FK
    ALTER TABLE checkpoints ADD COLUMN IF NOT EXISTS question_num INT;

    -- Thách đấu giữa học sinh
    CREATE TABLE IF NOT EXISTS challenges (
        id               SERIAL PRIMARY KEY,
        challenger_id    BIGINT NOT NULL,
        challengee_id    BIGINT NOT NULL,
        so_buoi          INT NOT NULL,
        challenger_score INT,
        challengee_score INT,
        status           TEXT DEFAULT 'pending',
        winner_id        BIGINT,
        created_at       TIMESTAMP DEFAULT NOW(),
        expires_at       TIMESTAMP DEFAULT NOW() + INTERVAL '24 hours'
    );
    CREATE INDEX IF NOT EXISTS idx_challenges_challenger ON challenges(challenger_id);
    CREATE INDEX IF NOT EXISTS idx_challenges_challengee ON challenges(challengee_id);
    CREATE INDEX IF NOT EXISTS idx_challenges_status     ON challenges(status);
    """
    try:
        async with pool.acquire() as conn:
            await conn.execute(sql)
            await conn.execute(migration)
        logger.info("✅ Database schema initialized")
    except Exception as e:
        logger.error(f"❌ DB init error: {e}")
        raise
