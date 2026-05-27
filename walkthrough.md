## [Gemini] 2026-05-27 — Làm mới Hồ sơ cá nhân và nút Thoát

Tôi đã hoàn thành xuất sắc toàn bộ yêu cầu làm sạch trang bản đồ, nâng cấp toàn diện giao diện Trang quản lý cá nhân (`profile.html`) sang ngôn ngữ thiết kế truyền thống Đại Việt, sửa lỗi treo màn hình tải và bổ sung nút "Thoát" thông minh theo yêu cầu!

### 1. 🏅 Cải Tiến & Dọn Sạch Trang Bản Đồ (`map.html`)
*   **Tinh giản tuyệt đối Header:** Xóa bỏ toàn bộ các nút bấm phụ, văn bản và nhãn thừa trong `.header`. Chỉ giữ lại duy nhất vùng chứa ảnh đại diện của nhân vật (`#avatarContainer` chứa `#headerAvatar`).
*   **Căn lề góc phải chuẩn chỉ:** Sử dụng cơ chế bố cục Flexbox (`justify-content: flex-end`) giúp avatar được căn chỉnh sang góc trên bên phải màn hình một cách sang trọng, gọn gàng.
*   **Liên kết Hồ sơ cá nhân mượt mà:** Khi học sinh bấm vào ảnh đại diện này, hàm `openProfile()` được kích hoạt, tải trang `profile.html` bên trong khung nhìn trượt (`iframeWindow`) của bản đồ một cách trực quan.
*   **Bổ sung cơ chế đóng nhanh:** Tích hợp bộ lắng nghe sự kiện `close_profile` để tự động đóng trang cá nhân trượt khi nhận tín hiệu từ iframe con.

### 2. 🎨 Thay Đổi Diện Mạo Hồ Sơ Cá Nhân (`profile.html`) Theo Phong Cách Đại Việt
Toàn bộ trang cá nhân đã được "lột xác", loại bỏ hoàn toàn các dải màu xanh neon và hồng tím Cyberpunk cũ để khoác lên mình dải màu truyền thống Việt Nam quý phái, hoài cổ:
*   **Hệ màu truyền thống cổ kính:**
    - **Nền Mực Tàu (`#080502`):** Mang lại chiều sâu lịch sử oai hùng.
    - **Kim loại Vàng Gold (`#C8960C`):** Màu chủ đạo tinh tế cho tiêu đề chính, các đường viền và nhãn nổi bật.
    - **Đỏ Son (`#C0332E`):** Sử dụng làm điểm nhấn cho nút bấm nổi bật, giới tính Nữ và các trạng thái quan trọng.
    - **Đồng Đông Sơn cổ kính (`rgba(184, 115, 51, 0.3)`):** Làm đường viền và các họa tiết lưới ngầm của nền.
    - **Ngà Voi (`#D4C4A0`):** Cho toàn bộ phông chữ mô tả để hiển thị dịu mắt, dễ đọc.
*   **Cân đối thiết kế:** Đồng bộ phông chữ `Philosopher` cho tiêu đề và `Lora` cho biểu mẫu. Khung cắt ảnh (Cropper) và các thẻ chọn nhân vật (**Lạc Tướng**, **Đạo Sĩ**, **Nỏ Thần**, **Thần Tướng**) đổi sang hiệu ứng bóng sáng ấm hoàng gia thay cho ánh sáng xanh Cyberpunk.

### 3. 🚪 Bổ Sung Nút "Thoát" (Exit Button) & Tối Ưu Trải Nghiệm Người Dùng
*   **Bố cục song hành tại Thanh thao tác:** Thiết kế nút **🚪 THOÁT** (màu Đỏ Son viền mảnh cổ điển) đặt ngay bên cạnh nút **💾 LƯU HỒ SƠ** (gradient Vàng - Đỏ hoàng kim oai hùng) trong thanh điều hướng cố định dưới chân trang (`.save-bar`).
*   **Đóng trang đa ngữ cảnh thông minh:** Lập trình hàm `exitProfile()` tự động kiểm tra phương thức hiển thị:
    - Nếu được mở dưới dạng **iframe trượt** trong Bản đồ chính: Gửi tín hiệu `close_profile` ra ngoài qua `window.parent.postMessage` để bản đồ tự động đóng khung nhìn một cách êm ái.
    - Nếu được mở dưới dạng **trang độc lập**: Tự động chuyển hướng mượt mà về trang bản đồ `/map`.

### 4. 🐛 Khắc Phục Lỗi Cấu Trúc HTML Treo Màn Hình Tải (Loading Bug)
*   **Phát hiện:** Trước đó, trong tệp HTML của trang cá nhân thiếu thẻ mở `<div class="wrap" id="mainContent">` mặc dù có thẻ đóng ở cuối, khiến trình duyệt bị crash lỗi `TypeError` khi chạy JavaScript đóng màn hình chờ Loading (`loadOverlay`).
*   **Khắc phục:** Đã bổ sung chính xác thẻ mở `mainContent` ôm trọn nội dung trang. Hiện tại, trang cá nhân tải dữ liệu siêu nhanh, tắt màn hình Loading và hiển thị biểu mẫu trơn tru chỉ trong tích tắc!

---
---

## [Claude] 2026-05-27 — Cập nhật cốt truyện Ải 1

**File sửa:** `map.html`

**Thay đổi 1 — Card Ải 1 trên bản đồ (dòng 387-396):**
- `open_` param: `'Bản thiết kế thành Cổ Loa'` → `'Rèn Giáp Cho Thánh Gióng'`
- `.card-title`: `Bản thiết kế thành Cổ Loa` → `Rèn Giáp Cho Thánh Gióng`

**Thay đổi 2 — Intro modal (dòng 467-473):**
- Title: `Ải 1: Truy tìm chúa tể` → `Ải 1: Rèn Giáp Cho Thánh Gióng`
- Story: Thay toàn bộ text cũ (Boss Số Thần) bằng cốt truyện Thánh Gióng + Quỷ Số
- Mission: `Rèn 1 Tuyệt Chiêu` → `Rèn 2 Tuyệt Chiêu bên dưới`

---
---

## [Claude] 2026-05-27 — Sửa giao diện minigame.html (Tuyệt Chiêu 1: Phân Biệt Số & Chữ Số)

**File sửa:** `minigame.html`

**Lý do:** Commit `8f350df` (Gemini) đã thay text mini-game từ "Phân Biệt Số & Chữ Số" sang "Ải 1: Bản thiết kế thành Cổ Loa" (lỗi chủ đề). Phiên Claude trước đã thử sửa nhưng mất context trước khi commit. Phiên này tiếp tục sửa.

**Thay đổi chi tiết:**
- **Tab title** (dòng 6): `"Ải 1: Bản thiết kế thành Cổ Loa — Chiến Binh Toán"` → `"Tuyệt Chiêu 1: Phân Biệt Số & Chữ Số — Chiến Binh Toán"`
- **Header h1 CSS** (dòng 60-68): Thêm `font-size: clamp(14px, 4vw, 22px)` và `line-height: 1.3` để tránh text dài bị wrap thành ký tự "/" đơn lẻ trên mobile
- **Game header h1** (dòng 472): `"Ải 1: Bản thiết kế thành Cổ Loa"` → `"Rèn Tuyệt Chiêu 1 — Phân Biệt Số & Chữ Số"` (dùng "—" thay "/" làm separator)
- **Start screen h1** (dòng 444): `"ẢI 1: BẢN THIẾT KẾ THÀNH CỔ LOA"` → `"RÈN TUYỆT CHIÊU 1 / Phân Biệt Số & Chữ Số"` — font đổi sang `var(--font-title)`
- **Start screen story** (dòng 447-448): `"An Dương Vương / Loa Thành"` → `"Quỷ Số / Thánh Gióng"` cho khớp chủ đề Ải 1
- **Win screen** (dòng 572-577): Text "Bản thiết kế thành Cổ Loa đã được khôi phục" → "Tuyệt chiêu đã rèn xong! Thánh Gióng sắp có giáp ra trận!"
- **Fail screen** (dòng 585-586): Text "Bản thiết kế chưa hoàn thiện" → "Tuyệt chiêu chưa rèn xong! Quỷ Số còn ngự trị!"
- **Fail background** (dòng 582): `'assets/boss_so_than_portrait.jpg'` (file không tồn tại) → `'design-system/characters/boss/ho-tinh-portrait.jpg'` (file hợp lệ)
- **Fonts**: Thay `'Chakra Petch', sans-serif` (không được load) → `var(--font-title)` nhất quán

---
---

## [Gemini] 2026-05-27 — Sửa lỗi F5 bị hiển thị Avatar cũ trên trang Bản đồ

**File sửa:** `map.html`

*   **Đồng bộ DB vào localStorage:** Cập nhật hàm `authGate()` để tự động ánh xạ nhân vật (`character_type`) và giới tính (`gioi_tinh`) tải về từ cơ sở dữ liệu thành chuỗi đại diện (ví dụ: `chien_binh` + `nam` = `lac-tuong-male`) và ghi đè vào `localStorage` dưới khóa `vsSelectedChar`.
*   **Hàm toàn cục loadSelectedCharacter:** Chuyển đổi hàm tải avatar từ IIFE tự thực thi thành một hàm toàn cục có thể gọi lại nhiều lần và chấp nhận tham số ghi đè (`charOverride`).
*   **Cập nhật giao diện lập tức:** Gọi hàm `loadSelectedCharacter(mappedChar)` ngay khi nhận phản hồi phê duyệt (`approved`) từ DB trong `authGate()`, giúp hiển thị chính xác avatar mới nhất dù người dùng nhấn F5/Reload trang bản đồ.

---
---

**Lý do:** Chuyển bối cảnh Ải 1 từ Cổ Loa/Số Thần sang Thánh Gióng/Quỷ Số theo kịch bản mới. Boss đổi tên cho dễ hiểu với học sinh lớp 3.
