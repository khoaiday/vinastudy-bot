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
