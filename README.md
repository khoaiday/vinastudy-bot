# VInaStudy Bot — Toán Lớp 3 HSG

Bot Telegram dạy Toán lớp 3 bồi dưỡng học sinh giỏi.
Thầy Nguyễn Thành Long | [vinastudy.vn](https://vinastudy.vn)

---

## Cấu trúc repo

```
vinastudy-bot/
├── bot.py                          # Bot Telegram chính
├── requirements.txt                # Python dependencies
├── README.md                       # File này
│
└── content/                        # Nội dung buổi học
    └── lop3/
        ├── bai02/
        │   ├── system-prompt.txt   # System prompt cho AI
        │   └── bai-tap.html        # Bài tập HTML5
        ├── bai03/ ... bai08/       # Tương tự
        └── bai27/
            ├── system-prompt.txt
            └── bai-tap.html
```

---

## Deploy lên Railway

### 1. Tạo project Railway
- Kết nối repo GitHub này với Railway
- Railway tự động deploy khi push code mới

### 2. Environment Variables (Railway)
```
TELEGRAM_TOKEN=<token từ @BotFather>
ANTHROPIC_API_KEY=<key từ console.anthropic.com>
BASE_URL=https://[username].github.io/vinastudy-bot
CONTENT_DIR=content
```

### 3. Bật GitHub Pages
```
Settings → Pages → Source: Deploy from branch → main → / (root)
```
URL bài tập sẽ là: `https://[username].github.io/vinastudy-bot/content/lop3/baiXX/bai-tap.html`

---

## Tính năng bot

| Nút | Chức năng |
|-----|-----------|
| 🏠 Bài tập về nhà | Danh sách 8 buổi → mở file HTML bài tập |
| 🎯 Kiểm tra năng lực | Đang phát triển |
| 📊 Bảng điểm | Đang phát triển |
| 📹 Xem video | Link video YouTube buổi hiện tại |
| 💬 Hỏi bài | Chat với AI theo phương pháp thầy Long |
| 📚 Chọn buổi học | Chuyển sang buổi học khác |
| 🗑️ Xoá lịch sử | Xoá lịch sử hội thoại |

### Lệnh bot
```
/start     — Khởi động, hiện menu chính
/btvn      — Mở menu bài tập về nhà
/chonbuoi  — Chọn buổi học
/video     — Link video buổi hiện tại
/xoa       — Xoá lịch sử hội thoại
```

---

## Danh sách buổi học

| Buổi | Chủ đề | Video |
|------|--------|-------|
| 2  | Bài Toán Cấu Tạo Số | [YouTube](https://youtu.be/tQPklWVzur8) |
| 3  | Viết Số Tự Nhiên Thỏa Mãn Điều Kiện | [YouTube](https://youtu.be/fMegXvbsYPk) |
| 4  | Dãy Số Cách Đều | [YouTube](https://youtu.be/TcJ50kKlyg0) |
| 5  | Biểu Thức Số | YouTube |
| 6  | Tính Tổng Dãy Số Ghép Cặp | [YouTube](https://www.youtube.com/watch?v=h1lHS_SGSjA) |
| 7  | Tính Tổng Dãy Số Ghép Cặp (Tiếp) | [YouTube](https://youtu.be/69v3vUYp3U8) |
| 8  | Ôn Tập Dãy Số + Dãy Hình Quy Luật | [YouTube](https://youtu.be/19EXHoiUwTU) |
| 27 | Các Bài Toán Về Thời Gian | [YouTube](https://www.youtube.com/watch?v=XuH1MmzQOlw) |

---

## Tech Stack
- **Bot**: Python 3.12 + python-telegram-bot 21.0
- **AI**: Anthropic Claude claude-sonnet-4-6
- **Deploy**: Railway.app
- **Bài tập**: GitHub Pages (HTML5 static)

---

*BẢN QUYỀN BÀI GIẢNG THUỘC VỀ CÔNG TY TNHH GIÁO DỤC TRỰC TUYẾN VINASTUDY*
*Website: [vinastudy.vn](https://vinastudy.vn) — Hotline: 0932.39.39.56 – 0832.64.64.64*
