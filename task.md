## [Gemini] 2026-05-27 — Trang cá nhân và nút Thoát

- `[x]` 1. Sửa lỗi giao diện và cấu trúc trong `profile.html`
  - `[x]` Thêm thẻ mở `<div class="wrap" id="mainContent" style="display:none">` để khắc phục lỗi thiếu thẻ khiến trang bị treo màn hình tải.
  - `[x]` Đồng bộ hóa hệ CSS variables sang dải màu truyền thống Đại Việt (Mực Tàu, Vàng nghệ, Đỏ son, Ngà voi, Đồng Đông Sơn).
  - `[x]` Dọn dẹp triệt để các mã màu cyberpunk/neon còn sót lại (xanh lam neon, hồng tím magenta).
- `[x]` 2. Bổ sung tính năng "Thoát" (Exit) trên trang hồ sơ
  - `[x]` Thêm nút "THOÁT" ở góc dưới cùng, thiết kế tinh tế kế bên nút "LƯU HỒ SƠ" trong `.save-bar`.
  - `[x]` Lập trình hàm `exitProfile()` để gửi tín hiệu `close_profile` đến cửa sổ cha (iframe) hoặc chuyển hướng về trang `/map` nếu mở độc lập.
- `[x]` 3. Cập nhật trang bản đồ (`map.html`)
  - `[x]` Xác minh và làm sạch header, đảm bảo chỉ có duy nhất nút avatar nhân vật và được căn sát lề phải.
  - `[x]` Bổ sung xử lý sự kiện nhận tin nhắn `close_profile` từ iframe trang cá nhân để đóng modal trượt mượt mờ.
- `[x]` 4. Kiểm tra thực tế
  - `[x]` Mở trang bản đồ, click avatar xem trang profile mở ra mượt mà và tắt lớp phủ loading chuẩn xác không.
  - `[x]` Giao diện profile mang vẻ cổ kính, sang trọng của Đại Việt.
  - `[x]` Nhấn nút "THOÁT", trang profile đóng lại ngay lập tức và đưa người dùng về bản đồ.

---
---

## [Claude] 2026-05-27 — Cập nhật cốt truyện Ải 1 (Thánh Gióng + Quỷ Số)

- `[x]` Sửa card Ải 1 trên map: "Bản thiết kế thành Cổ Loa" → "Rèn Giáp Cho Thánh Gióng"
- `[x]` Sửa intro modal title: "Truy tìm chúa tể" → "Rèn Giáp Cho Thánh Gióng"
- `[x]` Sửa intro story: Boss Số Thần → Quỷ Số + cốt truyện Thánh Gióng
- `[x]` Sửa intro mission: yêu cầu rèn 2 tuyệt chiêu trước khi vào ải

---
---

## [Claude] 2026-05-27 — Sửa giao diện minigame.html (Tuyệt Chiêu 1)

- `[x]` Cập nhật tab title → "Tuyệt Chiêu 1: Phân Biệt Số & Chữ Số — Chiến Binh Toán"
- `[x]` Cập nhật header h1 game → "Rèn Tuyệt Chiêu 1 — Phân Biệt Số & Chữ Số" (dùng — thay / tránh wrapping)
- `[x]` Cập nhật CSS `.header h1` → dùng `clamp(14px, 4vw, 22px)` + `line-height: 1.3` cho mobile
- `[x]` Cập nhật Start Screen → cốt truyện Thánh Gióng / Quỷ Số, bỏ An Dương Vương / Loa Thành
- `[x]` Cập nhật Win Screen → "Tuyệt chiêu đã rèn xong! Thánh Gióng sắp có giáp ra trận!"
- `[x]` Cập nhật Fail Screen → "Tuyệt chiêu chưa rèn xong! Quỷ Số còn ngự trị!"
- `[x]` Sửa background fail screen → dùng ảnh boss có sẵn thay vì file lỗi
- `[x]` Loại bỏ font 'Chakra Petch' (không load) → dùng `var(--font-title)` nhất quán

---
---

## [Gemini] 2026-05-27 — Khắc phục lỗi lưu Avatar trên trang Bản đồ khi F5

- `[x]` Chuyển đổi hàm `loadSelectedCharacter` từ IIFE thành hàm toàn cục có tham số ghi đè `loadSelectedCharacter(charOverride)`.
- `[x]` Cập nhật hàm `authGate()` trong `map.html` để đồng bộ thông tin nhân vật và giới tính từ cơ sở dữ liệu (`character_type`, `gioi_tinh`) vào `localStorage` và `sessionStorage` (`vsSelectedChar`).
- `[x]` Kích hoạt `loadSelectedCharacter(mappedChar)` ngay trong `authGate()` sau khi đồng bộ thành công để cập nhật giao diện avatar tức thời.
- `[x]` Đảm bảo khi F5 hoặc tải lại trang, avatar luôn hiển thị nhân vật mới nhất được lưu trong cơ sở dữ liệu thay vì avatar cũ lưu trong cache cũ.

---
---

## [Gemini] 2026-05-27 — Tối ưu hóa hiển thị Mobile cho 2 Minigames

- `[x]` Thêm các quy tắc CSS `@media (max-width: 420px)` và `@media (max-height: 680px)` vào `minigame.html` để thu nhỏ kích thước thẻ bài tương thích với các dòng máy di động màn hình nhỏ.
- `[x]` Thêm các quy tắc CSS tương tự vào `minigame2.html`, giảm kích thước của trung tâm thẻ bài (`.deck-container`) từ 240px xuống 180px và thu hẹp các hộp chứa mục tiêu hai bên từ 80px xuống 60px trên màn hình di động.
- `[x]` Loại bỏ hoàn toàn lỗi đè lấp (overlapping) giữa xếp bài ở giữa và các hộp mục tiêu Hàng Trăm/Chục/Đơn vị hai bên trên màn hình điện thoại dưới 420px.
- `[x]` Đảm bảo trò chơi hiển thị trọn vẹn bên trong iframe mà không gây ra thanh cuộn dọc (vertical scrollbars) trên các thiết bị chiều cao thấp.

---
---

## [Gemini] 2026-05-27 — Khắc Phục Lỗi Giao Diện 2 Minigame

- `[x]` 1. Khắc Phục Lỗi Đè Lấp Trên Màn Hình Cực Nhỏ
  - `[x]` Tối ưu hóa padding của `.targets-container` xuống `10px` (<420px) và `6px` (<360px).
  - `[x]` Thêm media query `@media (max-width: 360px)` để giảm kích thước xếp bài ở giữa xuống `140px` và hộp mục tiêu xuống `45px`.
  - `[x]` Đảm bảo khoảng cách an toàn (gap) đạt `39px`, giải quyết dứt điểm lỗi chồng chéo phần tử trên các dòng máy 320px - 360px.
- `[x]` 2. Giải Phóng Không Gian Hiển Thị Tránh Double Headers
  - `[x]` Thiết lập đoạn script kiểm tra chế độ iframe (`window.parent !== window`).
  - `[x]` Tự động ẩn thẻ tiêu đề `h1` bên trong minigame, tiết kiệm `35px-40px` chiều cao cho vùng chơi chính.
  - `[x]` Tối ưu hóa media query `@media (max-height: 540px)` cho các khung nhìn có chiều cao siêu hạn chế.
- `[x]` 3. Nâng Cao Trải Nghiệm Thoát UX (No-Trapping)
  - `[x]` Tích hợp thêm nút "QUAY LẠI ẢI" (Exit) trên màn hình Thất bại (Failure Screen) của cả hai minigames.
  - `[x]` Xây dựng hàm `exitMinigame()` gửi tín hiệu `close_profile` ra ngoài cửa sổ mẹ để đóng modal trượt êm ái.
- `[x]` 4. Cải Thiện Thẩm Mỹ Truyền Thuyết & Cú Pháp HTML
  - `[x]` Thay thế phông chữ thô cứng `var(--font-mono)` trên thẻ bài Minigame 2 và feedback chữ số thành phông chữ truyền thống Đại Việt `var(--font-title)` (Philosopher).
  - `[x]` Loại bỏ thẻ đóng `</div>` dư thừa lỗi cú pháp ở dòng 624 của `minigame2.html`.

---
---

## [Gemini] 2026-05-27 — Tinh Chỉnh Thu Nhỏ Thẻ Bài Phân Biệt Số

- `[x]` 1. Khóa Chống Móp Méo Tỉ Lệ Thẻ Bài
  - `[x]` Bổ sung `flex-shrink: 0` cho `.card-container` để ngăn trình duyệt tự động ép bóp dẹt chiều cao thẻ bài khi thiếu không gian dọc.
- `[x]` 2. Thu Nhỏ Triệt Để Thẻ Bài Cho Mọi Viewport
  - `[x]` Giảm kích thước `.card-container` trên thiết bị <420px xuống còn **215px x 295px**, cỡ chữ số xuống **75px**.
  - `[x]` Giảm kích thước `.card-container` trên thiết bị cực nhỏ <360px xuống còn **190px x 260px**, cỡ chữ số xuống **65px**.
- `[x]` 3. Khắc Phục Giao Diện Chữ Số Thẻ Bẫy (Trick Card)
  - `[x]` Loại bỏ inline `font-size: 120px` ghi đè thô bạo trên thẻ bẫy.
  - `[x]` Thay thế bằng các class `.trick-text` và `.trick-number` thích ứng linh hoạt trong CSS để tự động thu nhỏ chữ số bẫy trên di động.
- `[x]` 4. Ẩn Header Bằng CSS Thuần
  - `[x]` Áp dụng quy tắc `@media` ẩn `.header h1` trực tiếp khi chiều rộng <420px hoặc chiều cao <680px, cam kết sạch bóng double headers.

---
---

## [Claude] 2026-05-28 — Sửa Lỗi "/" Ảo Trong Quick Tour (minigame.html)

- `[x]` 1. Xác định nguyên nhân lỗi
  - `[x]` Chữ số "7" hiển thị 160px trong `showTourStep(0)` bị tooltip tour đè lên phần trên (~51px)
  - `[x]` Chỉ còn thấy nét chéo dưới của "7" → trông như dấu "/" bồng bềnh
- `[x]` 2. Sửa `showTourStep()` trong `minigame.html`
  - `[x]` Step 0: giảm font số demo từ 160px → 80px, thêm nhãn `"← CHỮ SỐ | SỐ →"`
  - `[x]` Step 2: giảm font số "23" từ 160px → 80px, thêm nhãn `"👉 Đây là SỐ (>9)"`
  - `[x]` Step 3 (trick card): giảm font text bẫy 2.5rem → 1.8rem, số 120px → 80px
  - `[x]` Font `.number-display` trong gameplay thực (CSS class) KHÔNG thay đổi
- `[x]` 3. Commit & push (c9ce117)

---
---
