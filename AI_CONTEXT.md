# VINASTUDY BOT - BATTLE ARENA PROJECT CONTEXT

Tài liệu này chứa toàn bộ ngữ cảnh, quy chuẩn thiết kế và cấu trúc kỹ thuật mới nhất của dự án "VinaStudy Bot - Chiến binh Toán học". Hãy đọc kỹ tài liệu này trước khi thực hiện bất kỳ thay đổi nào để đảm bảo tính đồng bộ của dự án.

## 1. Tổng quan dự án
- **Mục tiêu:** Chuyển đổi các bài tập Toán học dạng danh sách nhàm chán thành một **Mini-game nhập vai (RPG) phong cách Cyberpunk / Sci-fi** ngay trên giao diện Telegram WebApp.
- **Tech Stack:** Vanilla HTML, CSS, JavaScript (Không sử dụng Framework nặng để đảm bảo tốc độ tải trên Telegram WebApp).
- **URL Production:** `https://app.soichido.vn/baitap/` (VD: `app.soichido.vn/baitap/daiviet_defense/index_3d.html`)

## 2. Quy chuẩn Đồ họa (Cyberpunk UI System)
Mọi thiết kế giao diện phải tuân thủ nghiêm ngặt hệ thống Design Tokens sau:

### 2.1. Typography & Colors
- **Font chữ:** `Roboto` (Nội dung dễ đọc) và `Rajdhani` (Tiêu đề, số liệu mang tính tương lai).
- **Màu nền tổng thể:** Nền tối `#050a1f` (Dark Navy) kết hợp lưới hoặc gradient.
- **Màu Neon chủ đạo:**
  - `var(--primary)`: `#0ae0fe` (Cyan/Neon Blue) - Dùng cho viền, nút bấm chính.
  - `var(--secondary)`: `#ea0eed` (Neon Purple) - Dùng cho điểm nhấn, Boss.
  - `var(--success)`: `#4eff9f` (Neon Green) - Dùng cho đáp án Đúng.
  - `var(--danger)`: `#ff0055` (Neon Red) - Dùng cho đáp án Sai.
  - `var(--amber)`: `#fbbf24` (Vàng/Cam) - Dùng cho cảnh báo, chờ đợi.

### 2.2. Hiệu ứng đặc trưng (Signature Effects)
- **Cyber Box (`.cyber-box`):** 
  - Khung viền bo tròn 16px.
  - Viền phát sáng được tạo bằng kỹ thuật `::before` với `linear-gradient` và dùng `-webkit-mask` cắt viền 2px hoàn hảo. 
  - KHÔNG sử dụng `border` thông thường hay `clip-path` cắt góc nữa.
- **Battle Arena Header:**
  - Sàn đấu 3D: Cấu trúc sử dụng `transform: rotateX(75deg)` kết hợp với ảnh nền lưới định dạng **SVG** (`stroke-width=3`) để chống nhiễu Moiré.
  - Các ký hiệu toán học lơ lửng: Sử dụng `translateZ` để bay từ xa (-600px) tới gần (400px), tạo chiều sâu không gian (Depth of Field).

## 3. Cấu trúc Gameplay (Single-Screen Mechanics)
- **Slide-based:** Thay vì hiển thị toàn bộ câu hỏi (Scrollable), bài tập được chia thành các màn hình nhỏ (Slide). Mỗi `q-slide` chứa Tiêu đề dạng, lý thuyết (`method-box`) và 1 câu hỏi.
- **Tự động chuyển cảnh:** Khi người chơi trả lời ĐÚNG, nút "Kiểm tra" chuyển thành nút "Tiếp tục" nhấp nháy (`pulseNeon`). Nhấn nút này sẽ tự động giấu slide hiện tại và trượt slide tiếp theo ra (`animation: fadeInRight`).
- **Hệ thống Combat:** 
  - Tích hợp thanh HP (Máu) của Người chơi và Quái vật. 
  - Trả lời đúng: Quái vật mất máu, bị rung lắc (`animation: shake`).
  - Trả lời sai: Người chơi mất máu.

## 4. Cấu trúc Thư mục (Directory Structure)
- `content/lop3/bai02/bai-tap.html`: **Phiên bản hoàn thiện nhất (Master Template)**. Toàn bộ tính năng Battle Arena và Slide đã được triển khai hoàn chỉnh ở đây.
- `content/lop3/bai03...`: Hiện tại mới chỉ được tiêm (inject) lớp CSS Cyberpunk bằng đoạn code ở cuối file (`CYBERPUNK RESKIN OVERRIDES`). Chưa được chuyển đổi cấu trúc HTML sang dạng Battle Arena.

## 5. Quy tắc cho AI (AI Instructions)
1. **Tuyệt đối không** phá vỡ cấu trúc `.cyber-box` bằng cách thêm border viền thuần. Phải sử dụng cấu trúc `::before/::after` đã có sẵn.
2. **Khi tạo giao diện mới**, luôn ưu tiên sử dụng dải màu Neon và thêm `box-shadow: 0 0 15px var(--primary-glow)` để tạo hiệu ứng phát sáng.
3. Khi làm việc với `bai03` đến `bai36`, cần cẩn thận vì cấu trúc HTML của chúng vẫn là dạng danh sách cũ. Nếu cần nâng cấp lên dạng Battle Arena, hãy tham khảo file `bai02/bai-tap.html` làm khuôn mẫu chuẩn.

---

## 6. Audio Assets — Suno Generated (daiviet_defense/audio/music/)

13 tracks đã có sẵn, tất cả trong `daiviet_defense/audio/music/`:

| File | Dùng cho |
|---|---|
| `main_theme.mp3` | Màn hình chính |
| `main_menu.mp3` | Menu chọn ải |
| `co_loa_theme_v1.mp3` | Bản đồ Zone Cổ Loa |
| `co_loa_theme_v2.mp3` | Bản đồ Zone Cổ Loa (alt) |
| `thanh_au_lac_v1.mp3` | Intro / cốt truyện |
| `thanh_au_lac_v2.mp3` | Intro / cốt truyện (alt) |
| `boss_wave.mp3` | Khi boss xuất hiện |
| `daiviet_battle_intense.mp3` | Trận đấu căng thẳng |
| `bach_dang_theme.mp3` | Zone Bạch Đằng |
| `me_linh_theme.mp3` | Zone Mê Linh |
| `level_select.mp3` | Chọn level |
| `victory_daiviet.mp3` | Thắng trận |
| `defeat_daiviet.mp3` | Thua trận |

SFX footsteps: `daiviet_defense/audio/impact/` (ogg format, kenney pack)

---

## 6b. FR2 Map Architecture — Bài học từ reverse engineering APK

XOR key: **0xF8** (single byte). Decrypt: `bytes(b ^ 0xF8 for b in raw)`

### Thiết kế map FR2 (đã xác nhận qua giải mã):
- **Map = ảnh JPG vẽ tay** (~900KB, ~1200×800px). Path được paint trực tiếp vào background.
- **Không có canvas grid lines** — engine biết grid tọa độ, player chỉ thấy artwork liền mạch.
- **Decoration strips** = PNG riêng ghép lên viền (rooftop, cliff, etc.)
- **Công thức**: Background JPG + enemy/tower sprites render đè lên + grid ẩn (chỉ highlight khi hover)

### Áp dụng cho Đại Việt Defender:
- Thay canvas texture hiện tại bằng **ảnh background painted** (Midjourney/DALL-E)
- Path = đường đá cuội vẽ vào scene, không phải canvas overlay
- Grid lines bỏ hoặc cực mờ, chỉ hiện khi đặt tháp
- Midjourney prompt: *"Vietnamese ancient fortress Cổ Loa top-down game map, stone brick winding path through rice fields, bamboo groves, spiral fortress walls, pagoda watchtowers, warm earth tones, hand-painted TD game art, 16:9, no text --ar 16:9"*

### Assets đã giải mã (trong apk/fr2_extracted/assets/):
| File | Nội dung |
|------|---------|
| 00000393 | Map grassland + river |
| 01621 | Map farm fields |
| 01256 | Map city cobblestone |
| 00000081 | Map crystal cave |
| 00000541 | Map lava industrial |
| 00000140 | Decoration strip (rooftop PNG) |

---

## 7. Tower Defense Game — daiviet_defense/

Đây là game thủ thành riêng biệt (KHÔNG phải battle.html). Đã có:

### 7.1 Specs
- `FR2_STRUCTURE_ANALYSIS.md` — phân tích APK Fieldrunners 2
- `GAME_BALANCE.md` — 9 tháp + 11 loại quân địch với stats đầy đủ
- `UI_DESIGN_SPEC.md` — thiết kế UI theo FR2 style

### 7.2 Towers (9 loại)
Nỏ Liên Châu · Bẫy Nhựa · Thần Cơ Pháo · Bẫy Chông · Hỏa Tháp · Trống Lệnh · Đàn Hương · Lôi Tháp · Thần Cơ Đại Pháo

### 7.3 Enemies (11 loại)
Lính Trinh Sát · Bộ Binh · Voi Chiến · Kị Binh · Quạ Sắt · Pháp Sư · Xe Trâu · Lính Bom · Khí Cầu · Đại Tướng · Quái Vô Hình

### 7.4 Assets 2D (daiviet_defense/assets/)
arrow_tower.png · bomb_tower.png · cannon_tower.png · flame_tower.png · slow_tower.png · tesla_tower.png
enemy_scout.png · enemy_soldier.png · enemy_heavy.png · enemy_cavalry.png · enemy_air.png · enemy_blimp.png · enemy_boss.png · enemy_medic.png

### 7.5 Assets 3D (daiviet_defense/3d_assets/)
- **Kenney TD pack** (GLB format): detail-crystal/dirt/rocks/tree, enemy-ufo variants
- `models/` — custom models
- `daiviet_defense/index_3d.html` — prototype 3D đã có

---

## 8. MVP Scope (Deadline 6/6/2026)

Chỉ Zone Cổ Loa (Ải 7 + Ải 8):
- Ải 7 (Buổi 1): minigame.html + minigame2.html + battle.html?ai=7 ✅ DONE
- Ải 8 (Buổi 2): minigame Ải 2 (TODO) + battle.html?ai=8 (TODO)

Yêu cầu UX: mượt như Fieldrunners 2 + nhạc nền Suno + đồ họa Đại Việt cổ kính

---

## 9. GAME DESIGN — Đại Việt Defender (MVP Cổ Loa)

### 9.1 Luồng chính (User Flow — CANONICAL)

```
Telegram bot → Đăng ký → Được duyệt → map.html
→ Chọn Ải Cổ Loa (Ải 7 hoặc 8)
→ intro.html — màn giới thiệu cốt truyện
→ Chọn chế độ:
    ├── ⚔️ GIỮ NƯỚC  → thẳng vào loadout (chỉ towers cơ bản, không coins, không tuyệt chiêu) → TD
    └── 🏗️ DỰNG NƯỚC → Bước 1: Quiz → Bước 2: Minigame → Bước 3: Loadout → TD
```

### 9.2 Chế độ GIỮ NƯỚC (Hard Mode — vào thẳng)

- Bỏ qua toàn bộ phần học
- Loadout: chỉ 2 tháp mặc định (Nỏ Liên Châu + Bẫy Nhựa), không mua thêm được
- Không có tuyệt chiêu (items slots bị khóa)
- Không có coins khởi đầu
- Mục đích: rất khó → thúc đẩy quay lại chơi Dựng Nước

### 9.3 Chế độ DỰNG NƯỚC (Learning Mode — 3 bước)

**Bước 1 — Quiz (battle.html):**
- Học lý thuyết + làm bài tập dạng quiz
- Mỗi câu đúng = +50 coins (lưu vào localStorage `vs_coins_ai{N}`)
- Đúng >80% = unlock tuyệt chiêu (không cần minigame)
- Đúng 100% = +200 coins bonus

**Bước 2 — Minigame Tuyệt Chiêu (tuỳ chọn, song song với quiz):**
- minigame.html → Tuyệt Chiêu 1 (TC1) — unlock slot items 1
- minigame2.html → Tuyệt Chiêu 2 (TC2) — unlock slot items 2
- Thắng minigame = unlock tuyệt chiêu đó (độc lập với quiz %)
- **Điều kiện unlock tuyệt chiêu:** minigame thắng ✅ **HOẶC** quiz >80% ✅ (1 trong 2 đủ)

**Bước 3 — Pre-Game Loadout (GameMissionPrepForm style FR2):**
```
Tab 1 — CHỌN THÁP (6 slots):
  • Nỏ Liên Châu [FREE — mặc định]
  • Bẫy Nhựa     [FREE — mặc định]
  • Thần Cơ Pháo [150 coins]
  • Hỏa Tháp     [200 coins]
  • Lôi Tháp     [300 coins]
  • Trống Lệnh   [250 coins]
  → Coins = tổng kiếm được từ quiz Bước 1
  → HasPlayerEquippedGoodTowers() check trước khi cho vào game

Tab 2 — TUYỆT CHIÊU / ITEMS (3 slots):
  • Slot 1: TC1 — chỉ active nếu minigame1 thắng HOẶC quiz >80%
  • Slot 2: TC2 — chỉ active nếu minigame2 thắng HOẶC quiz >80%
  • Slot 3: Đòn Trời (airstrike) — luôn available khi Dựng Nước
  → Slot bị khóa = hiện icon 🔒 + tooltip hướng dẫn mở
```

**Bước 4 — Đại Việt Defender gameplay (tower_defense.html):**
- Nhận towers + items đã chọn qua URL params hoặc localStorage
- Gameplay FR2-style: đặt tháp, combo kills, airstrike meter

### 9.4 Mapping FR2 → Đại Việt Defense

| FR2 | Đại Việt Defense | Nguồn unlock |
|-----|-----------------|--------------|
| `GameMissionPrepForm` | Màn Loadout (Tab Tháp + Tab Tuyệt Chiêu) | Sau quiz/minigame |
| Tower selection (6 slots) | Chọn tháp | Mua bằng coins từ quiz |
| Items/Abilities (3 slots) | Tuyệt Chiêu | Minigame thắng HOẶC quiz >80% |
| Airstrike meter (`gAirstrikeMeterMaxPoints`) | Đòn Trời ⚡ | Tích lũy khi giết quân trong TD |
| Combo kills (`gDefaultMinComboRequirement`) | Chuỗi tiêu diệt | Giết liên tiếp <1s |
| Gold/coins in-game | Vàng Đông Sơn | Từ quiz (trước game) + giết quân (trong game) |
| Stars 1-3 (`Star_Meter_Fill`) | Sao Cổ Loa ⭐⭐⭐ | Hoàn thành wave, ít mạng mất |
| `Enemy_Escaped` event | Mạng bị cắt | Địch thoát qua exit |
| `Overdrive_Available` SFX | Đòn Trời sẵn sàng | Meter 100% |

### 9.5 Screens cần build cho MVP Cổ Loa

| # | File | Status |
|---|------|--------|
| 1 | `intro.html` — cốt truyện + chọn Dựng/Giữ nước | Có nhưng chưa có mode select |
| 2 | `battle.html?ai=7` — Quiz Ải 7 + cộng coins | ✅ DONE |
| 3 | `battle.html?ai=8` — Quiz Ải 8 + cộng coins | TODO |
| 4 | `minigame.html` — TC1 Ải 7 | ✅ DONE |
| 5 | `minigame2.html` — TC2 Ải 7 | ✅ DONE |
| 6 | Minigame TC1 Ải 8 | TODO |
| 7 | `loadout.html` — GameMissionPrepForm (chọn tháp + tuyệt chiêu) | TODO (NEW) |
| 8 | `tower_defense.html` — nhận loadout state, gameplay | Có, cần kết nối |
| 9 | Win/Lose screen với stars + coins earned | TODO |

### 9.6 State truyền giữa các màn (localStorage keys)

```
vs_mode_ai{N}        = "dungnuoc" | "giunuoc"
vs_coins_ai{N}       = số nguyên (tích lũy từ quiz)
vs_quiz_pct_ai{N}    = phần trăm đúng (0-100)
vs_tc1_ai{N}         = true/false (minigame1 thắng)
vs_tc2_ai{N}         = true/false (minigame2 thắng)
vs_loadout_towers    = JSON array tên towers đã chọn
vs_loadout_items     = JSON array tuyệt chiêu đã chọn
```

### 9.7 Coins Economy

| Nguồn | Coins |
|-------|-------|
| Quiz đúng 1 câu | +50 |
| Quiz đúng >80% bonus | +200 |
| Giết quân trong TD | +10–50 |
| Khởi đầu Dựng Nước | +100 |

| Tower | Giá |
|-------|-----|
| Nỏ Liên Châu | Free (default) |
| Bẫy Nhựa | Free (default) |
| Thần Cơ Pháo | 150 coins |
| Hỏa Tháp | 200 coins |
| Lôi Tháp | 300 coins |
| Trống Lệnh (buff) | 250 coins |

### 9.8 Mapping Ải → Nội dung học

| Ải | Zone | Quiz chủ đề | TC1 | TC2 |
|----|------|------------|-----|-----|
| 7 | Cổ Loa | Phân biệt Số/Chữ số + Cấu tạo số | Thần Nhãn Vị Số | Bút Pháp Thiên Cơ |
| 8 | Cổ Loa | Viết thêm chữ số + Tìm số ẩn | TC1 Ải 8 (TODO) | TC2 Ải 8 (TODO) |
