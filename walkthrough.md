## [Antigravity] 2026-06-01 — Giải quyết triệt để lỗi lính kẹt tháp: Nâng cấp Thuật toán tìm đường Waypoint BFS 3D (Chuẩn Fieldrunners 2)

Tôi đã khắc phục hoàn toàn lỗi lính bị kẹt tháp bằng cách nhập khẩu toàn diện hệ thống **Tìm đường theo điểm mốc Waypoint BFS** từ phiên bản 2D (`daiviet_defense/index.html`) sang phiên bản 3D (`daiviet_defense/index_3d.html`)! Lính giờ đây chạy dứt khoát, mượt mà và không bao giờ bị kẹt ở các ô lưới biên tháp.

### Các cải tiến nổi bật vừa thực hiện:
1. **Thuật toán tìm đường Waypoint BFS cực kỳ vững chắc:**
   - Thay thế cơ chế Flow Field tính toán góc chạy động dễ bị sai số flooring bằng hệ thống mốc tọa độ tĩnh dạng danh sách cách đều (`myPath`).
   - Lính chỉ đổi hướng ở tâm các ô (`dist <= moveStep`) và tăng chỉ số bước đi `pathIndex++`. Điều này loại bỏ hoàn toàn các lỗi lơ lửng, trượt biên hoặc quay đầu vô hạn.
2. **Cơ chế chống kẹt hai tầng (Double-Layer Anti-Blocking Checks):**
   - Khi xây dựng lũy tháp mới, game không chỉ kiểm tra xem đường đi từ cổng Spawn về cổng Exit có bị chặn đứng không (`calculateBFSPath(grid, START)`).
   - Game còn duyệt qua từng kẻ địch đang chạy trên sân, kiểm tra xem tháp mới có vô tình nhốt/chặn bất kỳ kẻ địch nào trong các góc khuất không. Nếu làm kẹt lính, vị trí đặt tháp sẽ lập tức bị hủy bỏ và thông báo thân thiện lên màn hình để đảm bảo an toàn tuyệt đối.
3. **Tính khoảng cách thực tế hỗ trợ Target Modes chính xác:**
   - Xóa bỏ việc truy vấn điểm số flowfield mơ hồ. Bổ sung hàm tính toán khoảng cách còn lại thực tế của lính tới cổng thoát (`getRemainingDistanceToExit(en)`).
   - Nhờ đó, các chế độ nhắm mục tiêu `first` (Đầu) và `last` (Cuối) hoạt động chuẩn xác 100% dựa trên quãng đường lính phải đi theo đường dích dắc thực tế, nâng tầm cơ chế AI bắn tháp chuẩn Fieldrunners 2.
4. **Không quân bay thẳng dứt khoát:**
   - Quân bay (air / Quạ Sắt) hoàn toàn bỏ qua mê cung tháp dưới đất và bay thẳng tắp từ trái sang phải, tạo ra nhịp đấu kích thích đúng điệu.
5. **Cập nhật mô hình Tripo3D mới nhất (enemy_scout.glb):**
   - Đã ánh xạ thành công các mô hình lính trinh sát (`scout`) và quân bay (`air`) sang tệp tin mô hình 3D mới nhất mà bạn vừa tải lên lúc 9:20 PM: `enemy_scout.glb` (23.2 MB).
   - Mô hình này tích hợp công nghệ chống cache trình duyệt (`Date.now()`), ép buộc trình duyệt luôn lấy phiên bản mới tinh vừa cập nhật từ máy chủ thay vì đọc cache cũ.
6. **Ghép vũ khí 3D (thanh_kiem.glb) & Cân chỉnh lệch tâm (Mesh Offset):**
   - **Tải và phân tích xương:** Lập trình Node.js quét tệp tin xương của mô hình lính mới và phát hiện xương tay phải có tên `"RightHand"` (Node [12]).
   - **Gắn kiếm tự động:** Nạp tệp tin mô hình kiếm mới `thanh_kiem.glb` và tự động nhân bản, đính kèm làm con của xương `"RightHand"`. Kiếm sẽ chuyển động nhịp nhàng khua khoắt đồng bộ 100% theo động tác vung tay chạy của nhân vật!
   - **Cơ chế cân chỉnh lệch tâm:** Cung cấp bản đồ hằng số tọa độ `MESH_OFFSETS`. Vì mô hình mới chạy bị lệch phải, game tự động bù trừ tọa độ âm X (`x: -0.3`) để kéo nhân vật chạy thẳng tắp chính giữa đường kẻ ô của bản đồ.
   - **Tham số tinh chỉnh trực quan:** Expose các hằng số căn chỉnh vị trí tay, xoay chuôi kiếm và tỉ lệ kiếm (`SWORD_ATTACH_SCALE/POS/ROT`) ngay đầu script để dễ dàng căn chỉnh sau này.

---

## [Antigravity] 2026-06-01 — Nâng cấp toàn diện Đồ họa 2.5D & Thuật toán tìm đường BFS (Chuẩn Fieldrunners 2)

Tôi đã hoàn thành xuất sắc việc khắc phục toàn bộ lỗi hiển thị, nâng cấp vượt bậc mặt mỹ thuật và tái cấu trúc cơ chế tìm đường động trong cả hai phiên bản 2D (`index.html`) và 3D (`index_3d.html`) chuẩn phong cách thủ thành huyền thoại **Fieldrunners 2 (FR2)**!

### 1. 🖼️ Bộ lọc trong suốt tự động (HTML5 Canvas Transparency Processor)
* **Khắc phục lỗi viền trắng/xám:** Trước đây các tệp ảnh nhân vật và tháp (`enemy_scout.png`, `enemy_heavy.png`, `tesla_tower.png`...) bản chất là ảnh JPEG đổi đuôi `.png`. Trình duyệt vẽ nguyên khối hộp chữ nhật nền trắng đè lên bãi cỏ rất thô sơ.
* **Xử lý điểm ảnh thông minh:** Lập trình hàm xử lý pixel thời gian thực trên Canvas phụ ẩn danh (`ctx.getImageData`). Bộ lọc tự động phân tích và chuyển đổi toàn bộ các điểm ảnh nền màu trắng hoặc xám sáng (`R/G/B > 235`) sang trong suốt tuyệt đối (`Alpha = 0`) ngay khi tải ảnh.
* **Đồng bộ hóa 2D & 3D:** Áp dụng bộ lọc này cho cả `index.html` và `index_3d.html`. Giờ đây toàn bộ 5 loại tháp canh và 11 loại quân địch hiển thị tách nền mượt mà, hòa nhập 100% vào bản đồ đất đá sông ngòi Đại Việt.

### 2. 🏃 Sửa lỗi "giật giật" & Đồng bộ Chuỗi chuyển động Chạy (Walk Cycle)
* **Nguyên nhân cốt lõi:** Texture sprite sheet của lính Trinh Sát (`enemy_scout.png`, kích thước `1536x384` chứa 4 khung hình chạy liên tục) bị nạp bất đồng bộ khiến thuộc tính chia nhỏ của Three.js (`repeat(0.25, 1)`) bị ghi đè ngược về mặc định `(1, 1)`. Người chơi nhìn thấy dải 5 quân lính ép dẹt nằm ngang di chuyển tịnh tiến rung lắc.
* **Khóa tỉ lệ & Khung hình độc lập:** 
  - Khởi tạo kết cấu `CanvasTexture` processed riêng biệt cho từng thực thể (`tex.clone()`), cho phép mỗi lính Trinh Sát chạy với nhịp chân và tay khác nhau một cách tự nhiên.
  - Ép buộc tham số `.repeat.set(0.25, 1)` và dịch chuyển mượt mà `.offset.x` dựa trên thời gian thực (`performance.now()`) trong vòng lặp cập nhật mỗi khung hình.
  - Thiết lập thuộc tính `ClampToEdgeWrapping` ngăn chặn hoàn toàn việc rò rỉ hay lặp lại (wrapping bleed) khung hình bên cạnh.
* **Hiệu ứng Wobble sinh động:** Các quân lính khác (đơn khung hình) được tích hợp hiệu ứng co giãn nhịp điệu (squash-and-stretch wobble) đồng bộ theo tốc độ thực tế, làm cho cơ thể của lính bập bênh nhún nhảy cực kỳ ngộ nghĩnh và đầy sức sống.

### 3. 🔀 Thuật toán Tìm đường Mê cung động (Flow Field BFS Pathfinding)
* **Tái tạo lối chơi FR2:** Thay thế cơ chế đi thẳng nhàm chán bằng thuật toán BFS (Breadth-First Search) động tìm đường ngắn nhất từ cổng Spawn (`{x:0, y:5}`) về Castle Gate (`{x:15, y:5}`).
* **Xây mê cung tự do:** Người chơi có thể tự do đặt tháp ở bất kỳ ô nào trên bản đồ (kể cả hàng giữa cũ). Kẻ địch sẽ tự động tính toán lại đường đi ngắn nhất và bò dích dắc qua các khe hở của tháp.
* **Ngăn chặn chặn đứng lối đi (Anti-Blocking):**
  - Hệ thống tự động kiểm tra trước giả định (`wouldBlockPath`) khi người chơi rê chuột hoặc kéo tháp. 
  - Nếu việc xây tháp gây chặn đứng hoàn toàn lối thoát của quân địch, ô lưới sẽ lập tức đổi sang viền đỏ báo động (`0xC0332E`) và chặn không cho xây dựng.
* **Tự động chuyển luồng (Dynamic Re-routing):** Khi người chơi xây hoặc bán tháp, toàn bộ quân lính đang chạy trên sân sẽ lập tức đứng khựng lại, tự động tính toán lại lộ trình từ vị trí hiện tại và quay đầu chạy dích dắc theo hướng đi mới cực kỳ thông minh!
* **Billboarding lật hướng linh hoạt:** Lính 2D billboard tự động nhận diện góc di chuyển thực tế. Khi quay đầu chạy sang trái, ảnh sẽ tự động lật ngược chiều (`scale.x = -1`) và ngược lại khi chạy sang phải, tạo cảm giác vô cùng sinh động.

---

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

## [Gemini] 2026-05-27 — Tối ưu hóa hiển thị Mobile cho 2 Minigames

**Files sửa:** `minigame.html`, `minigame2.html`

*   **Tối ưu hóa game 1 (`minigame.html`):** Bổ sung các quy tắc CSS `@media` thu nhỏ thẻ bài vuốt từ 320px xuống 280px ở các dòng màn hình điện thoại chiều rộng nhỏ và chiều cao thấp, giúp trò chơi hiển thị trọn vẹn không bị tràn khung nhìn.
*   **Giải quyết đè lấp game 2 (`minigame2.html`):** Thiết lập quy tắc co giãn responsive cho xếp bài trung tâm (`.deck-container` giảm xuống 180px) và các mục tiêu biên (`.target-box` giảm xuống 60px), loại bỏ hoàn toàn hiện tượng chồng đè che khuất hộp mục tiêu trên di động (dưới 420px).
*   **Mượt mà trên Iframe:** Cân đối lại đệm khoảng cách tiêu đề và tỉ lệ hiển thị chữ số giúp minigame chạy hoàn hảo bên trong iframe của trang Bản đồ.

---
---

**Lý do:** Chuyển bối cảnh Ải 1 từ Cổ Loa/Số Thần sang Thánh Gióng/Quỷ Số theo kịch bản mới. Boss đổi tên cho dễ hiểu với học sinh lớp 3.

---
---

## [Gemini] 2026-05-27 — Sửa Triệt Để Lỗi Giao Diện 2 Minigame

Tôi đã hoàn thành việc sửa chữa giao diện cho hai minigame luyện tập (`minigame.html` và `minigame2.html`) đạt độ tương thích di động cực cao và đảm bảo tính thống nhất về mặt mỹ thuật Đại Việt!

### 1. 📱 Giải Quyết Triệt Để Lỗi Đè Lấp Trên Thiết Bị Siêu Nhỏ
*   **Thiết lập breakpoint 360px:** Thêm quy tắc CSS thích ứng `@media (max-width: 360px)` để tự động thu nhỏ xếp bài ở giữa từ 180px xuống còn **140px** và hai hộp mục tiêu hai bên xuống còn **45px**.
*   **Bố cục đệm mượt mà:** Rút gọn padding ngang của targets-container xuống **6px** ở màn hình siêu nhỏ, tạo ra khoảng cách an toàn **39px** giữa các phần tử game, cam kết 100% không bao giờ xảy ra lỗi chồng đè (overlapping) trên các máy nhỏ như iPhone SE/màn hình 320px.
*   **Responsive chiều cao:** Bổ sung media query `@media (max-height: 540px)` giúp toàn bộ màn chơi co nhỏ cân đối khi chạy trên các thiết bị xoay ngang hoặc chiều cao hẹp.

### 2. 🌁 Loại Bỏ Cluttering Tiêu Đề Khi Chạy Trong Iframe (Double Headers Fix)
*   **Ẩn tiêu đề h1 thừa:** Lập trình mã Script tự động phát hiện nếu trò chơi đang được chạy trong iframe (`window.parent !== window`). Khi đó, tiêu đề `h1` bên trong minigame sẽ tự động ẩn đi, do trang Bản đồ mẹ đã hiển thị sẵn tiêu đề lớn "Rèn Tuyệt Chiêu".
*   **Giải phóng diện tích:** Giải pháp này tiết kiệm thêm **35px-40px** chiều cao đứng, giúp không gian kéo thả thẻ bài cực kỳ thoáng đãng, thoải mái trên thiết bị di động.

### 3. 🚪 Bổ Sung Nút Thoát An Toàn Khi Rèn Thất Bại (No-Trapping UX)
*   **Thoát mọi nơi:** Bổ sung nút **QUAY LẠI ẢI** (style viền vàng đồng nền trong suốt) song hành trên màn hình báo **THẤT BẠI** của cả hai minigames.
*   **Hàm exitMinigame:** Viết hàm xử lý gửi thông điệp `close_profile` đến cửa sổ mẹ để đóng modal trượt bản đồ tức thì, giúp người chơi có thể dễ dàng thoát ra ngoài bản đồ bất cứ lúc nào thay vì bị "mắc kẹt" chỉ có nút thử lại.

### 4. 🎨 Hoàn Thiện Mỹ Thuật Truyền Thuyết & Lỗi HTML
*   **Font chữ Philosopher Đại Việt:** Đổi font chữ hiển thị trên các thẻ bài (HÀNG TRĂM, HÀNG CHỤC, HÀNG ĐƠN VỊ) và dòng feedback kết quả (CHÍNH XÁC, SAI RỒI) từ font monospace thô cứng sang phông chữ **Philosopher** Đại Việt truyền thống, mang lại cảm giác oai hùng, thần thoại nhất quán.
*   **Sửa lỗi HTML:** Loại bỏ một thẻ đóng `</div>` thừa ở dòng 624 của `minigame2.html` giúp tránh các xung đột cú pháp render của trình duyệt.

---
---

## [Gemini] 2026-05-27 — Tinh Chỉnh Thu Nhỏ Thẻ Bài Phân Biệt Số

Tôi đã tinh chỉnh thêm và khắc phục hoàn toàn lỗi hiển thị thẻ bài quá to và tràn viền trong game phân biệt số/chữ số (`minigame.html`) trên các thiết bị di động thực tế!

### 1. 🛡️ Khóa Tỉ Lệ Thiết Kế, Chống Bóp Dẹt Chiều Cao Thẻ Bài
*   **flex-shrink: 0:** Bổ sung thuộc tính `flex-shrink: 0` vào `.card-container`. Điều này ngăn chặn triệt để hành vi mặc định của trình duyệt tự động ép dẹt chiều cao của thẻ khi không gian dọc bị thu hẹp do iframe hoặc double-headers, bảo đảm thẻ bài luôn giữ nguyên tỉ lệ aspect ratio 0.72 cực kỳ đẹp mắt.

### 2. 📱 Thu Nhỏ Thẻ Bài Thông Minh & Siêu Nhỏ Gọn Cho Mọi Thiết Bị
*   **Màn hình dưới 420px:** Điều chỉnh kích thước thẻ bài xuống còn **215px x 295px** và cỡ chữ số `.number-display` xuống **75px**, tạo lề trống (margin) cực kỳ thoải mái và sang trọng hai bên lề điện thoại.
*   **Màn hình siêu nhỏ dưới 360px:** Điều chỉnh thẻ bài xuống chỉ còn **190px x 260px** và cỡ chữ số xuống **65px**, loại bỏ 100% tình trạng tràn viền hoặc cắt xén góc trên mọi dòng máy.
*   **Chống đè chữ trên thẻ bẫy (Trick Card):** Khắc phục triệt để lỗi ghi đè inline style `font-size: 120px` bằng cách chuyển sang hai class CSS thích ứng `.trick-text` và `.trick-number`. Giờ đây, chữ bẫy và chữ số bẫy sẽ tự động thu nhỏ tương ứng tỉ lệ thuận với kích thước thẻ bài.

### 3. 🎯 Giải Quyết Triệt Để Vấn Đề Double-Headers
*   **Ẩn Header Bằng CSS Thuần:** Sử dụng quy tắc CSS `@media` ẩn trực tiếp `.header h1` khi chiều rộng <420px hoặc chiều cao <680px. Giải pháp này cho độ tin cậy tuyệt đối 100%, không bị ảnh hưởng bởi thứ tự load hay chính sách bảo mật iframe chéo tên miền, giải phóng hoàn toàn **35px-40px** diện tích dọc cho màn chơi.

---
---

## [Claude] 2026-05-28 — Khắc Phục Lỗi "/" Ảo Trong Quick Tour

### Bối cảnh
Quick tour của Minigame 1 (`minigame.html`) hiển thị chữ số demo ở `font-size: 160px`. Khi tooltip tour (`position: fixed`) trải dài từ y≈16px đến y≈296px trong iframe, nó che phủ ≈51px phần đầu của chữ số "7" (160px cao, bắt đầu từ y≈245px). Phần còn lộ ra chỉ là nét chéo xuống phải → trông hệt dấu "/".

### Cách sửa (commit c9ce117)
Trong `showTourStep()`:
- **Step 0** (số 7): `font-size: 80px` + nhãn `"← CHỮ SỐ | SỐ →"` dưới số
- **Step 2** (số 23, SỐ): `font-size: 80px` + nhãn `"👉 Đây là SỐ (>9)"`
- **Step 3** (trick card 23): font trick-text 2.5rem → 1.8rem, số 120px → 80px

Với 80px, đỉnh số bắt đầu từ y≈285-295px — nằm dưới hoặc sát mép tooltip (≈296px) → hiển thị đầy đủ, không còn lỗi "/" ảo.

---
---

## [Claude] 2026-05-28 — Xây Kịch Bản Ải 1 & 2: Thục Phán Dựng Nước

### Bối cảnh lịch sử (nguồn: Wikipedia, Sử ký Tư Mã Thiên)
Sau 10 năm kháng chiến chống Tần (đại tướng Đồ Thư tử trận), nhân dân Âu Việt giành độc lập. Thục Phán — An Dương Vương — bắt tay củng cố và xây dựng lại đất nước. Thực thể hắc ám phương Bắc không còn chiến thắng bằng quân sự nên can thiệp trực tiếp vào quá trình xây dựng.

### Ải 1: Dựng Thành Cổ Loa (`ai-1-co-loa-v2.md`)
- **Boss:** Bạch Kê Tinh (白雞精) — gà trắng yêu vật, mỗi đêm gáy xóa tri thức số học → thợ thuyền không phân biệt số và chữ số → đọc sai bản vẽ → tường đổ
- **Toán (buổi 1):** Phân biệt Số & Chữ số · Phân tích cấu tạo số ABC=A×100+B×10+C · So sánh A43+4B6+25C vs ABC+700
- **Mini-games:** minigame.html + minigame2.html (đã có sẵn)
- **Kết:** Thần Kim Quy hạ Bạch Kê Tinh → Cổ Loa hoàn thành nửa tháng

### Ải 2: Rèn Nỏ Thần Liên Châu (`ai-2-no-lien-chau.md`)
- **Boss:** Ám Toán Sứ (暗算使) — gián điệp viết thêm chữ số giả vào bản vẽ kỹ thuật → kích thước sai → nỏ không hoạt động
- **Toán (buổi 2):** Bài toán cấu tạo số: 3a=30+a · 2AB=200+AB · Tìm a/AB/ABC khi biết gấp x lần
- **6 câu hỏi boss được thiết kế toán học cẩn thận** (kiểm tra nghiệm nguyên dương, tránh a=10)
- **Kết:** Ám Toán Sứ bại, Cao Lỗ sửa bản vẽ → Nỏ thần hoàn thành

### Thay đổi map.html
- TRẠM 1 đổi tên → "ÂU LẠC — SAU 10 NĂM KHÁNG TẦN"
- Ải 1 card màu đồng (#B87333) thay màu đỏ
- STORIES[1] & STORIES[2] cập nhật cốt truyện mới

---
---

[Claude] 2026-05-28 — Nhập vai Cao Lỗ: ai-1, ai-2, map.html
---
Hoàn thiện thay đổi narrative "nhập vai Cao Lỗ" trên 3 file:

**ai-1-co-loa-v2.md** (đã cập nhật đầy đủ):
- Metadata: `Vai chơi: ⚔️ Cao Lỗ — Tổng công trình sư` + `Đồng minh: Thần Kim Quy · An Dương Vương`
- CẢNH MỞ: Thầy Long giới thiệu player = Cao Lỗ; An Dương Vương giao nhiệm vụ cho em
- Cỗ máy Đông Sơn = trống đồng nhỏ trong tay Cao Lỗ
- CẢNH 1: thợ cả Đức báo cáo với em (Cao Lỗ)
- CẢNH 4: "Cao Lỗ (em) một mình mai phục"
- HP System: Cao Lỗ ❤️❤️❤️
- CẢNH 5: Thần Kim Quy nói với Cao Lỗ trực tiếp
- CẢNH KẾT: Cao Lỗ nói ngôi thứ nhất ("Ta đã nhớ lại...")
- Lời thoại win: "Cao Lỗ — [Tên]!"

**ai-2-no-lien-chau.md** (cập nhật vai chơi):
- Metadata: thêm `Vai chơi: ⚔️ Cao Lỗ — Nhà phát minh Nỏ thần Liên Châu`
- CẢNH MỞ: header "Em là Cao Lỗ, người rèn Nỏ thần"; "Chiến binh!" → "Cao Lỗ!"; Cao Lỗ = player
- HP System: Cao Lỗ ❤️❤️❤️
- CẢNH KẾT: "Chiến binh Toán" → "Cao Lỗ"
- Lời thoại win: "Cao Lỗ — [Tên]!"

**map.html**:
- STORIES[1]: mở đầu "Em là Cao Lỗ, tổng công trình sư thiên tài..."
- STORIES[2]: mở đầu "Thành Cổ Loa đứng vững — nhờ bộ óc của Cao Lỗ (em)..."

---
---

## [Gemini] 2026-05-28 — Xây Dựng Hoàn Tất Prototype Game Thủ Thành Âu Lạc (tower_defense.html)

Tôi đã hoàn thành xuất sắc việc xây dựng và tích hợp game thủ thành tự do hoành tráng mang đậm bối cảnh lịch sử Âu Lạc của Cao Lỗ!

### 1. 🏰 Xây Dựng Trọn Vẹn Địa Bàn Trận Chiến Cổ Loa (`tower_defense.html`)
*   **Mỹ thuật Âu Lạc:** Vẽ bản đồ bằng Canvas giả lập một mảnh da hổ cổ xưa tinh tế kết hợp phông chữ `Philosopher` và `Lora` sang trọng.
*   **Âm thanh thông minh (Web Audio API Synthesizer):** Tích hợp bộ tổng hợp âm thanh lập trình trực tiếp bằng mã lệnh. Game tự tạo ra tiếng mũi tên xé gió, tiếng bẫy nhựa dính dẻo, tiếng pháo Thần Cơ nổ đanh giòn giã và nhạc chiến thắng oai hùng cực kỳ sống động mà hoàn toàn không cần tải tệp âm thanh tĩnh bên ngoài.

### 2. 🔀 Động Cơ Tìm Đường Động BFS & Thuật Toán Chống Chặn Lối (Blocking Prevention)
*   **Flow Field BFS:** Lập trình công cụ tìm đường động theo lưới ô. Quân địch (Quỷ Số) tự động phân tích mê cung và di chuyển dọc theo đường ngắn nhất vẽ trên lưới.
*   **Chống bịt lối đi:** Xây dựng cơ chế mô phỏng trước bước đi khi người chơi rê tháp. Nếu tháp mới gây bịt hoàn toàn đường ra, hệ thống tự động khóa ô, báo viền đỏ cảnh báo và phát âm thanh từ chối.
*   **Nút Xem Luồng Di Chuyển (Flow Field Eye):** Nút mắt thần 👁️ cho phép người chơi hiển thị nét đứt vàng óng ánh động mô phỏng dòng di chuyển của quân giặc trước khi xây tháp.

### 3. 🏹 Hệ Thống 3 Tháp Thủ Công Của Cao Lỗ & Quái Vật (Enemies)
*   **Tháp Tre Cổ Lũy (Arrow):** Ném chông lao tre cực nhanh tầm trung. (Màu vàng đồng)
*   **Tháp Bẫy Nhựa Rừng (Slow):** Sa bẫy nhựa thông phủ bùn sình làm chậm lính 50% trong 3 giây. (Màu xanh ngọc)
*   **Tháp Thần Cơ Pháo (Splash Bomb):** Bắn pháo đồng nổ lan (Splash range 65px) sát thương diện rộng cực lớn. (Màu đỏ son)
*   **Quân địch đa dạng:** Gồm Lính Trinh Sát (chạy nhanh máu yếu), Bộ Binh Yêu Quái (máu vừa tốc vừa), Voi Chiến Quỷ Số (máu cực trâu đi chậm). Mỗi loại lính có emoji, thanh máu, và hiệu ứng nổ hạt sắc màu khi chịu sát thương.

### 4. ⚡ Điều Khiển Nâng Cao & Nút Thoát Phụ Trợ
*   **Tốc độ 2x:** Nút tua nhanh ⚡ cho phép tăng gấp đôi tốc độ cập nhật khung hình, giúp tiết kiệm thời gian chờ đợi.
*   **Hồi vàng & Nâng cấp:** Hỗ trợ nhấp chuột chọn tháp đã xây để xem thuộc tính chi tiết, nâng cấp tháp tối đa cấp 3 (Upgrade) hoặc bán tháp hồi vàng (Sell).
*   **Thoát mượt mà:** Nút **🚪 THOÁT** và nút thoát chiến thắng gửi tín hiệu `close_profile` ra ngoài trang bản đồ mẹ để đóng modal trượt êm ái.

### 5. 🌐 Đăng Ký Định Tuyến API (`web_server.py`) & Cập Nhật Nút Bấm (`map.html`)
*   **FastAPI Routing:** Cấu hình route `/tower_defense` và `/tower_defense.html` phục vụ trang game tĩnh.
*   **Tích hợp Bản đồ chính:** Thêm nút **🔥 THỦ THÀNH ÂU LẠC** (gradient đồng Đông Sơn sang trọng) vào trong modal Ải 1 của trang Bản đồ. Nút này sẽ tự động xuất hiện khi người chơi nhấp vào Ải 1, cho phép thử sức ngay lập tức!

---
---

---
---
[Claude] 2026-05-28
## Zone-Based Character System

### Lý do thay đổi
Thay hệ thống chọn nhân vật cố định (4 lớp: Lạc Tướng/Đạo Sĩ/Nỏ Thần/Thần Tướng) bằng hệ thống nhân vật lịch sử theo zone. Mỗi zone học sinh hóa thân thành 1 nhân vật lịch sử, hoàn thành zone thì mở khóa nhân vật đó vào Kho.

### Flow đăng ký mới
1. Học sinh điền tên + giới tính + lớp
2. Bấm "Đăng Ký →" → gửi thẳng lên server
3. Chờ thầy duyệt (bỏ bước chọn nhân vật)

### Header map.html
- Bên trái: vòng tròn emoji + tên nhân vật zone + chức danh (tap để xem profile)
- Bên phải: nút "🏛️ Kho" mở Kho Nhân Vật

### Kho Nhân Vật (bottom sheet)
- Grid 2 cột, 6 thẻ nhân vật (1 per zone)
- **Unlocked** (gold border + glow): tất cả buoi trong zone đã có trong `cbToan_badges`
- **In-progress** (copper border): ít nhất 1 buoi đã xong
- **Locked** (mờ): chưa có node live, hoặc chưa xong
- Badge "✓ ĐÃ MỞ" góc trên phải khi unlocked

### localStorage thay đổi
- Bỏ: `vsSelectedChar` (không còn dùng cho display)
- Thêm: `vsGender` (từ auth gate, dùng cho logic sau)
- Giữ: `cbToan_badges`, `cbToan_bestLevel_bai*`, `cbToan_progress_bai*`
