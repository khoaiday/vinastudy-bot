## [Claude] 2026-05-30 — Tích Hợp Backend: Game Progress + Auth + Leaderboard + Bot Notification

- `[x]` 1. DB: thêm bảng `game_progress` (telegram_id, ai_num, score, stars, completed_at)
- `[x]` 2. CRUD: `get_game_progress`, `upsert_game_progress` (giữ điểm cao nhất), `get_leaderboard_progress`
- `[x]` 3. API `POST /api/student/tg-auth` — xác thực `initData` Telegram HMAC-SHA256
- `[x]` 4. API `GET /api/student/progress?tg_id=` — lấy toàn bộ ải đã hoàn thành
- `[x]` 5. API `POST /api/student/complete-ai` — lưu kết quả + cộng XP + gửi bot Telegram chúc mừng
- `[x]` 6. API `GET /api/student/leaderboard-progress` — BXH theo tổng điểm + số ải
- `[x]` 7. `map.html`: `syncProgressFromServer()` — tải tiến độ từ server, merge vào localStorage, re-render map
- `[x]` 8. `minigame.html` + `minigame2.html`: gọi `/complete-ai` khi thắng (fire-and-forget)
- `[x]` 9. Commit `3d10465` trên branch `dev`

---
---

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

## [Claude] 2026-05-28 — Xây Dựng Ải 1 & 2: Cổ Loa + Nỏ Thần (Bối Cảnh An Dương Vương)

- `[x]` 1. Tạo kịch bản Ải 1: Dựng Thành Cổ Loa (`scenarios/ai-1-co-loa-v2.md`)
  - `[x]` Bối cảnh: Thục Phán củng cố Âu Lạc sau 10 năm kháng Tần (~210 TCN)
  - `[x]` Boss: Bạch Kê Tinh — tiếng gáy xóa tri thức số học, tường Cổ Loa cứ đổ
  - `[x]` Toán: Phân biệt số/chữ số · Phân tích cấu tạo số ABC=A×100+B×10+C · So sánh số
  - `[x]` 6 câu hỏi boss (🌱 Nhận biết → ⚔️ Giá trị → 🏹 So sánh A43+4B6+25C → 🏆 Tổng hợp)
  - `[x]` Lời thoại đầy đủ: Thầy Long · Cỗ máy Đông Sơn · Cao Lỗ · Thần Kim Quy · Bạch Kê Tinh
  - `[x]` Ngân hàng câu hỏi mở rộng (🌱⚔️🏹)
- `[x]` 2. Tạo kịch bản Ải 2: Rèn Nỏ Thần Liên Châu (`scenarios/ai-2-no-lien-chau.md`)
  - `[x]` Bối cảnh: Thần Kim Quy tặng vuốt rùa, Cao Lỗ rèn nỏ thần
  - `[x]` Boss: Ám Toán Sứ — viết thêm chữ số giả vào bản vẽ kỹ thuật
  - `[x]` Toán: Bài toán viết thêm chữ số · Tìm số ẩn 1/2/3 chữ số (3a=30+a, 2AB=200+AB)
  - `[x]` 6 câu hỏi boss (🌱 Phép viết thêm → 🌱 Giá trị cụ thể → ⚔️ Tìm a 1 c.số → ⚔️ Số 2 c.số → 🏹 Tìm AB → 🏆 Tìm ABC)
  - `[x]` Ngân hàng câu hỏi hợp lệ (kiểm tra nghiệm nguyên dương)
- `[x]` 3. Cập nhật `map.html`
  - `[x]` TRẠM 1: "THUỞ SƠ KHAI" → "ÂU LẠC — SAU 10 NĂM KHÁNG TẦN"
  - `[x]` Ải 1 card: "Rèn Giáp Cho Thánh Gióng" → "Dựng Thành Cổ Loa" · màu đồng #B87333
  - `[x]` Ải 2 card: thêm thông tin boss "📜 Ám Toán Sứ · Buổi 2", border màu đỏ
  - `[x]` STORIES[1]: cập nhật cốt truyện Bạch Kê Tinh + Cổ Loa
  - `[x]` STORIES[2]: cập nhật cốt truyện Ám Toán Sứ + Nỏ thần
- `[x]` 4. Commit & push (430f3ae)

---
---

[Claude] 2026-05-28 — Nhập vai Cao Lỗ: hoàn thiện kịch bản Ải 1 & Ải 2
---
- `[x]` Cập nhật `scenarios/ai-1-co-loa-v2.md` — học sinh nhập vai Cao Lỗ
  - `[x]` Metadata: thêm `> **Vai chơi:** ⚔️ **Cao Lỗ**`, đổi Đồng minh → Thần Kim Quy · An Dương Vương
  - `[x]` CẢNH MỞ: Thầy Long giới thiệu "em sẽ trở thành Cao Lỗ"; An Dương Vương nói chuyện với Cao Lỗ (em)
  - `[x]` CẢNH 1: Thợ cả báo cáo với Cao Lỗ (em); Cỗ máy Đông Sơn = trống đồng trong tay Cao Lỗ
  - `[x]` CẢNH 4: "Chiến binh" → "Cao Lỗ (em) một mình mai phục"
  - `[x]` HP System: "Chiến binh" → "Cao Lỗ" ❤️❤️❤️
  - `[x]` CẢNH 5: Thần Kim Quy nói với Cao Lỗ trực tiếp (không còn "Chiến binh Toán")
  - `[x]` CẢNH KẾT: Cao Lỗ nói theo ngôi thứ nhất ("Ta đã nhớ lại...")
  - `[x]` Lời thoại thắng: "Cao Lỗ — [Tên]!"
- `[x]` Cập nhật `scenarios/ai-2-no-lien-chau.md` — học sinh nhập vai Cao Lỗ
  - `[x]` Metadata: thêm `> **Vai chơi:** ⚔️ **Cao Lỗ** — Nhà phát minh Nỏ thần Liên Châu`
  - `[x]` CẢNH MỞ: "Chiến binh!" → "Cao Lỗ!"; Cao Lỗ không còn là nhân vật phụ mà là người chơi
  - `[x]` HP System: "Chiến binh" → "Cao Lỗ" ❤️❤️❤️
  - `[x]` CẢNH KẾT: "Chiến binh Toán" → "Cao Lỗ"
  - `[x]` Lời thoại thắng: "Cao Lỗ — [Tên]!"
- `[x]` Cập nhật `map.html` STORIES[1] & STORIES[2]
  - `[x]` STORIES[1]: "Em là Cao Lỗ, tổng công trình sư thiên tài..."
  - `[x]` STORIES[2]: "Thành Cổ Loa đứng vững — nhờ bộ óc của Cao Lỗ (em)..."

---
---

## [Gemini] 2026-05-28 — Phát triển Prototype Game Thủ Thành Âu Lạc (tower_defense.html)

- `[x]` 1. Cập Nhật FastAPI Web Server (`web_server.py`)
  - `[x]` Thêm route phục vụ `/tower_defense.html` tại cả `/tower_defense` và `/tower_defense.html` sử dụng `HTMLResponse`.
- `[x]` 2. Xây Dựng Game HTML/CSS/JS Cơ Bản (`tower_defense.html`)
  - `[x]` Thiết lập cấu trúc giao diện HTML5 Canvas (16x11 grid) và Design System Đại Việt cổ kính (Philosopher, Lora, Gold/Son-Red/Ivory).
  - `[x]` Tích hợp Web Audio API Synthesizer tạo hiệu ứng âm thanh bắn cung, làm chậm, pháo nổ chân thực mà không cần asset tĩnh.
- `[x]` 3. Hiện Thực Hóa Logic Tìm Đường Động BFS
  - `[x]` Xây dựng thuật toán Breadth-First Search (BFS) vẽ lại đường đi tối ưu ngay khi đặt/bán tháp phòng thủ.
  - `[x]` Lập trình tính năng Chống chặn đường (Blocking Prevention) ngăn người chơi bịt kín lối ra của quân địch.
- `[x]` 4. Hoàn Thiện Hệ Thống Tháp & Kẻ Địch Của Cao Lỗ
  - `[x]` Triển khai 3 loại tháp: Tháp Tre Cổ Lũy (Arrow), Tháp Bẫy Nhựa Rừng (Slow), Tháp Pháo Thần Cơ (Splash).
  - `[x]` Thiết lập hệ thống quái vật (Quỷ Số, quân giặc) di chuyển mượt mà, có thanh máu, hiệu ứng giảm tốc và nổ pháo.
  - `[x]` Hỗ trợ các nút điều khiển nâng cao: Play/Pause, Fast Forward 2x, nâng cấp (Upgrade), bán tháp (Sell), và nút Thoát thoát hiểm.

---
---

## [Gemini] 2026-05-28 — Tái Thiết Kế Mỹ Thuật Đồ Họa & Giao Diện Theo Phong Cách Fieldrunners 2

- `[/]` 1. Cải tiến giao diện UI/UX lơ lửng (Floating Command HUD)
  - `[ ]` Thay thế header cũ bằng bảng điều khiển nổi trong suốt, định dạng phông chữ clamp.
  - `[ ]` Thiết kế lại shop tháp (khay tròn nổi) ở góc dưới với hiệu ứng 3D hover và giá vàng nổi.
  - `[ ]` Biến đổi Details Panel thành ngăn kéo nâng cấp/bán cơ khí trượt lên mượt mà.
- `[/]` 2. Nâng cấp đồ họa Canvas: Pháo đài xoay (Rotating Turrets)
  - `[ ]` Cập nhật lớp `Tower` hỗ trợ xoay nòng pháo mượt mà theo góc kẻ địch (`angle`, `currentAngle`).
  - `[ ]` Vẽ đế tháp đồng cổ kính và nòng súng/turret xoay riêng biệt, hỗ trợ hiệu ứng giật nòng (`recoil`).
- `[/]` 3. Nâng cấp hiệu ứng chiến đấu rực rỡ (Trails & Waves)
  - `[ ]` Vẽ đường đạn mượt mà: vệt lao tre mờ ảo, bọt nhựa xanh lá bám dính, pháo cối bay parabol xoay vòng.
  - `[ ]` Thêm hiệu ứng nổ lan: vòng sóng xung kích (Explosion Shockwave) lan rộng và tàn lửa cho Thần Cơ Pháo.
  - `[ ]` Thêm trạng thái nhấp nhô (wobble) khi đi của kẻ địch, vòng mục tiêu đỏ, và bao phủ băng tuyết khi bị làm chậm.
  - `[ ]` Vẽ lưới hướng đi di động (Marching Glowing Chevron Arrows) lấp lánh dọc lộ trình quái.

---
---


---
---
[Claude] 2026-05-28
## Zone-Based Character System — Implementation Complete

### Changes Made
**register.html**
- Removed Step 2 character selection (4-class grid: Lạc Tướng/Đạo Sĩ/Nỏ Thần/Thần Tướng)
- Step indicator: 3 dots → 2 dots (Thông tin → ✓)
- Step 1 CTA: `goStep2()` → `submitDirect()` — submits directly from info form
- Removed: `step2bg`, `step2Overlay` divs, `currentChar`, `currentFolder` state vars
- Removed: `selectChar()`, `updateAvatarImages()`, `updateCharPreview()`, `goStep2()` functions
- `_submitProfile()` → `submitDirect()`: reads step1 form, defaults `character_type='chien_binh'`
- `goStep()` simplified: handles only step1, step3, steprejected

**map.html**
- Header: `justify-content: flex-end` → `space-between`
- Header HTML: replaced avatar `<img>` with zone character badge (emoji circle + name + title)
- Header: added 🏛️ Kho button (calls `openVault()`)
- Added `ZONE_CHARACTERS` array (6 zones, each with nodes, buois, name, emoji, color, zone_name)
- Replaced `loadSelectedCharacter()` with `loadZoneCharacter()` — reads active zone from `ZONE_CHARACTERS`
- Auth gate: removed old class-map + vsSelectedChar logic, calls `loadZoneCharacter()` instead
- Added vault CSS: `.vault-modal`, `.vault-panel`, `.vault-grid`, `.vault-char-card`, `.vault-unlock-badge`
- Added vault HTML: `#vaultModal` bottom sheet before `#introModal`
- Added `openVault()`: builds 6 character cards from `ZONE_CHARACTERS` + `cbToan_badges`, shows unlocked/in-progress/locked states
- Added `closeVault()`

### Zone → Character Mapping
| Zone | Nodes (ải) | Buois (live) | Character |
|------|-----------|-------------|-----------|
| 0 | 1–3 | — | Lạc Long Quân |
| 1 | 4–6 | — | Thánh Gióng |
| 2 | 7–8 | 1, 2 | Cao Lỗ ← LIVE |
| 3 | 9–10 | — | Trưng Trắc |
| 4 | 11–12 | — | Ngô Quyền |
| 5 | 13 | — | Đinh Bộ Lĩnh |

### Status: ✅ Complete
