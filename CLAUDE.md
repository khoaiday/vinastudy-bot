# CLAUDE.md — Quy tắc bắt buộc cho mọi phiên làm việc

## ⚠️ ĐỌC TRƯỚC KHI LÀM BẤT CỨ ĐIỀU GÌ

### 1. Luôn cập nhật AI_CONTEXT.md
Sau MỖI thay đổi quan trọng (thiết kế, quyết định kỹ thuật, asset mới, luồng mới):
- Mở `AI_CONTEXT.md`
- Bổ sung phần liên quan
- Commit cùng với code thay đổi

### 2. Luôn cập nhật task.md
Sau MỖI task hoàn thành:
- Đánh dấu `[x]` vào task đó trong `task.md`
- Thêm task mới phát sinh vào section "Chờ làm"
- Format: `## [Claude/Gemini] YYYY-MM-DD — Tên task`

### 3. Không bao giờ để thông tin quan trọng chỉ tồn tại trong chat
Các loại thông tin PHẢI ghi vào file ngay lập tức:
- Asset đồ họa (tên file, nguồn, style)
- Track nhạc (tên, URL, Suno prompt)
- Quyết định thiết kế (tại sao chọn approach này)
- Bug đã fix (để không fix lại)
- Biến môi trường mới

### 4. Commit message chuẩn
Format: `type(scope): mô tả ngắn`
Types: feat / fix / chore / docs / style / refactor

---

## Dự án: VInaStudy Bot — Chiến Binh Toán

**Tech stack:** Vanilla HTML/CSS/JS · FastAPI · asyncpg · python-telegram-bot · Railway

**Design system:** Đại Việt cổ kính (Philosopher + Lora · Đỏ son #C0332E · Vàng nghệ #C8960C · Mực tàu #050A1F)

**MVP deadline:** 6/6/2026 — Zone Cổ Loa (Ải 7 + Ải 8) hoàn chỉnh để học sinh test

**Đọc thêm:** `AI_CONTEXT.md` (ngữ cảnh đầy đủ) · `task.md` (task board) · `WORKFLOW.md` (quy trình)
