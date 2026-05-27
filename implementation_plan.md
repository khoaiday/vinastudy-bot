## [Gemini] 2026-05-27 — Thiết kế Hồ sơ Cá nhân (profile.html) theo Giao diện Cổ kính Đại Việt

Tài liệu này mô tả chi tiết kế hoạch thiết kế và làm mới hoàn toàn giao diện Trang Quản trị Cá nhân (`profile.html`), loại bỏ hoàn toàn các di tích cyberpunk (xanh neon, hồng magenta) để đồng bộ với ngôn ngữ thiết kế "Hào khí Đại Việt" (tone màu Đỏ son, Vàng nghệ, Trầm gỗ, Ngà voi, Đồng Đông Sơn).

### Điểm mấu chốt của thiết kế mới:
1. **Khắc phục lỗi hiển thị:** Sửa lỗi thiếu thẻ mở `<div class="wrap" id="mainContent" style="display:none">` trong `profile.html` khiến trang bị crash JS khi mở lên.
2. **Xóa bỏ các màu Cyberpunk:** Thay thế toàn bộ mã màu `#0ae0fe`, `#ea0eed`, `rgba(10,224,254,...)` bằng dải màu truyền thống Việt Nam:
   - **Mực Tàu:** `#080502` làm nền tối cổ kính.
   - **Vàng nghệ / Kim loại Gold:** `#C8960C` cho tiêu đề và các đường viền nổi bật.
   - **Đỏ son / Son-Red:** `#C0332E` cho các nút bấm, nhân vật Lạc Tướng và trạng thái nguy hiểm.
   - **Ngà Voi:** `#D4C4A0` cho phần văn bản mô tả để tăng tính hoài cổ, dễ chịu cho mắt.
   - **Đồng Đông Sơn:** `rgba(184,115,51,0.3)` cho các khung lưới và đường viền phụ.
3. **Tối ưu hóa phông chữ:** Sử dụng đồng bộ font chữ `Philosopher` cho tiêu đề chính, `Lora` cho văn bản mô tả và nội dung biểu mẫu để giữ độ cổ điển.
4. **Trang Bản đồ (map.html):** Đảm bảo phần header chỉ chứa duy nhất avatar của nhân vật nằm sát lề phải, khi ấn vào sẽ chuyển hướng sang trang hồ sơ cá nhân mượt mà.

### Các thay đổi đề xuất:

#### `profile.html` (Hồ Sơ Chiến Binh)
- **Cập nhật CSS Variables:** Đồng bộ dải màu truyền thống Đại Việt.
- **Loại bỏ Cyberpunk styling:**
  - Sửa `.hdr` có dải gradient trong suốt vàng đồng thay vì xanh neon.
  - Sửa `.cyber-card::before` sử dụng gradient vàng đồng - đỏ son (`linear-gradient(135deg, var(--primary), var(--secondary))`).
  - Sửa `.avatar-ring::before` sử dụng dải màu truyền thống cùng hiệu ứng tỏa sáng màu vàng đồng ấm thay vì xanh lam.
  - Sửa `.field input`, `.field select` có màu nền trầm gỗ kết hợp ánh đồng Đông Sơn.
  - Sửa `.gender-btn.active-nam` và `.gender-btn.active-nu` đồng bộ sang tone Đỏ Son và Vàng Đồng truyền thống.
  - Sửa nền Crop Modal `#cropModal` sang màu Mực Tàu `#080502` tối giản.
- **Sửa lỗi cấu trúc HTML:**
  - Bổ sung thẻ mở `<div class="wrap" id="mainContent" style="display:none">` sau thẻ đóng của `#loadOverlay` để ôm toàn bộ nội dung trang profile và khớp với lệnh đóng/mở loading bằng JS.
  - Căn chỉnh lề và hiệu ứng kéo thả mượt mà trên thiết bị di động.

#### `map.html` (Bản Đồ Chiến Dịch)
- Xác nhận và làm sạch phần `.header` để loại bỏ mọi văn bản thừa, nút bấm dư, chỉ để duy nhất thẻ chứa `#avatarContainer` được căn sang bên phải sát góc (`justify-content: flex-end`).

### Kế hoạch xác minh:
1. **Kiểm tra cú pháp & tính sẵn sàng của server:** Chạy `web_server.py` để đảm bảo hệ thống phản hồi tốt ở cổng `8080` (hoặc cổng cấu hình).
2. **Kiểm tra trang Hồ sơ cá nhân (`/profile`):**
   - Mở trực tiếp trình duyệt đến trang hồ sơ cá nhân.
   - Xác nhận lớp phủ loading ẩn đi chính xác sau khi tải xong dữ liệu giả lập hoặc dữ liệu từ Telegram.
   - Kiểm tra xem giao diện có hiển thị tone màu ấm hoàng gia cổ kính (Đỏ son, Vàng đồng, Trầm gỗ) hoàn toàn sạch bóng các màu xanh lam neon cũ không.
   - Thử click chọn các lớp nhân vật (Lạc Tướng, Đạo Sĩ, Nỏ Thần, Thần Tướng), xem hiệu ứng viền sáng đổi màu mượt mà.
3. **Kiểm tra trang Bản đồ (`/map`):**
   - Đảm bảo header cực kỳ tinh giản, chỉ có duy nhất avatar hình tròn nằm gọn ở góc phải.
   - Nhấn vào avatar, xác nhận trang Hồ sơ cá nhân được trượt vào/hiển thị mượt mà.

---
---

## [Claude] 2026-05-27 — Ải 1: Thánh Gióng + Quỷ Số

### Đã hoàn thành
- [x] Đổi tên card Ải 1 trên map → "Rèn Giáp Cho Thánh Gióng"
- [x] Viết cốt truyện intro modal (Thánh Gióng, Quỷ Số xáo số, rèn 2 tuyệt chiêu)
- [x] Cập nhật `map.html`

### Tiếp theo
- [ ] Viết cốt truyện Ải 2 (buổi + chất liệu lịch sử chưa xác định)
- [ ] Cập nhật text boss trong `bai01/bai-tap.html` (đổi Số Thần → Quỷ Số nếu cần)

---
---

## [Gemini] 2026-05-27 — Sửa lỗi F5 bị hiển thị Avatar cũ trên trang Bản đồ

Tài liệu này đề xuất phương án giải quyết dứt điểm lỗi khi nhấn F5/Reload trang Bản đồ thì avatar người dùng bị hiển thị lại avatar cũ.

### Giải pháp kỹ thuật:
1. **Lỗi hiện tại:** Hàm `authGate()` trong `map.html` lấy thông tin chính xác từ DB nhưng không ghi nhận giá trị nhân vật và giới tính mới vào `localStorage.getItem('vsSelectedChar')`. Khi F5, hàm tải ảnh `loadSelectedCharacter()` (dạng IIFE tự thực thi) sẽ đọc giá trị cũ từ `localStorage` và ghi đè ảnh đại diện cũ lên giao diện.
2. **Đồng bộ cơ sở dữ liệu:** Thêm ánh xạ nhân vật/giới tính từ API trả về để tự động ghi đè khóa `vsSelectedChar` trong `localStorage` và `sessionStorage`.
3. **Chuyển đổi hàm toàn cục:** Chuyển `loadSelectedCharacter` thành hàm có tham số ghi đè `loadSelectedCharacter(charOverride)` để có thể gọi lại bất cứ lúc nào trong `authGate()`, giúp cập nhật avatar mới ngay lập tức mà không cần đợi người dùng reload thủ công.

### Các thay đổi đề xuất:

#### `map.html` (Bản Đồ Chiến Dịch)
- **Sửa hàm `loadSelectedCharacter`**: Bỏ IIFE, chuyển thành hàm thông thường và hỗ trợ tham số ghi đè `charOverride`.
- **Sửa hàm `authGate()`**: Bổ sung cơ chế đồng bộ hóa dữ liệu từ DB vào `localStorage` và kích hoạt hàm vẽ lại avatar `loadSelectedCharacter(mappedChar)`.

---
---
