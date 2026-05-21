import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Env variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
BASE_URL = os.getenv("BASE_URL", "https://vinastudy.vn/baitap")
CONTENT_DIR = Path(os.getenv("CONTENT_DIR", "content"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Buoi configurations
BUOI_CONFIG = {
    2:  {"ten": "Bài Toán Cấu Tạo Số",                 "video": "https://youtu.be/tQPklWVzur8",                "folder": "bai02"},
    3:  {"ten": "Viết Số Tự Nhiên Thỏa Mãn Điều Kiện", "video": "https://youtu.be/fMegXvbsYPk",                "folder": "bai03"},
    4:  {"ten": "Dãy Số Cách Đều",                      "video": "https://youtu.be/TcJ50kKlyg0",                "folder": "bai04"},
    5:  {"ten": "Biểu Thức Số",                         "video": "https://youtu.be/placeholder_b5",             "folder": "bai05"},
    6:  {"ten": "Tính Tổng Dãy Số Ghép Cặp",           "video": "https://www.youtube.com/watch?v=h1lHS_SGSjA", "folder": "bai06"},
    7:  {"ten": "Tính Tổng Dãy Số Ghép Cặp (Tiếp)",    "video": "https://youtu.be/69v3vUYp3U8",                "folder": "bai07"},
    8:  {"ten": "Ôn Tập Dãy Số + Dãy Hình Quy Luật",   "video": "https://youtu.be/19EXHoiUwTU",                "folder": "bai08"},
    27: {"ten": "Các Bài Toán Về Thời Gian",           "video": "https://www.youtube.com/watch?v=XuH1MmzQOlw", "folder": "bai27"},
}

BTVN_CONFIG = {
    2:  {"so_cau": 2,  "html": "content/lop3/bai02/bai-tap.html"},
    3:  {"so_cau": 3,  "html": "content/lop3/bai03/bai-tap.html"},
    4:  {"so_cau": 3,  "html": "content/lop3/bai04/bai-tap.html"},
    5:  {"so_cau": 3,  "html": "content/lop3/bai05/bai-tap.html"},
    6:  {"so_cau": 2,  "html": "content/lop3/bai06/bai-tap.html"},
    7:  {"so_cau": 2,  "html": "content/lop3/bai07/bai-tap.html"},
    8:  {"so_cau": 3,  "html": "content/lop3/bai08/bai-tap.html"},
    27: {"so_cau": 23, "html": "content/lop3/bai27/bai-tap.html"},
}

DANG_BAI = {
    2:  ["Cấu tạo số từ chữ số", "Tìm số theo điều kiện"],
    3:  ["Đếm số thỏa mãn điều kiện", "Số tròn chục/trăm", "Tổng chữ số"],
    4:  ["Số hạng dãy số", "Số hạng thứ N", "Đếm số chẵn/lẻ"],
    5:  ["Biểu thức có nhân chia", "Thứ tự phép tính", "Tính nhanh"],
    6:  ["Ghép cặp dãy chẵn", "Tính tổng dãy số"],
    7:  ["Ghép cặp dãy lẻ", "Dãy hình quy luật"],
    8:  ["Ôn tập dãy số", "Dãy hình theo quy luật"],
    27: ["So sánh đơn vị thời gian", "Tính khoảng thời gian",
         "Tính giờ chuyến tàu", "Xác định thứ trong tuần"],
}

DEFAULT_BUOI = 27

# ── Web server & OAuth ──────────────────────────────────────────────────
WEB_PORT        = int(os.getenv("PORT", "8080"))
BASE_DOMAIN     = os.getenv("BASE_DOMAIN", "http://localhost:8080")
SECRET_KEY      = os.getenv("SECRET_KEY", "changeme-use-random-32-chars")
ADMIN_SECRET    = os.getenv("ADMIN_SECRET", "admin-secret-token")

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI", f"{BASE_DOMAIN}/auth/google/callback")

# ── Avatar / AI ──────────────────────────────────────────────────────────
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")   # optional

# ── Characters ───────────────────────────────────────────────────────────
CHARACTERS = {
    "chien_binh": {"name": "Chiến Binh",  "emoji": "⚔️",  "color": "#0ae0fe", "bg": "#050a1f"},
    "phu_thuy":   {"name": "Phù Thủy",    "emoji": "🔮",  "color": "#ea0eed", "bg": "#0f0020"},
    "xa_thu":     {"name": "Xạ Thủ",      "emoji": "🏹",  "color": "#4eff9f", "bg": "#001f10"},
    "hiep_si":    {"name": "Hiệp Sĩ",     "emoji": "🛡️",  "color": "#ffd700", "bg": "#1a1000"},
}
