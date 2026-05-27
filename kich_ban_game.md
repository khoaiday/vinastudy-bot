# KỊCH BẢN GAME: CHIẾN BINH TOÁN
## VINASTUDY · HÀNH TRÌNH XUYÊN KHÔNG THỜI GIAN

> Cập nhật: 2026-05-27 · Phiên bản v2.0

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

Học sinh điều khiển Cỗ máy Đông Sơn đi dọc tiến trình lịch sử Đại Việt. Mỗi Ải là một sự kiện lịch sử có thật, lồng ghép bài Toán Lớp 3.

---

### 🏛️ TRẠM 1: THUỞ SƠ KHAI — DỰNG NƯỚC & GIỮ NƯỚC

**Ải 1: Bản Thiết Kế Của An Dương Vương**
- **Toán:** Phân biệt Số & Chữ số
- **Bối cảnh:** Loa Thành cổ kính. An Dương Vương phân tích nhân lực xây vòng thành ốc xoắn.
- **Cốt truyện:** Quân giặc tráo bản vẽ quy hoạch. Học sinh phải phân biệt ký hiệu "chữ số" cổ nhân và "số" lượng thực tế để xây thành đúng hạn.
- **Boss:** 🐓 Bạch Kê Tinh (Tinh Gà Trắng — 9 lông đuôi phong ấn chữ số 0-9, tiếng gáy bình minh xóa tri thức số học)

**Ải 2: Nỏ Thần Liên Châu**
- **Toán:** Cấu tạo số 3 chữ số (hàng trăm, hàng chục, hàng đơn vị)
- **Bối cảnh:** Tướng Cao Lỗ chế tạo Nỏ Thần bắn vạn mũi tên.
- **Cốt truyện:** Bản đúc khuôn đồng bị hư hại. Học sinh điền đúng thông số kỹ thuật để Cao Lỗ hoàn thiện nỏ hộ quốc.

**Ải 3: Đốm Đen Trên Thẻ Tre**
- **Toán:** Phép cộng/trừ trong phạm vi 1000
- **Bối cảnh:** Quân giặc làm đổ mực lên thẻ tre ghi kho lương Loa Thành.
- **Cốt truyện:** Khôi phục số liệu lương thảo để quân sĩ đủ sức xây thành bảo vệ đất nước.

---

### 🥁 TRẠM 2: TIẾNG TRỐNG MÊ LINH — THỜI KỲ TRƯNG VƯƠNG

**Ải 4: Hội Quân Mê Linh**
- **Toán:** Cộng/trừ có nhớ trong phạm vi 1000
- **Bối cảnh:** Hai Bà Trưng phất cờ khởi nghĩa năm 40 SCN tại cửa sông Hát.
- **Cốt truyện:** Các cánh quân từ khắp nơi đổ về. Học sinh tính số binh sĩ, voi chiến từ các quận để sắp xếp doanh trại.

**Ải 5: Chiến Thuật Voi Chiến**
- **Toán:** Nhân/Chia cơ bản, bảng cửu chương
- **Bối cảnh:** Quân Đông Hán dàn trận mai phục.
- **Cốt truyện:** Tính toán chia đội hình voi chiến theo hàng lối để phá kỵ binh địch, giành lại 65 thành trì.

---

### ⚓ TRẠM 3: TIẾNG SẤM SÔNG BẠCH ĐẰNG — THỜI KỲ TỰ CHỦ

**Ải 6 & 7: Trận Bạch Đằng — Ngô Quyền Đại Phá Nam Hán**
- **Toán:** Phép nhân/chia, đo lường & thời gian
- **Bối cảnh:** Sông Bạch Đằng, năm 938. Quân Nam Hán do Hoằng Tháo kéo chiến thuyền vào vịnh.
- **Cốt truyện:** Ngô Quyền cần cắm trận địa cọc gỗ bịt sắt. Học sinh đo độ dài cọc, khoảng cách giữa cọc, và tính thời gian thủy triều lên xuống để dụ địch vào bẫy đúng lúc nước rút.

---

### 👑 TRẠM ĐẶC BIỆT: THỐNG NHẤT GIANG SƠN

**Ải 8: Cờ Lau Tập Trận — Đinh Bộ Lĩnh Dẹp Loạn 12 Sứ Quân**
- **Toán:** Giải toán có lời văn tổng hợp
- **Bối cảnh:** Hoa Lư cổ kính, cậu bé Đinh Bộ Lĩnh bày trận giả bằng cờ lau.
- **Cốt truyện:** Học sinh tham gia trận giả, giải đố phân chia lãnh địa và thu phục sứ quân — giúp Đinh Bộ Lĩnh thống nhất đất nước, lên ngôi Đinh Tiên Hoàng, đặt quốc hiệu Đại Cồ Việt.

---

## 5. HỆ THỐNG BOSS

| Boss | Xuất hiện | Đặc điểm |
|---|---|---|
| 🐓 **Bạch Kê Tinh** | Ải 1 | Tinh Gà Trắng — tiếng gáy bình minh xóa tri thức số học. 9 lông đuôi phong ấn 9 chữ số 0-9. Bị Kim Quy hạ. |
| 🦊 **Hồ Tinh** | Trạm 0 (huyền sử) | Cáo chín đuôi thời Lạc Long Quân — dành cho màn huyền sử mở đầu (nếu có) |
| (Mở rộng sau) | Ải tiếp theo | TBD |

**Bạch Kê Tinh — thiết kế:** Gà trắng mắt đỏ, 9 lông đuôi dài phát sáng xanh lạnh, mỗi lông ẩn một chữ số. Tiếng gáy tạo sóng trắng ma mị. Được Thực thể phương Bắc triệu hồi và trao quyền năng.

**Hồ Tinh — thiết kế:** Nữ yêu hồ hybrid người+cáo, áo thụng đỏ (modest), quạt vàng, 9 đuôi vàng phát sáng. Thời đại: huyền sử trước Hùng Vương.

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

*Chiến Binh Toán · VINASTUDY · v2.0 · 2026-05-27*
