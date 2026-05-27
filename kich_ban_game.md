# KỊCH BẢN GAME: CHIẾN BINH TOÁN
## VINASTUDY · HÀNH TRÌNH XUYÊN KHÔNG THỜI GIAN

> Cập nhật: 2026-05-27 · Phiên bản v4.0

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

Học sinh điều khiển Cỗ máy Đông Sơn đi dọc tiến trình lịch sử Đại Việt theo **thứ tự thời gian từ xa xưa nhất đến gần nhất**. Mỗi Ải = 1 Buổi học Toán 3, gắn với một sự kiện lịch sử/huyền sử có thật.

---

### 🐉 TRẠM 0: HỒNG BÀNG & HÙNG VƯƠNG SƠ KỲ
*Thời kỳ: ~2879 TCN (huyền sử) · Văn Lang sơ khai · Đông Sơn sơ kỳ*

**Ải 1: Trứng Tiên Nở Trăm Con** *(Buổi 1)*
- **Toán:** Ôn tập — Cộng, trừ phạm vi 100 · Chia đôi · Tính nhẩm
- **Bối cảnh:** Bờ biển Hồng Bàng. Lạc Long Quân và Âu Cơ chia tay — 100 người con phải được chia đôi: 50 theo cha xuống biển, 50 theo mẹ lên núi.
- **Cốt truyện:** Ngư Tinh tung Lưới Hỗn Độn xóa sạch mọi phép đếm và phép chia → Lạc Long Quân không thể chia con công bằng. Học sinh tính lại → 50+50=100 hoàn chỉnh → thuyền lửa dụ Ngư Tinh → Ngư Tinh bị diệt → Âu Cơ dẫn 50 con lên núi Nghĩa Lĩnh → Hùng Vương thứ 1 lên ngôi.
- **Boss:** 🐟 Ngư Tinh (Quái Ngư Nghìn Tuổi — Lưới Hỗn Độn phá phép đếm và chia đôi)
- **Đồng minh:** 🐉 Lạc Long Quân · 🧚 Âu Cơ
- **File kịch bản:** `scenarios/ai-1-lac-long-quan.md`

**Ải 2: Mười Lăm Bộ Lạc Văn Lang** *(Buổi 2)*
- **Toán:** Đọc và viết số có 3 chữ số · Số tròn trăm · Nhận biết hàng trăm-chục-đơn vị
- **Bối cảnh:** Phong Châu (Phú Thọ), Hùng Vương thứ 1. Triều đình mới lập cần đọc chính xác số liệu dân đinh, lương thực từ 15 bộ lạc để cai trị đất nước.
- **Cốt truyện:** Mộc Tinh (tinh cây cổ thụ) xâm nhập kho thẻ tre, đảo lộn vị trí các chữ số → 345 thành 534, 208 thành 820. Học sinh đọc và viết lại đúng 6 bộ số liệu → Hùng Vương vận hành được 15 bộ → Mộc Tinh bị Lạc Long Quân tiêu diệt.
- **Boss:** 🌳 Mộc Tinh (Cây Cổ Thụ Nghìn Năm — đảo vị trí chữ số trong mọi con số)
- **Đồng minh:** 👑 Hùng Vương thứ 1 · 🧙 Lạc Hầu
- **File kịch bản:** `scenarios/ai-2-van-lang.md`

**Ải 3: Yêu Cáo Chín Đuôi Tây Hồ** *(Buổi 3)*
- **Toán:** So sánh số có 3 chữ số · Xếp thứ tự · Tìm số lớn nhất/nhỏ nhất · Dấu >, <, =
- **Bối cảnh:** Vùng hồ lớn phía tây Phong Châu (nay là Tây Hồ, Hà Nội). Hồ Tinh — cáo 9 đuôi nghìn tuổi — cướp của cải từ khắp các bộ lạc và ẩn náu trong hang đá.
- **Cốt truyện:** Hồ Tinh dùng phép Huyễn Số xáo trộn thứ tự con số trong báo cáo mất mát → không ai biết bộ nào mất nhiều nhất → không định vị được hang. Học sinh so sánh và xếp đúng thứ tự → tìm ra bộ mất nhiều nhất → định vị hang → Lạc Long Quân phá hang → Tây Hồ hình thành.
- **Boss:** 🦊 Hồ Tinh (Cáo Chín Đuôi — Huyễn Số xáo trộn thứ tự mọi con số)
- **Đồng minh:** 🐉 Lạc Long Quân
- **File kịch bản:** `scenarios/ai-3-ho-tinh.md`

---

### 🥁 TRẠM 1: HÙNG VƯƠNG TRUNG & HẬU KỲ
*Thời kỳ: Văn Lang (~800 - 258 TCN) · Đông Sơn cực thịnh*

**Ải 4: Tiếng Trống Thúc Quân** *(Buổi 4)*
- **Toán:** Dãy số tự nhiên cách đều
- **Bối cảnh:** Làng Phù Đổng, Hùng Vương thứ 6. Cậu bé 3 tuổi xin ngựa sắt, giáp sắt đánh giặc Ân.
- **Cốt truyện:** Ân Cổ Sứ gõ Trống Vàng Ân phá tan quy luật dãy số ghi kế hoạch rèn giáp. Học sinh phục hồi 6 dãy số cách đều → giáp hoàn thành → Thánh Gióng xuất trận → diệt quân Ân.
- **Boss:** 🥁 Ân Cổ Sứ (Trống Vàng Ân phá quy luật dãy số)
- **Đồng minh:** ⚔️ Thánh Gióng (Phù Đổng Thiên Vương)
- **File kịch bản:** `scenarios/ai-4-thanh-giong.md`

**Ải 5: Đê Thần & Trận Hồng Thủy** *(Buổi 5)*
- **Toán:** Phép cộng số có 3 chữ số (có nhớ và không có nhớ)
- **Bối cảnh:** Châu thổ Sông Hồng, Hùng Vương thứ 18. Sơn Tinh cần số liệu chính xác để đắp đê chặn lũ.
- **Cốt truyện:** Bọt Hỗn Độn của Thủy Tinh xóa kết quả phép cộng → đê không hoàn thành. Học sinh tính lại → Sơn Tinh nâng núi → đê đứng → Thủy Tinh rút.
- **Boss:** 🌊 Thủy Tinh (Bọt Hỗn Độn xóa phép cộng)
- **Đồng minh:** 🏔️ Sơn Tinh (Tản Viên Sơn Thánh)
- **File kịch bản:** `scenarios/ai-5-son-tinh.md`

**Ải 6: Bếp Lửa Của Hoàng Tử Nghèo** *(Buổi 6)*
- **Toán:** Phép trừ số có 3 chữ số (có nhớ và không có nhớ)
- **Bối cảnh:** Cung Hùng Vương, Phong Châu, Hùng Vương thứ 6. Lang Liêu chuẩn bị Bánh Chưng Bánh Dày dâng vua chọn kế vị.
- **Cốt truyện:** Gian Thần Ân lấy trộm nguyên liệu + xóa hồ sơ số lượng. Học sinh tính phép trừ → phát hiện phần bị lấy → bắt gian thần → Lang Liêu làm đủ bánh → được kế vị.
- **Boss:** 🕵️ Gian Thần Ân (gián điệp bếp núc, xóa hồ sơ phép trừ)
- **Đồng minh:** 🍃 Lang Liêu (Hoàng tử thứ 18)
- **File kịch bản:** `scenarios/ai-6-lang-lieu.md`

---

### 🏛️ TRẠM 2: CỔ LOA — ÂU LẠC & THỤC PHÁN
*Thời kỳ: Âu Lạc (~257 - 179 TCN) · An Dương Vương*

**Ải 7: Bí Ẩn Cổ Loa** *(Buổi 7)*
- **Toán:** Phân biệt Số & Chữ số · Cấu tạo số tự nhiên · Giá trị theo vị trí
- **Bối cảnh:** Thành Cổ Loa (~257 TCN). Tường thành xây xong ban ngày, sáng hôm sau đổ sập — suốt 2 năm liên tiếp.
- **Cốt truyện:** Tiếng gáy ma mị của Bạch Kê Tinh xóa tri thức phân biệt số và chữ số → kiến trúc sư không đo được đúng → tường đổ. Học sinh phục hồi 7 câu hỏi về chữ số và giá trị vị trí → Thần Kim Quy hạ Bạch Kê Tinh → Cổ Loa hoàn thành.
- **Boss:** 🐓 Bạch Kê Tinh (9 lông đuôi phong ấn 9 chữ số 0-9)
- **Đồng minh:** 🐢 Thần Kim Quy
- **File kịch bản:** `scenarios/ai-7-co-loa.md`

**Ải 8: Nỏ Thần Liên Châu** *(Buổi 8)*
- **Toán:** Cấu tạo số 3 chữ số (hàng trăm, hàng chục, hàng đơn vị) · So sánh số
- **Bối cảnh:** Tướng Cao Lỗ chế tạo Nỏ Thần từ vuốt Rùa Vàng, bắn vạn mũi tên.
- **Cốt truyện:** Bản đúc khuôn đồng bị hư hại — thông số kỹ thuật mất. Học sinh điền đúng giá trị theo vị trí để Cao Lỗ hoàn thiện nỏ hộ quốc.
- **Boss:** TBD

---

### 🥁 TRẠM 3: TIẾNG TRỐNG MÊ LINH — THỜI KỲ TRƯNG VƯƠNG
*Thời kỳ: ~40 - 43 SCN · Hai Bà Trưng*

**Ải 9: Hội Quân Mê Linh** *(Buổi 9)*
- **Toán:** Cộng/trừ có nhớ trong phạm vi 1000
- **Bối cảnh:** Hai Bà Trưng phất cờ khởi nghĩa năm 40 SCN.
- **Cốt truyện:** Các cánh quân từ khắp nơi đổ về, học sinh tính quân số, voi chiến để sắp xếp doanh trại.

**Ải 10: Chiến Thuật Voi Chiến** *(Buổi 10)*
- **Toán:** Nhân/Chia cơ bản, bảng cửu chương
- **Cốt truyện:** Chia đội hình voi chiến theo hàng lối để phá kỵ binh địch, giành lại 65 thành trì.

---

### ⚓ TRẠM 4: TIẾNG SẤM SÔNG BẠCH ĐẰNG
*Thời kỳ: 938 SCN · Ngô Quyền*

**Ải 11 & 12: Trận Bạch Đằng — Ngô Quyền Đại Phá Nam Hán**
- **Toán:** Phép nhân/chia, đo lường & thời gian
- **Cốt truyện:** Cắm trận địa cọc gỗ bịt sắt; tính thời gian thủy triều để dụ địch vào bẫy.

---

### 👑 TRẠM ĐẶC BIỆT: THỐNG NHẤT GIANG SƠN
*Thời kỳ: 968 SCN · Đinh Bộ Lĩnh*

**Ải 13: Cờ Lau Tập Trận — Đinh Bộ Lĩnh Dẹp Loạn 12 Sứ Quân**
- **Toán:** Giải toán có lời văn tổng hợp
- **Cốt truyện:** Giải đố phân chia lãnh địa và thu phục sứ quân — giúp Đinh Bộ Lĩnh thống nhất đất nước.

---

## 5. HỆ THỐNG BOSS

| Boss | Ải | Cơ chế phá hoại | Bị hạ bởi |
|---|---|---|---|
| 🐟 **Ngư Tinh** | Ải 1 | Lưới Hỗn Độn xóa phép đếm, phép chia | Lạc Long Quân (thuyền lửa) |
| 🌳 **Mộc Tinh** | Ải 2 | Đảo vị trí chữ số → không đọc được số | Lạc Long Quân (đốt gốc, diệt tinh) |
| 🦊 **Hồ Tinh** | Ải 3 | Huyễn Số xáo trộn thứ tự con số | Lạc Long Quân (phá hang, thành Tây Hồ) |
| 🥁 **Ân Cổ Sứ** | Ải 4 | Trống Vàng Ân xóa quy luật dãy số | Thánh Gióng (sau khi giáp hoàn thành) |
| 🌊 **Thủy Tinh** | Ải 5 | Bọt Hỗn Độn xóa kết quả phép cộng | Sơn Tinh (sau khi đê hoàn thành) |
| 🕵️ **Gian Thần Ân** | Ải 6 | Lấy trộm nguyên liệu + xóa hồ sơ phép trừ | Lang Liêu (bắt quả tang) |
| 🐓 **Bạch Kê Tinh** | Ải 7 | Tiếng gáy bình minh xóa tri thức số & chữ số | Thần Kim Quy (hóa chuột cắn chân) |
| TBD | Ải 8+ | TBD | TBD |

**Ngư Tinh — thiết kế:** Cá khổng lồ đen bạc, vẩy như giáp đồng, mắt đỏ rực từ đáy biển, đuôi vung tạo sóng cao.

**Mộc Tinh — thiết kế:** Cây cổ thụ khổng lồ màu đen-xanh biết di chuyển, rễ như xúc tu bạch tuộc, lá rụng thành dao nhọn.

**Hồ Tinh — thiết kế:** Nữ nhân áo đỏ rực, 9 đuôi cáo vàng phát sáng ảo huyễn, đôi mắt xanh lạnh phát ánh ảo thuật.

**Ân Cổ Sứ — thiết kế:** Pháp sư cao lớn, áo đen viền vàng, mặt như đúc đồng, cầm Trống Vàng Ân hoa văn xoáy hỗn độn.

**Thủy Tinh — thiết kế:** Người từ thắt lưng trở lên, phần dưới là vùng nước xoáy, áo xanh lam sẫm, tóc xanh đen.

**Gian Thần Ân — thiết kế:** Tạp dề bếp giả mạo, mắt ti hí, lộ áo Ân đen viền vàng khi bị phát hiện.

**Bạch Kê Tinh — thiết kế:** Gà trắng mắt đỏ, 9 lông đuôi dài phát sáng xanh lạnh, mỗi lông ẩn một chữ số.

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

| Ải | Buổi | Tên | Thời kỳ | Nhân vật | Toán | Boss | File |
|---|---|---|---|---|---|---|---|
| 1 | B1 | Trứng Tiên Nở Trăm Con | Hồng Bàng | Lạc Long Quân & Âu Cơ | Cộng trừ /100, chia đôi | Ngư Tinh 🐟 | `ai-1-lac-long-quan.md` |
| 2 | B2 | Mười Lăm Bộ Lạc Văn Lang | Hùng Vương 1 | Hùng Vương 1, Lạc Hầu | Đọc viết số 3 chữ số | Mộc Tinh 🌳 | `ai-2-van-lang.md` |
| 3 | B3 | Yêu Cáo Chín Đuôi Tây Hồ | Hùng Vương sơ kỳ | Hồ Tinh, Lạc Long Quân | So sánh, xếp thứ tự số | Hồ Tinh 🦊 | `ai-3-ho-tinh.md` |
| 4 | B4 | Tiếng Trống Thúc Quân | Hùng Vương 6 | Thánh Gióng | Dãy số cách đều | Ân Cổ Sứ 🥁 | `ai-4-thanh-giong.md` |
| 5 | B5 | Đê Thần & Trận Hồng Thủy | Hùng Vương 18 | Sơn Tinh, Thủy Tinh | Phép cộng 3 chữ số | Thủy Tinh 🌊 | `ai-5-son-tinh.md` |
| 6 | B6 | Bếp Lửa Của Hoàng Tử Nghèo | Hùng Vương 6 | Lang Liêu | Phép trừ 3 chữ số | Gian Thần Ân 🕵️ | `ai-6-lang-lieu.md` |
| 7 | B7 | Bí Ẩn Cổ Loa | Âu Lạc 257 TCN | An Dương Vương, Cao Lỗ | Số & Chữ số, giá trị vị trí | Bạch Kê Tinh 🐓 | `ai-7-co-loa.md` |
| 8 | B8 | Nỏ Thần Liên Châu | Âu Lạc 257 TCN | Cao Lỗ | Cấu tạo số, so sánh | TBD | TBD |
| 9 | B9 | Hội Quân Mê Linh | 40 SCN | Hai Bà Trưng | Cộng/trừ có nhớ 1000 | TBD | TBD |
| 10 | B10 | Chiến Thuật Voi Chiến | 40 SCN | Hai Bà Trưng | Bảng nhân/chia | TBD | TBD |
| 11-12 | B11-12 | Trận Bạch Đằng | 938 SCN | Ngô Quyền | Nhân/chia, đo lường | TBD | TBD |
| 13 | B13 | Cờ Lau Tập Trận | 968 SCN | Đinh Bộ Lĩnh | Toán lời văn tổng hợp | TBD | TBD |

*Chiến Binh Toán · VINASTUDY · v4.0 · 2026-05-27*
