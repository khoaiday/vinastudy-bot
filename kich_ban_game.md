# KỊCH BẢN GAME: CHIẾN BINH TOÁN
## VINASTUDY · HÀNH TRÌNH XUYÊN KHÔNG THỜI GIAN

> Cập nhật: 2026-05-27 · Phiên bản v3.0

---

## 1. BỐI CẢNH & CỐT TRUYỆN (LORE)

### Lời mở đầu — 3 đoạn Prologue (hiển thị khi vào game)

**Đoạn 1 — Cỗ máy Đông Sơn:**
> *"Từ ngàn năm trước, các bậc tiền nhân Đại Việt đã tiên tri được một tai ương hủy diệt. Cỗ máy Đông Sơn không chỉ đơn thuần là vũ khí thủ thành, mà là một đại trận pháp công nghệ cổ xưa được phong ấn, lưu giữ toàn bộ mã nguồn của dòng chảy lịch sử dân tộc qua mọi thời đại..."*

**Đoạn 2 — Kẻ thù xuất hiện:**
> *"Năm 2026 SCN, một hiện tượng kinh hoàng ập đến. Một thực thể hắc ám vô hình từ phương Bắc bất ngờ trỗi dậy, khuấy đảo hư không. Thực thể đen tối này đang điên cuồng can thiệp vào trục thời gian, hòng xóa sổ những chiến công hiển hách và bóp méo cội nguồn dân tộc..."*

**Đoạn 3 — Lời triệu tập:**
> *"Trước nguy cơ lịch sử bị xóa sổ, Cỗ máy Đông Sơn chính thức thức giấc, tự động kích hoạt hệ thống phòng thủ xuyên thời không. Nó biến thành một cổng trục thời gian vĩ đại, phóng đi những hạt dữ liệu định vị vào không gian của quá khứ và kêu gọi các "Chiến binh Toán" bước vào cuộc hành trình xuyên thời không..."*

---

### Năm 2026 — Phòng Thí Nghiệm Của Thầy Long
Tại Viện Nghiên cứu Toán học Vinastudy, **Thầy Long** — nhà toán học kiêm kỹ sư lỗi lạc — là người giám hộ **Cỗ máy Đông Sơn**. Cỗ máy này không chạy bằng điện năng thông thường, mà vận hành bằng **Năng lượng Tư duy Toán học (Math Energy)**.

Một thực thể hắc ám vô hình từ phương Bắc bất ngờ can thiệp vào trục thời gian — xóa sổ chiến công, bóp méo lịch sử. Cỗ máy Đông Sơn tự thức giấc, mở cổng xuyên không và triệu tập **Chiến Binh Toán** — những học sinh lớp 3 có tâm hồn trong sáng và tư duy sắc bén — bước vào cuộc hành trình vá lại lịch sử.

---

## 2. NHÂN VẬT (CHARACTERS)

### 2.1 Nhân vật chơi được — 4 lớp nhân vật

Người chơi chọn **lớp nhân vật** và **giới tính** khi đăng ký. Mỗi lớp có avatar riêng (male/female).

| Lớp | Màu chủ | HP | Sở trường | Lore |
|---|---|---|---|---|
| ⚔️ **Lạc Tướng** | Đỏ #BE1A30 | Cao nhất | Tấn công | Tướng Hùng Vương, khiên đồng Đông Sơn, kiếm Việt |
| 🔮 **Đạo Sĩ** | Tím #7040A0 | Trung bình | Phép thuật | Pháp sư Lạc Việt, gậy hoa sen, cuộn Lĩnh Nam Chích Quái |
| 🏹 **Nỏ Thần** | Ngọc #5ABCAA | Thấp | Tốc độ | Chiến binh Cổ Loa, nỏ liên hoàn An Dương Vương |
| 🛡️ **Thần Tướng** | Chàm #2B2096 | Tối đa | Phòng thủ | Hình tượng Thánh Gióng + Trần Hưng Đạo, giáo sắt, khiên hổ phù |

**Asset:** `design-system/characters/playable/{folder}/{folder}-{male|female}-avatar.jpg`

---

### 2.2 Người đồng hành & hỗ trợ

- **Thầy Long (Mentor):** Kết nối qua bộ đàm holographic từ phòng thí nghiệm năm 2026. Cung cấp bối cảnh lịch sử và giảng giải toán học. Đóng vai AI Claude phân tích kết quả học sinh.

- **Cỗ máy Đông Sơn (Trợ lý):** Hiện thân tương tác của cỗ máy — giọng nói, biểu tượng hình trống đồng phát sáng. Khi học sinh gặp bài quá khó, Cỗ máy Đông Sơn kích hoạt **Hệ Thống Gợi Mở (Scaffolding)** — gợi ý từng bước mà không làm hộ đáp án.

---

## 3. LUỒNG TRẢI NGHIỆM NGƯỜI DÙNG (USER FLOW)

```
[Telegram Bot] 
    → /start hoặc nút Menu
    → intro.html (Splash: Chiến Binh Toán + VINASTUDY)
        → Chạm "chạm để xem lời mở đầu"
        → Prologue 3 đoạn (typewriter, có thể quay lại)
        → "bắt đầu cuộc hành trình »"
    → register.html
        → Bước 1: Nhập tên + chọn giới tính
        → Bước 2: Chọn nhân vật (4 lớp × 2 giới tính)
        → Submit → Thầy Long duyệt
        → Bước 3: Chờ duyệt (polling 5 giây/lần)
    → [Thầy Long duyệt qua Telegram Admin]
    → map.html (Bản đồ Chiến Dịch)
```

---

## 4. HÀNH TRÌNH KHẢO CỔ TOÁN HỌC (CAMPAIGN MAP)

Học sinh điều khiển Cỗ máy Đông Sơn đi dọc tiến trình lịch sử Đại Việt theo **thứ tự thời gian từ xa xưa nhất đến gần nhất**. Mỗi Ải là một sự kiện lịch sử/huyền sử có thật, lồng ghép bài Toán Lớp 3.

---

### 🥁 TRẠM 1: THUỞ BÌNH MINH — HÙNG VƯƠNG & VĂN LANG
*Thời kỳ: Văn Lang (~2879 - 258 TCN) · Văn minh Đông Sơn*

**Ải 1: Tiếng Trống Thúc Quân**
- **Toán:** Dãy số tự nhiên cách đều (Buổi 4)
- **Bối cảnh:** Làng Phù Đổng, Hùng Vương thứ 6. Cậu bé 3 tuổi đột nhiên lên tiếng xin ngựa sắt, giáp sắt để đánh giặc Ân.
- **Cốt truyện:** Ân Cổ Sứ gõ Trống Vàng Ân phá tan quy luật của mọi dãy số ghi kế hoạch rèn giáp. Học sinh phục hồi 6 dãy số cách đều → giáp hoàn thành → Thánh Gióng xuất trận.
- **Boss:** 🥁 Ân Cổ Sứ (Sứ thần trống Ân — Trống Vàng Ân phá quy luật số học)
- **Đồng minh:** ⚔️ Thánh Gióng (Phù Đổng Thiên Vương)
- **File kịch bản:** `scenarios/ai-1-thanh-giong.md`

**Ải 2: Đê Thần & Trận Hồng Thủy**
- **Toán:** Phép cộng số có 3 chữ số (có nhớ và không có nhớ)
- **Bối cảnh:** Châu thổ Sông Hồng, Hùng Vương thứ 18. Sơn Tinh cần số liệu chính xác để đắp đê chặn lũ của Thủy Tinh.
- **Cốt truyện:** Bọt Hỗn Độn của Thủy Tinh xóa sạch kết quả các phép cộng ghi kế hoạch đắp đê. Học sinh tính lại → Sơn Tinh có dữ liệu nâng núi → đê đứng vững → Thủy Tinh rút lui.
- **Boss:** 🌊 Thủy Tinh (Thần Nước, Bọt Hỗn Độn xóa phép cộng)
- **Đồng minh:** 🏔️ Sơn Tinh (Tản Viên Sơn Thánh)
- **File kịch bản:** `scenarios/ai-2-son-tinh.md`

**Ải 3: Bếp Lửa Của Hoàng Tử Nghèo**
- **Toán:** Phép trừ số có 3 chữ số (có nhớ và không có nhớ)
- **Bối cảnh:** Cung Hùng Vương tại Phong Châu, Hùng Vương thứ 6. Lang Liêu chuẩn bị Bánh Chưng Bánh Dày dâng vua để chọn người kế vị.
- **Cốt truyện:** Gian Thần Ân (gián điệp phương Bắc trà trộn) lấy bớt nguyên liệu và xóa hồ sơ số lượng. Học sinh tính lại phép trừ → phát hiện phần bị lấy trộm → bắt gian thần → Lang Liêu làm đủ bánh dâng vua → được chọn kế vị.
- **Boss:** 🦊 Gian Thần Ân (gián điệp ẩn, xóa kết quả phép trừ)
- **Đồng minh:** 🍃 Lang Liêu (Hoàng tử thứ 18)
- **File kịch bản:** `scenarios/ai-3-lang-lieu.md`

---

### 🏛️ TRẠM 2: CỔ LOA — ÂU LẠC & THỤC PHÁN
*Thời kỳ: Âu Lạc (~257 - 179 TCN) · An Dương Vương*

**Ải 4: Bí Ẩn Cổ Loa**
- **Toán:** Phân biệt Số & Chữ số · Cấu tạo số tự nhiên · Đọc viết số 3 chữ số
- **Bối cảnh:** Thành Cổ Loa (~257 TCN). An Dương Vương xây thành 2 năm liên tục đổ — nguyên nhân do Bạch Kê Tinh làm các kiến trúc sư không phân biệt được số và chữ số.
- **Cốt truyện:** Tiếng gáy ma mị của Bạch Kê Tinh xóa tri thức về cấu tạo số. Học sinh phục hồi 7 dãy câu hỏi về chữ số và giá trị vị trí → Thần Kim Quy hạ gục Bạch Kê Tinh → Cổ Loa đứng vững.
- **Boss:** 🐓 Bạch Kê Tinh (Tinh Gà Trắng — 9 lông đuôi phong ấn 9 chữ số 0-9)
- **Đồng minh:** 🐢 Thần Kim Quy
- **File kịch bản:** `scenarios/ai-4-co-loa.md`

**Ải 5: Nỏ Thần Liên Châu**
- **Toán:** Cấu tạo số 3 chữ số (hàng trăm, hàng chục, hàng đơn vị) · So sánh số
- **Bối cảnh:** Tướng Cao Lỗ chế tạo Nỏ Thần từ vuốt Rùa Vàng, bắn vạn mũi tên.
- **Cốt truyện:** Bản đúc khuôn đồng bị hư hại — thông số kỹ thuật mất. Học sinh điền đúng giá trị theo vị trí để Cao Lỗ hoàn thiện nỏ hộ quốc.
- **Boss:** TBD (Ân gián điệp phá khuôn đúc)

---

### 🥁 TRẠM 3: TIẾNG TRỐNG MÊ LINH — THỜI KỲ TRƯNG VƯƠNG
*Thời kỳ: ~40 - 43 SCN · Hai Bà Trưng*

**Ải 6: Hội Quân Mê Linh**
- **Toán:** Cộng/trừ có nhớ trong phạm vi 1000
- **Bối cảnh:** Hai Bà Trưng phất cờ khởi nghĩa năm 40 SCN. Các cánh quân từ khắp nơi đổ về.
- **Cốt truyện:** Học sinh tính số binh sĩ, voi chiến từ các quận để sắp xếp doanh trại.

**Ải 7: Chiến Thuật Voi Chiến**
- **Toán:** Nhân/Chia cơ bản, bảng cửu chương
- **Bối cảnh:** Quân Đông Hán dàn trận mai phục.
- **Cốt truyện:** Chia đội hình voi chiến theo hàng lối để phá kỵ binh địch, giành lại 65 thành trì.

---

### ⚓ TRẠM 4: TIẾNG SẤM SÔNG BẠCH ĐẰNG — THỜI KỲ TỰ CHỦ
*Thời kỳ: 938 SCN · Ngô Quyền*

**Ải 8 & 9: Trận Bạch Đằng — Ngô Quyền Đại Phá Nam Hán**
- **Toán:** Phép nhân/chia, đo lường & thời gian
- **Bối cảnh:** Sông Bạch Đằng, năm 938. Quân Nam Hán do Hoằng Tháo kéo chiến thuyền vào vịnh.
- **Cốt truyện:** Ngô Quyền cần cắm trận địa cọc gỗ bịt sắt. Học sinh đo độ dài cọc, khoảng cách giữa cọc, và tính thời gian thủy triều lên xuống để dụ địch vào bẫy đúng lúc nước rút.

---

### 👑 TRẠM ĐẶC BIỆT: THỐNG NHẤT GIANG SƠN
*Thời kỳ: 968 SCN · Đinh Bộ Lĩnh*

**Ải 10: Cờ Lau Tập Trận — Đinh Bộ Lĩnh Dẹp Loạn 12 Sứ Quân**
- **Toán:** Giải toán có lời văn tổng hợp
- **Bối cảnh:** Hoa Lư cổ kính, cậu bé Đinh Bộ Lĩnh bày trận giả bằng cờ lau.
- **Cốt truyện:** Học sinh tham gia trận giả, giải đố phân chia lãnh địa và thu phục sứ quân — giúp Đinh Bộ Lĩnh thống nhất đất nước, lên ngôi Đinh Tiên Hoàng, đặt quốc hiệu Đại Cồ Việt.

---

## 5. HỆ THỐNG BOSS

| Boss | Ải | Cơ chế phá hoại | Bị hạ bởi |
|---|---|---|---|
| 🥁 **Ân Cổ Sứ** | Ải 1 | Trống Vàng Ân gõ → xóa quy luật dãy số | Thánh Gióng (sau khi giáp hoàn thành) |
| 🌊 **Thủy Tinh** | Ải 2 | Bọt Hỗn Độn → xóa kết quả phép cộng | Sơn Tinh (sau khi đê hoàn thành) |
| 🦊 **Gian Thần Ân** | Ải 3 | Lấy trộm nguyên liệu + xóa hồ sơ phép trừ | Lang Liêu (bắt quả tang) |
| 🐓 **Bạch Kê Tinh** | Ải 4 | Tiếng gáy bình minh xóa tri thức số & chữ số | Thần Kim Quy (hóa chuột cắn chân) |
| (TBD) | Ải 5+ | TBD | TBD |
| 🦊 **Hồ Tinh** | Trạm huyền sử | Cáo 9 đuôi thời Lạc Long Quân — màn mở đầu tùy chọn | — |

**Ân Cổ Sứ — thiết kế:** Pháp sư cao lớn, áo đen viền vàng, mặt như đúc đồng, cầm Trống Vàng Ân. Hoa văn trống: xoáy hỗn độn (đối lập trống Đông Sơn hoa văn đồng tâm đều đặn).

**Thủy Tinh — thiết kế:** Người từ thắt lưng trở lên, phần dưới là vùng nước xoáy, áo xanh lam sẫm, tóc xanh đen như sóng.

**Gian Thần Ân — thiết kế:** Ẩn trong bóng tối, mặc tạp dề bếp giả mạo, mắt ti hí ranh mãnh. Lộ áo Ân đen viền vàng khi bị phát hiện.

**Bạch Kê Tinh — thiết kế:** Gà trắng mắt đỏ, 9 lông đuôi dài phát sáng xanh lạnh, mỗi lông ẩn một chữ số. Tiếng gáy tạo sóng trắng ma mị.

**Hồ Tinh — thiết kế:** Nữ yêu hồ hybrid người+cáo, áo thụng đỏ, quạt vàng, 9 đuôi vàng phát sáng. Thời đại: huyền sử trước Hùng Vương.

---

## 6. CƠ CHẾ GAMEPLAY (CORE LOOP)

### Vòng lặp cơ bản
1. **Vào ải:** Thầy Long kể bối cảnh lịch sử (1-2 câu)
2. **Câu hỏi toán:** Hiển thị bài toán theo chủ đề lịch sử
3. **Học sinh trả lời:** Nhập đáp án / chọn đáp án
4. **Cỗ máy Đông Sơn scaffolding:** Nếu sai 2 lần → Cỗ máy Đông Sơn gợi ý từng bước
5. **Vượt ải:** Thầy Long nhận xét, cộng điểm, mở ải tiếp

### Hệ thống đánh giá năng lực
- **Reaction Time:** Thời gian từ khi hiện câu hỏi đến khi trả lời đúng (đo độ nhạy số học)
- **Grit & Attempts:** Số lần thử sai trước khi đúng (đo độ kiên trì)
- **AI Claude (vai Thầy Long):** Phân tích toàn bộ checkpoint → nhận xét cá nhân hoá, xếp mức năng lực:
  - 🌱 Mức 1 — Đang nảy mầm
  - ⚔️ Mức 2 — Chiến binh tập sự
  - 🏹 Mức 3 — Chiến binh thiện chiến
  - 🏆 Mức 4 — Hộ vệ lịch sử

### Bản đồ Chiến Dịch
- Cuộn tranh thư pháp cổ mở ra, bản đồ Đại Việt theo tiến trình thời gian
- Ải đã vượt: hóa vàng + gắn 🏆
- Ải hiện tại: nhấp nháy, sẵn sàng vào
- Ải chưa mở: xám, khóa

---

## 7. KỸ THUẬT & TRIỂN KHAI

| Thành phần | Công nghệ |
|---|---|
| Bot | Python + python-telegram-bot |
| Backend | FastAPI |
| Database | PostgreSQL |
| AI nhận xét | Claude API (Anthropic) |
| Deploy | Railway |
| Frontend | HTML/CSS/JS thuần (Telegram WebApp) |

### Các màn hình hiện có
| File | Chức năng | Trạng thái |
|---|---|---|
| `intro.html` | Splash + Prologue 3 đoạn typewriter | ✅ Done |
| `register.html` | Đăng ký: tên + giới tính + chọn nhân vật | ✅ Done |
| `map.html` | Bản đồ chiến dịch | 🔨 Cần làm |
| `battle.html` | Màn chơi câu hỏi toán | 🔨 Cần làm |
| `result.html` | Kết quả sau ải, nhận xét Thầy Long | 🔨 Cần làm |

---

## 8. PALETTE MÀU (DESIGN SYSTEM)

| Token | Hex | Dùng cho |
|---|---|---|
| Primary Gold | `#C8960C` | Logo, highlight, CTA |
| Secondary Red | `#C0332E` | Boss, nguy hiểm, Lạc Tướng |
| Copper Bronze | `#B87333` | Đông Sơn, đồng, accent |
| Void Black | `#07040A` | Background |
| Text Main | `#F5EED6` | Nội dung chính |
| Text Muted | `#A08C70` | Phụ, gợi ý |

Font: **Philosopher** (title) · **Lora** (body) · **Roboto Mono** (data/mono)

---

---

## 9. BẢNG TỔNG HỢP CÁC ẢI (v3.0)

| Ải | Tên | Thời kỳ | Nhân vật chính | Toán | Boss | File kịch bản |
|---|---|---|---|---|---|---|
| 1 | Tiếng Trống Thúc Quân | Hùng Vương 6 | Thánh Gióng | Dãy số cách đều (Buổi 4) | Ân Cổ Sứ 🥁 | `ai-1-thanh-giong.md` |
| 2 | Đê Thần & Trận Hồng Thủy | Hùng Vương 18 | Sơn Tinh | Phép cộng 3 chữ số | Thủy Tinh 🌊 | `ai-2-son-tinh.md` |
| 3 | Bếp Lửa Của Hoàng Tử Nghèo | Hùng Vương 6 | Lang Liêu | Phép trừ 3 chữ số | Gian Thần Ân 🦊 | `ai-3-lang-lieu.md` |
| 4 | Bí Ẩn Cổ Loa | Âu Lạc 257 TCN | An Dương Vương, Cao Lỗ | Số & Chữ số, cấu tạo số | Bạch Kê Tinh 🐓 | `ai-4-co-loa.md` |
| 5 | Nỏ Thần Liên Châu | Âu Lạc 257 TCN | Cao Lỗ | Cấu tạo số, so sánh | TBD | TBD |
| 6 | Hội Quân Mê Linh | 40 SCN | Hai Bà Trưng | Cộng/trừ có nhớ | TBD | TBD |
| 7 | Chiến Thuật Voi Chiến | 40 SCN | Hai Bà Trưng | Bảng nhân/chia | TBD | TBD |
| 8-9 | Trận Bạch Đằng | 938 SCN | Ngô Quyền | Nhân/chia, đo lường | TBD | TBD |
| 10 | Cờ Lau Tập Trận | 968 SCN | Đinh Bộ Lĩnh | Toán lời văn tổng hợp | TBD | TBD |

*Chiến Binh Toán · VINASTUDY · v3.0 · 2026-05-27*
