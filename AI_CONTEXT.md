# VINASTUDY BOT - BATTLE ARENA PROJECT CONTEXT

Tài liệu này chứa toàn bộ ngữ cảnh, quy chuẩn thiết kế và cấu trúc kỹ thuật mới nhất của dự án "VinaStudy Bot - Chiến binh Toán học". Hãy đọc kỹ tài liệu này trước khi thực hiện bất kỳ thay đổi nào để đảm bảo tính đồng bộ của dự án.

## 1. Tổng quan dự án
- **Mục tiêu:** Chuyển đổi các bài tập Toán học dạng danh sách nhàm chán thành một **Mini-game nhập vai (RPG) phong cách Cyberpunk / Sci-fi** ngay trên giao diện Telegram WebApp.
- **Tech Stack:** Vanilla HTML, CSS, JavaScript (Không sử dụng Framework nặng để đảm bảo tốc độ tải trên Telegram WebApp).

## 2. Quy chuẩn Đồ họa (Cyberpunk UI System)
Mọi thiết kế giao diện phải tuân thủ nghiêm ngặt hệ thống Design Tokens sau:

### 2.1. Typography & Colors
- **Font chữ:** `Roboto` (Nội dung dễ đọc) và `Rajdhani` (Tiêu đề, số liệu mang tính tương lai).
- **Màu nền tổng thể:** Nền tối `#050a1f` (Dark Navy) kết hợp lưới hoặc gradient.
- **Màu Neon chủ đạo:**
  - `var(--primary)`: `#0ae0fe` (Cyan/Neon Blue) - Dùng cho viền, nút bấm chính.
  - `var(--secondary)`: `#ea0eed` (Neon Purple) - Dùng cho điểm nhấn, Boss.
  - `var(--success)`: `#4eff9f` (Neon Green) - Dùng cho đáp án Đúng.
  - `var(--danger)`: `#ff0055` (Neon Red) - Dùng cho đáp án Sai.
  - `var(--amber)`: `#fbbf24` (Vàng/Cam) - Dùng cho cảnh báo, chờ đợi.

### 2.2. Hiệu ứng đặc trưng (Signature Effects)
- **Cyber Box (`.cyber-box`):** 
  - Khung viền bo tròn 16px.
  - Viền phát sáng được tạo bằng kỹ thuật `::before` với `linear-gradient` và dùng `-webkit-mask` cắt viền 2px hoàn hảo. 
  - KHÔNG sử dụng `border` thông thường hay `clip-path` cắt góc nữa.
- **Battle Arena Header:**
  - Sàn đấu 3D: Cấu trúc sử dụng `transform: rotateX(75deg)` kết hợp với ảnh nền lưới định dạng **SVG** (`stroke-width=3`) để chống nhiễu Moiré.
  - Các ký hiệu toán học lơ lửng: Sử dụng `translateZ` để bay từ xa (-600px) tới gần (400px), tạo chiều sâu không gian (Depth of Field).

## 3. Cấu trúc Gameplay (Single-Screen Mechanics)
- **Slide-based:** Thay vì hiển thị toàn bộ câu hỏi (Scrollable), bài tập được chia thành các màn hình nhỏ (Slide). Mỗi `q-slide` chứa Tiêu đề dạng, lý thuyết (`method-box`) và 1 câu hỏi.
- **Tự động chuyển cảnh:** Khi người chơi trả lời ĐÚNG, nút "Kiểm tra" chuyển thành nút "Tiếp tục" nhấp nháy (`pulseNeon`). Nhấn nút này sẽ tự động giấu slide hiện tại và trượt slide tiếp theo ra (`animation: fadeInRight`).
- **Hệ thống Combat:** 
  - Tích hợp thanh HP (Máu) của Người chơi và Quái vật. 
  - Trả lời đúng: Quái vật mất máu, bị rung lắc (`animation: shake`).
  - Trả lời sai: Người chơi mất máu.

## 4. Cấu trúc Thư mục (Directory Structure)
- `content/lop3/bai02/bai-tap.html`: **Phiên bản hoàn thiện nhất (Master Template)**. Toàn bộ tính năng Battle Arena và Slide đã được triển khai hoàn chỉnh ở đây.
- `content/lop3/bai03...`: Hiện tại mới chỉ được tiêm (inject) lớp CSS Cyberpunk bằng đoạn code ở cuối file (`CYBERPUNK RESKIN OVERRIDES`). Chưa được chuyển đổi cấu trúc HTML sang dạng Battle Arena.

## 5. Quy tắc cho AI (AI Instructions)
1. **Tuyệt đối không** phá vỡ cấu trúc `.cyber-box` bằng cách thêm border viền thuần. Phải sử dụng cấu trúc `::before/::after` đã có sẵn.
2. **Khi tạo giao diện mới**, luôn ưu tiên sử dụng dải màu Neon và thêm `box-shadow: 0 0 15px var(--primary-glow)` để tạo hiệu ứng phát sáng.
3. Khi làm việc với `bai03` đến `bai36`, cần cẩn thận vì cấu trúc HTML của chúng vẫn là dạng danh sách cũ. Nếu cần nâng cấp lên dạng Battle Arena, hãy tham khảo file `bai02/bai-tap.html` làm khuôn mẫu chuẩn.
