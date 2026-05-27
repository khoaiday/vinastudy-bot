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

## [Claude] 2026-05-27 — Sửa giao diện minigame.html cho chủ đề Thánh Gióng

### Vấn đề
Commit Gemini (`8f350df`) đã nhầm khi đổi text `minigame.html` từ chủ đề "Phân Biệt Số & Chữ Số" sang "Bản thiết kế thành Cổ Loa" (chủ đề cũ). Ngoài ra header h1 dài gây lỗi "/" float trên mobile khi text wraps.

### Giải pháp
- Dùng `font-size: clamp()` cho `.header h1` để giới hạn kích cỡ font trên mọi thiết bị
- Dùng "—" (em dash) thay "/" làm separator trong h1 để tránh wrap thành ký tự đơn
- Cập nhật toàn bộ text để khớp với chủ đề Ải 1: Thánh Gióng / Quỷ Số
- Sửa background reference đến file ảnh tồn tại thực sự

### Tiếp theo
- [ ] Test visual trên mobile (điện thoại thực hoặc DevTools)
- [ ] Cập nhật `minigame2.html` nếu cũng còn text cũ

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

## [Gemini] 2026-05-27 — Tối ưu hóa hiển thị Mobile cho 2 Minigames

Tài liệu này đề xuất phương án tối ưu hóa thiết kế thích ứng (responsive design) trên thiết bị di động cho cả hai minigames luyện tập, giải quyết triệt để vấn đề chồng chéo (overlapping) phần tử gameplay trên các dòng máy màn hình nhỏ.

### Giải pháp kỹ thuật:
1. **Minigame 1 (`minigame.html`):** Thiết lập các CSS media queries (@media) cho màn hình chiều rộng hẹp (dưới 420px) và chiều cao hạn chế (dưới 680px) để thu nhỏ kích thước thẻ bài vuốt từ 320px xuống 280px/260px và giảm kích thước hiển thị chữ số.
2. **Minigame 2 (`minigame2.html`):** 
   - **Vấn đề chồng lấn:** Xếp bài ở giữa (`.deck-container`) có chiều rộng tĩnh là 240px, khi hiển thị trên màn hình điện thoại 360px sẽ che lấp toàn bộ các hộp mục tiêu Hàng Trăm, Chục, Đơn vị hai bên (.target-box, rộng 80px mỗi bên).
   - **Giải pháp:** Sử dụng CSS `@media (max-width: 420px)` để tự động co tỷ lệ của `.deck-container` xuống 180px, đồng thời giảm kích cỡ `.target-box` xuống 60px và cỡ chữ số xuống 2.5rem, mở ra khoảng trống 40px ở giữa giúp loại bỏ hoàn toàn việc chồng đè.
   - Thêm media query chiều cao hạn chế để tự động thu nhỏ giao diện khi minigame chạy bên trong iframe có chiều cao hạn chế của trang Bản đồ.

### Các thay đổi đề xuất:

#### `minigame.html` (Tuyệt Chiêu 1)
- Bổ sung quy tắc CSS thích ứng chiều rộng (`max-width: 420px`) và chiều cao (`max-height: 680px`) ở cuối thẻ `<style>`.

#### `minigame2.html` (Tuyệt Chiêu 2)
- Bổ sung quy tắc CSS thích ứng chiều rộng (`max-width: 420px`) và chiều cao (`max-height: 680px`) ở cuối thẻ `<style>`.

---
---

## [Gemini] 2026-05-27 — Sửa Triệt Để Lỗi Giao Diện 2 Minigame

Tài liệu này trình bày phương án khắc phục hoàn toàn lỗi giao diện, tối ưu không gian hiển thị trên các dòng điện thoại siêu nhỏ (320px - 360px), loại bỏ hiện tượng đè lấp và cải thiện trải nghiệm thoát/back.

### Điểm mấu chốt của thiết kế tối ưu:
1. **Tránh Cluttering Đầu Trang (Double Headers):** Khi minigame chạy trong iframe trên trang Bản đồ, header của trang mẹ chiếm diện tích đáng kể. Tôi thực hiện tự động ẩn tiêu đề `h1` bên trong minigame khi chạy ở chế độ iframe (`window.parent !== window`), chỉ giữ lại thanh stats, giải phóng 35px-40px chiều cao cực kỳ quý giá cho thiết bị di động.
2. **Khắc phục triệt để đè lấp ở màn hình cực hẹp (<360px):**
   - Giảm padding ngang của `.targets-container` từ 20px xuống 10px (hoặc 6px cho màn hình <360px).
   - Thiết lập media query `@media (max-width: 360px)` để co nhỏ xếp bài `.deck-container` xuống 140px và các hộp mục tiêu `.target-box` xuống 45px, mở rộng khoảng cách an toàn (gap) lên đến 39px, ngăn ngừa mọi khả năng chồng đè.
3. **Thoát an toàn khi thất bại (No-Trapping UX):**
   - Tích hợp thêm nút "QUAY LẠI ẢI" (Exit) trên màn hình Thất bại (Failure Screen) ở cả hai minigames.
   - Thêm hàm `exitMinigame()` gửi tin nhắn `close_profile` ra ngoài iframe cha để đóng modal trượt êm ái, đảm bảo học sinh không bao giờ bị "mắc kẹt" khi rèn luyện thất bại.
4. **Hòa hợp mỹ thuật truyền thống:** Thay thế phông chữ monospace thô cứng trên thẻ bài minigame 2 và dòng feedback chữ số thành phông chữ `Philosopher` uốn lượn cổ kính của Đại Việt.
5. **Cú pháp HTML chuẩn:** Xóa bỏ thẻ đóng dư thừa `</div>` lỗi cú pháp ở dòng 624 của `minigame2.html`.

### Các tệp sửa đổi:
- `minigame.html`
- `minigame2.html`

---
---

## [Gemini] 2026-05-27 — Tinh Chỉnh Thu Nhỏ Thẻ Bài Phân Biệt Số

Tài liệu này đề xuất phương án tinh chỉnh bổ sung để thu nhỏ triệt để thẻ bài game phân biệt số/chữ số, khắc phục hiện tượng thẻ bài tràn viền và lỗi đè chữ trên các máy điện thoại di động thực tế.

### Chi tiết giải pháp:
1. **Khóa chống móp méo tỉ lệ (Aspect Ratio Locked):** Thêm `flex-shrink: 0` vào `.card-container` để ngăn trình duyệt tự động ép bóp chiều cao của thẻ khi chạy trong không gian iframe chật hẹp, giữ nguyên tỉ lệ thiết kế 0.72 đẹp đẽ.
2. **Thu nhỏ triệt để thẻ bài:**
   - Trên màn hình dưới 420px: Giảm kích thước thẻ bài xuống còn **215px x 295px** (rất nhỏ gọn) và cỡ chữ số `.number-display` xuống **75px**.
   - Trên màn hình dưới 360px: Giảm kích thước thẻ bài xuống còn **190px x 260px** và cỡ chữ số xuống **65px**, đảm bảo khoảng trống lề (margin) hai bên luôn đạt mức an toàn >40px.
3. **Giải quyết đè kích thước chữ số trên thẻ bẫy (Trick Card):** Khắc phục lỗi inline style `font-size: 120px` cứng nhắc trên thẻ bẫy. Thay thế bằng các class CSS chuyên biệt `.trick-text` và `.trick-number` để tự động scale cỡ chữ bẫy và cỡ chữ số tương ứng với kích thước thẻ bài thu nhỏ.
4. **Hệ thống ẩn header 100% bằng CSS:** Thay thế đoạn script JS bằng quy tắc CSS `@media` ẩn `.header h1` trực tiếp khi chiều rộng màn hình dưới 420px hoặc chiều cao dưới 680px, mang lại độ tin cậy tuyệt đối và không tốn chi phí render JS.

---
---
