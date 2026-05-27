# Kế hoạch Thiết kế Hồ sơ Cá nhân (profile.html) theo Giao diện Cổ kính Đại Việt

Tài liệu này mô tả chi tiết kế hoạch thiết kế và làm mới hoàn toàn giao diện Trang Quản trị Cá nhân (`profile.html`), loại bỏ hoàn toàn các di tích cyberpunk (xanh neon, hồng magenta) để đồng bộ với ngôn ngữ thiết kế "Hào khí Đại Việt" (tone màu Đỏ son, Vàng nghệ, Trầm gỗ, Ngà voi, Đồng Đông Sơn).

---

## User Review Required

> [!IMPORTANT]
> **Điểm mấu chốt của thiết kế mới:**
> 1. **Khắc phục lỗi hiển thị:** Sửa lỗi thiếu thẻ mở `<div class="wrap" id="mainContent" style="display:none">` trong `profile.html` khiến trang bị crash JS khi mở lên.
> 2. **Xóa bỏ các màu Cyberpunk:** Thay thế toàn bộ mã màu `#0ae0fe`, `#ea0eed`, `rgba(10,224,254,...)` bằng dải màu truyền thống Việt Nam:
>    - **Mực Tàu:** `#080502` làm nền tối cổ kính.
>    - **Vàng nghệ / Kim loại Gold:** `#C8960C` cho tiêu đề và các đường viền nổi bật.
>    - **Đỏ son / Son-Red:** `#C0332E` cho các nút bấm, nhân vật Lạc Tướng và trạng thái nguy hiểm.
>    - **Ngà Voi:** `#D4C4A0` cho phần văn bản mô tả để tăng tính hoài cổ, dễ chịu cho mắt.
>    - **Đồng Đông Sơn:** `rgba(184,115,51,0.3)` cho các khung lưới và đường viền phụ.
> 3. **Tối ưu hóa phông chữ:** Sử dụng đồng bộ font chữ `Philosopher` cho tiêu đề chính, `Lora` cho văn bản mô tả và nội dung biểu mẫu để giữ độ cổ điển.
> 4. **Trang Bản đồ (map.html):** Đảm bảo phần header chỉ chứa duy nhất avatar của nhân vật nằm sát lề phải, khi ấn vào sẽ chuyển hướng sang trang hồ sơ cá nhân mượt mà.

---

## Proposed Changes

### 1. `profile.html` (Hồ Sơ Chiến Binh)
#### [MODIFY] [profile.html](file:///c:/Users/Nam/OneDrive/Desktop/vinastudy-bot/profile.html)
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

### 2. `map.html` (Bản Đồ Chiến Dịch)
#### [MODIFY] [map.html](file:///c:/Users/Nam/OneDrive/Desktop/vinastudy-bot/map.html)
- Xác nhận và làm sạch phần `.header` để loại bỏ mọi văn bản thừa, nút bấm dư, chỉ để duy nhất thẻ chứa `#avatarContainer` được căn sang bên phải sát góc (`justify-content: flex-end`).

---

## Verification Plan

### Automated & Manual Verification
1. **Kiểm tra cú pháp & tính sẵn sàng của server:** Chạy `web_server.py` để đảm bảo hệ thống phản hồi tốt ở cổng `8080` (hoặc cổng cấu hình).
2. **Kiểm tra trang Hồ sơ cá nhân (`/profile`):**
   - Mở trực tiếp trình duyệt đến trang hồ sơ cá nhân.
   - Xác nhận lớp phủ loading ẩn đi chính xác sau khi tải xong dữ liệu giả lập hoặc dữ liệu từ Telegram.
   - Kiểm tra xem giao diện có hiển thị tone màu ấm hoàng gia cổ kính (Đỏ son, Vàng đồng, Trầm gỗ) hoàn toàn sạch bóng các màu xanh lam neon cũ không.
   - Thử click chọn các lớp nhân vật (Lạc Tướng, Đạo Sĩ, Nỏ Thần, Thần Tướng), xem hiệu ứng viền sáng đổi màu mượt mà.
3. **Kiểm tra trang Bản đồ (`/map`):**
   - Đảm bảo header cực kỳ tinh giản, chỉ có duy nhất avatar hình tròn nằm gọn ở góc phải.
   - Nhấn vào avatar, xác nhận trang Hồ sơ cá nhân được trượt vào/hiển thị mượt mà.
