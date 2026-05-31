# VINASTUDY BOT - BATTLE ARENA PROJECT CONTEXT

Tài liệu này chứa toàn bộ ngữ cảnh, quy chuẩn thiết kế và cấu trúc kỹ thuật mới nhất của dự án "VinaStudy Bot - Chiến binh Toán học". Hãy đọc kỹ tài liệu này trước khi thực hiện bất kỳ thay đổi nào để đảm bảo tính đồng bộ của dự án.

## 1. Tổng quan dự án
- **Mục tiêu:** Chuyển đổi các bài tập Toán học dạng danh sách nhàm chán thành một **Mini-game nhập vai (RPG) phong cách Cyberpunk / Sci-fi** ngay trên giao diện Telegram WebApp.
- **Tech Stack:** Vanilla HTML, CSS, JavaScript (Không sử dụng Framework nặng để đảm bảo tốc độ tải trên Telegram WebApp).

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

## 9. GAME DESIGN MỚI — Đại Việt Defender (MVP Cổ Loa)

### 9.1 Luồng chính (User Flow)

```
Telegram bot → Đăng ký → Được duyệt → Map
→ Chọn Zone Cổ Loa (Ải 7/8)
→ [INTRO SCREEN] Chọn chế độ:
    ├── 🏗️ DỰNG NƯỚC (học + chơi)
    └── ⚔️ GIỮ NƯỚC (chỉ chơi TD, không học)
```

### 9.2 Chế độ DỰNG NƯỚC (Learning Mode)

**Bước 1 — Học Quiz:**
- Màn học lý thuyết (battle.html intro/theory screens)
- Quiz bài tập → đúng >80% = đủ điều kiện mở items
- Mỗi câu đúng = +50 coins (dùng mua tower)
- Đúng hết = +bonus 200 coins

**Bước 2 — Minigame Tuyệt Chiêu:**
- minigame.html = Tuyệt Chiêu 1 (items slot 1)
- minigame2.html = Tuyệt Chiêu 2 (items slot 2)
- Thắng minigame = unlock tuyệt chiêu tương ứng

**Bước 3 — Pre-Game Loadout (FR2 style GameMissionPrepForm):**
```
┌─────────────────────────────────────┐
│  CHỌN THÁP (6 slots)                │
│  [Nỏ Liên Châu] [Bẫy Nhựa] [...]  │
│  Mặc định: 2 tháp cơ bản           │
│  Mua thêm = dùng coins từ quiz      │
├─────────────────────────────────────┤
│  TUYỆT CHIÊU (items, 3 slots)       │
│  [Bom Thần] [Đông Băng] [Vàng Thêm]│
│  Chỉ có nếu: minigame ✅ hoặc quiz >80% │
└─────────────────────────────────────┘
```

**Bước 4 — Đại Việt Defender (Tower Defense):**
- Có đủ towers và items đã chọn
- Gameplay như Fieldrunners 2

### 9.3 Chế độ GIỮ NƯỚC (Hard Mode)

- Vào thẳng Đại Việt Defender
- Chỉ có 2 towers cơ bản (Nỏ Liên Châu + Bẫy Nhựa)
- Không có coins (không mua thêm được)
- Không có tuyệt chiêu/items
- Rất khó → thúc đẩy chơi lại theo chế độ Dựng Nước

### 9.4 Mapping FR2 → Đại Việt Defense

| FR2 | Đại Việt Defense | Nguồn unlock |
|-----|-----------------|-------------|
| Tower selection | Chọn tháp (6 slots) | Mua bằng coins quiz |
| Items/Abilities | Tuyệt Chiêu (3 slots) | Minigame hoặc quiz >80% |
| Airstrike meter | Đòn Trời (⚡ meter) | Tích lũy khi giết quân |
| Combo kills | Chuỗi tiêu diệt | Giết liên tiếp < 1s |
| Gold/coins | Vàng Đông Sơn | Từ quiz + giết quân |
| Stars 1-3 | Sao Cổ Loa ⭐⭐⭐ | Hoàn thành wave, ít mất mạng |

### 9.5 Screens cần build cho MVP Cổ Loa

1. **Intro screen** — chọn Dựng nước / Giữ nước (NEW)
2. **Quiz screen** — câu hỏi bài tập, cộng coins (dùng battle.html theory+boss)
3. **Pre-game loadout** — chọn tower + items (NEW - GameMissionPrepForm)
4. **Đại Việt Defender gameplay** — tower_defense.html nâng cấp
5. **Win/Lose screen** — stars, coins earned, unlock Ải tiếp

### 9.6 Coins Economy

| Nguồn | Coins |
|-------|-------|
| Quiz đúng 1 câu | +50 |
| Quiz đúng >80% bonus | +200 |
| Giết quân trong TD | +10-50 |
| Bắt đầu mỗi ải | +100 (cơ bản) |

| Tower | Giá |
|-------|-----|
| Nỏ Liên Châu (mặc định) | Free |
| Bẫy Nhựa (mặc định) | Free |
| Thần Cơ Pháo | 150 coins |
| Hỏa Tháp | 200 coins |
| Lôi Tháp | 300 coins |
| Trống Lệnh (buff) | 250 coins |

### 9.7 Mapping Ải → Nội dung học

| Ải | Zone | Quiz chủ đề | Tuyệt Chiêu |
|-----|------|------------|-------------|
| Ải 7 | Cổ Loa | Phân biệt Số/Chữ số + Cấu tạo số | TC1: Thần Nhãn Vị Số |
| Ải 8 | Cổ Loa | Viết thêm chữ số + Tìm số ẩn | TC2: Bút Pháp Thiên Cơ |
