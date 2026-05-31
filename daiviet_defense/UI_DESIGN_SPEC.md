# ĐẠI VIỆT DEFENSE — UI/UX DESIGN SPEC
## Inspired by tower defense game conventions, designed with Đại Việt aesthetic

**Style direction:** Đại Việt cổ kính + cyberpunk neon accents (hybrid)
**Color palette:**
- Primary: `#C8960C` (vàng đồng Đông Sơn)
- Secondary: `#C0332E` (đỏ son)
- Accent: `#B87333` (đồng cổ)
- Success: `#5ABCAA` (ngọc bích)
- Bg dark: `#07040A` (mực tàu)
- Text: `#F5EED6` (ngà voi)

**Fonts:**
- Title: `Philosopher, serif` (đã có)
- Body: `Lora, serif` (đã có)
- Mono: `Roboto Mono` (số liệu)

---

## 1. WORLD MAP SCREEN (đã có trong map.html)

```
┌────────────────────────────────────────┐
│  [Avatar] Cao Lỗ  ⚡120 [📊] [🏛️]    │ ← Header (CÓ RỒI)
├────────────────────────────────────────┤
│                                        │
│  🗺️  GEO MAP (Vietnam shape)           │
│                                        │
│    🏛️ Ải 1 ─────🏰 Ải 2               │ ← Nodes có:
│    ⭐⭐⭐         ⭐⭐                    │   - emoji boss
│         \         /                    │   - star rating
│          🌊 Ải 3 ────⚓ Ải 4           │   - locked overlay
│          ⭐         🔒                  │
│                                        │
└────────────────────────────────────────┘
```

**Status:** ✅ ĐÃ CÓ — chỉ cần polish thêm:
- [ ] Animated path giữa các ải (nét đứt vàng di chuyển)
- [ ] Star rating hiển thị 1/2/3 sao
- [ ] Boss preview pop-up khi hover/long-press

---

## 2. PRE-LEVEL TOWER SELECTION SCREEN (CHƯA CÓ)

Mới — trước khi vào ải, player chọn 6 trong 9 tháp:

```
┌────────────────────────────────────────┐
│   🏛️ ẢI 3: BẠCH ĐẰNG                  │ ← Title bar đỏ son
│   Boss: 🐍 Hắc Long  | HP: 500         │
│   Wave: 1-15  | Khó: ⚔️⚔️⚔️           │
├────────────────────────────────────────┤
│                                        │
│   CHỌN 6 THÁP (tối đa):               │
│   ┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐│
│   │ 🏹 ││ 💧 ││ 💣 ││ 🔥 ││ ⚡ ││ 🪤 ││ ← 9 tháp
│   │ Nỏ ││Nhựa││Pháo││Hỏa ││Sét ││Chông││   horizontal scroll
│   └────┘└────┘└────┘└────┘└────┘└────┘│
│                                        │
│   CHỌN 3 ITEM:                        │
│   ┌────┐┌────┐┌────┐                  │
│   │ 💣 ││ ❄️ ││ 💰 │                  │
│   └────┘└────┘└────┘                  │
│                                        │
│   [QUAY LẠI]    [BẮT ĐẦU CHIẾN]      │
└────────────────────────────────────────┘
```

**Element cần làm:**
- `tower_card_empty.png` (slot trống chờ chọn)
- `tower_card_selected.png` (slot đã chọn, vàng glow)
- `tower_card_locked.png` (chưa unlock, xám)
- `boss_preview.png` (avatar boss của ải đó)

---

## 3. IN-GAME HUD (đang có nhưng cần polish)

```
┌────────────────────────────────────────┐
│ ❤️ 30/30  💰 350  🌊 Wave 1/15  📊 0  │ ← Top bar
├────────────────────────────────────────┤
│ ⚡▓▓▓▓░░░░░  COMBO x5 🔥             │ ← Airstrike + Combo
├────────────────────────────────────────┤
│                                        │
│    [GAME CANVAS]                       │
│                                        │
├────────────────────────────────────────┤
│ 🏹 💧 💣 🔥 ⚡ 🥁 🪤        ▶ ⚡ 👁 ✈│ ← Bottom bar
│  Build Tower buttons        Controls    │
└────────────────────────────────────────┘
```

**Status:** ✅ ĐÃ CÓ, cần polish:
- [ ] Top bar nền **bảng đồng Đông Sơn** với hoạ tiết khắc cổ
- [ ] HP heart pulse khi <20%
- [ ] Gold counter **chữ Hán** kế bên số
- [ ] Wave counter dạng **kinh sử** (thẻ tre)

---

## 4. TOWER INFO PANEL (chọn tháp đã đặt)

```
┌────────────────────────────────────────┐
│  [Tower sprite]  NỎ LIÊN CHÂU Lv.2    │
│                  ⭐⭐                  │
│                                        │
│  Sát thương: 18 → 35 (next)           │
│  Tầm bắn: 135 → 160                   │
│  Tốc độ: 0.65s/shot                   │
│                                        │
│  🎯 MỤC TIÊU:                         │
│  [⬆ Đầu] [⬇ Cuối] [💪 Mạnh] [❤️ Yếu]│
│                                        │
│  [⬆ Nâng cấp 💰50]  [❌ Bán 💰30]    │
└────────────────────────────────────────┘
```

**Status:** ✅ ĐÃ CÓ — polish thêm:
- [ ] Tower sprite preview (placeholder hiện chỉ text)
- [ ] Stat bars (progress bar visual cho damage/range)
- [ ] Range circle nhấp nháy trên canvas khi panel mở

---

## 5. VICTORY / DEFEAT SCREEN

```
┌────────────────────────────────────────┐
│                                        │
│      🏆 CHIẾN THẮNG OAI HÙNG! 🏆      │
│                                        │
│         ⭐⭐⭐ Hoàn hảo!                │
│                                        │
│  Wave hoàn thành: 15/15                │
│  Combo cao nhất: x18                   │
│  Điểm: 4,250                           │
│  Vàng thừa: 580                        │
│  Lives còn: 28/30                      │
│                                        │
│  🎁 Phần thưởng:                       │
│  + 100 Toán Lực                        │
│  + Mở khoá: Ải 4                       │
│                                        │
│  [QUAY LẠI BẢN ĐỒ]  [CHƠI LẠI]       │
└────────────────────────────────────────┘
```

**Status:** ⚠️ CÓ NHƯNG SƠ SÀI — cần làm:
- [ ] Star rating animation (1→2→3 sao xuất hiện lần lượt)
- [ ] Score counter đếm lên animated
- [ ] Confetti particle effect
- [ ] Boss head silhouette với "Defeated" stamp

---

## 6. WAVE BANNER (giữa game)

```
   ╔══════════════════════════════╗
   ║   ⚔️ ĐỢT 8 — KHÔNG QUÂN! ⚔️ ║
   ╚══════════════════════════════╝
```

Status: ✅ ĐÃ CÓ — polish:
- [ ] Banner shape giống **trống đồng Đông Sơn** (hình tròn)
- [ ] Slide in từ trên + rotate nhẹ
- [ ] Particle vàng đồng bay xung quanh

---

# 🎨 AI IMAGE GENERATION PROMPTS

## A. Tower Cards (cho Pre-level selection)

### A1. Tower icon background
**Prompt cho Midjourney/DALL-E:**
```
ancient Vietnamese bronze plaque background, Đông Sơn drum pattern engraved,
weathered patina copper texture, ornate border with lotus motifs,
empty center frame for icon placement, square format 200x200px,
isometric view slight angle, game UI asset transparent background,
Đại Việt aesthetic style, no text, no characters, --ar 1:1 --style raw
```

### A2. Tower icons (9 tháp)

**Nỏ Liên Châu (Arrow):**
```
ancient Vietnamese crossbow tower top-down view game icon,
multi-shot repeating crossbow with bronze details, bamboo construction,
Cao Lỗ's invention, isometric 3/4 view, 256x256px transparent,
hand-drawn game art style, Đại Việt warrior aesthetic --ar 1:1
```

**Bẫy Nhựa (Slow/Goo):**
```
ancient Vietnamese sap trap tower top-down game icon,
hollow bamboo container with green sticky liquid bubbling,
jade-green glow, isometric 3/4 view, 256x256px transparent background,
hand-drawn game art style --ar 1:1
```

**Thần Cơ Pháo (Cannon):**
```
ancient Vietnamese bronze cannon Đông Sơn drum style game icon,
large bronze barrel with embossed dragon engravings,
mounted on wooden carriage, isometric 3/4 view, 256x256px transparent,
Đại Việt warrior aesthetic, hand-drawn game art --ar 1:1
```

**Hỏa Tháp (Flame):**
```
ancient Vietnamese flame tower top-down game icon,
bronze brazier on wooden tower with continuous flames,
dragon-mouth flame spout, red and orange glow, isometric 3/4 view,
256x256px transparent, Đại Việt aesthetic --ar 1:1
```

**Lôi Tháp (Tesla/Lightning):**
```
ancient Vietnamese mystical lightning tower game icon,
bronze tower with crystal orb on top emitting blue lightning,
Taoist symbols carved on base, ethereal lightning bolts,
isometric 3/4 view, 256x256px transparent --ar 1:1
```

**Trống Lệnh (Power buff):**
```
ancient Vietnamese command drum tower top-down game icon,
giant Đông Sơn bronze drum on wooden platform with banner flags,
golden command staff in stand, ceremonial atmosphere,
isometric 3/4 view, 256x256px transparent --ar 1:1
```

**Bãi Chông (Mine field):**
```
ancient Vietnamese bamboo spike trap field game icon,
sharpened bamboo stakes arranged in circular pattern in earth,
hidden trap, top-down view, 256x256px transparent,
Đại Việt warrior aesthetic --ar 1:1
```

---

## B. Boss / Enemy Avatars

### B1. Bạch Kê Tinh (Ải 1 boss)
```
ancient Vietnamese folklore evil rooster spirit demon boss,
giant white rooster with glowing red eyes, 9 magical feathers,
mystical aura, dark fog around, isometric 3/4 game character,
512x512px transparent background, hand-drawn Vietnamese folklore style --ar 1:1
```

### B2. Ám Toán Sứ (Ải 2 boss)
```
ancient Vietnamese shadow envoy demon boss,
dark shrouded figure with calligraphy brush as weapon,
floating Chinese numerals around him glowing red,
mystical evil aura, 512x512px transparent --ar 1:1
```

### B3. Đại Tướng Quỷ Số (Final boss)
```
ancient Vietnamese great demon general boss character,
armored skeleton warrior with golden crown and bronze spear,
purple mystical aura, intimidating war pose, 512x512px transparent,
Đại Việt folklore aesthetic, isometric 3/4 view --ar 1:1
```

---

## C. UI Panels

### C1. Top HUD bar background
```
ancient Vietnamese bronze plaque horizontal banner UI,
Đông Sơn drum patterns engraved on aged copper,
weathered patina texture, ornate lotus motif border,
2048x128px transparent background top edge fade,
game UI asset, no text --ar 16:1
```

### C2. Bottom tower selection bar background
```
ancient Vietnamese wooden scroll bar UI horizontal,
weathered dark wood with bronze rivets,
6 rectangular slots for tower icons,
2048x256px transparent, ornate Đại Việt carvings on edges,
game UI asset --ar 8:1
```

### C3. Wave banner (Đông Sơn drum shape)
```
ancient Vietnamese Đông Sơn bronze drum circular banner UI,
detailed center sun motif with rays, concentric rings of carvings,
gold and copper colors, glowing edges, 1024x1024px transparent,
game UI announcement banner --ar 1:1
```

---

## D. Game State Screens

### D1. Victory screen background
```
ancient Vietnamese victory celebration scene background,
Đại Việt warriors raising flags on fortress walls,
sunset golden light, dragon banner waving, particles of light,
1920x1080px game victory screen background --ar 16:9
```

### D2. Defeat screen background
```
ancient Vietnamese fallen fortress sad scene background,
broken Cổ Loa walls in twilight, abandoned weapons,
gray sad atmosphere, single lone warrior silhouette,
1920x1080px game defeat screen background --ar 16:9
```

---

## E. Decorative Elements

### E1. Star rating (1/2/3 sao)
```
ancient Vietnamese bronze star medal game asset,
ornate lotus pattern star with copper patina,
glowing golden edges, 128x128px transparent,
game achievement star icon --ar 1:1
```

### E2. Border frames
```
ancient Vietnamese ornate corner border frame ornament,
Đông Sơn drum patterns at corners, dragon scroll details,
gold copper color, 256x256px transparent,
game UI decorative corner asset --ar 1:1
```

---

# 📋 ASSET PRODUCTION CHECKLIST

## Tier 1 — Critical (làm trước)
- [ ] 9 tower icons (256x256) — A2 prompts
- [ ] HUD top bar bg (C1)
- [ ] Tower selection bottom bar (C2)
- [ ] Wave banner Đông Sơn drum (C3)

## Tier 2 — Important
- [ ] Tower card empty/selected/locked (A1)
- [ ] 3 item icons (bom/freeze/gold)
- [ ] Victory + Defeat backgrounds (D1, D2)
- [ ] Star rating medal (E1)

## Tier 3 — Polish
- [ ] 3-5 boss avatars (B1, B2, B3...)
- [ ] Border frames (E2)
- [ ] Particle textures (ánh sao, ánh vàng)

---

# 🎯 KHUYẾN NGHỊ TOOLS

| Tool | Pro | Con | Phù hợp |
|---|---|---|---|
| **Midjourney** | Chất lượng cao nhất, style consistent | $30/tháng | Boss avatars, backgrounds |
| **DALL-E 3 (ChatGPT)** | Free w/ ChatGPT Plus, hiểu prompt tốt | Khó control style | Tower icons, items |
| **Leonardo.ai** | Free tier 150/ngày | Chất lượng vừa | Bulk produce icons |
| **Stable Diffusion (ComfyUI)** | Free, full control | Cần GPU | Khi muốn iterate nhanh |

**Đề xuất:** Dùng **Leonardo.ai** (free) cho 9 tower icons + 3 item icons (12 ảnh) → đủ Tier 1.

---

# 📐 SỬA CODE TRONG GAME KHI CÓ ẢNH

Khi có ảnh, sửa code:

```javascript
// Trong assets object:
const assets = {
    arrow_tower: new Image(),
    // ... existing
    // NEW:
    tower_card_empty: new Image(),
    tower_card_selected: new Image(),
    hud_top_bar: new Image(),
    wave_banner: new Image(),
    boss_bach_ke_tinh: new Image(),
    item_bomb: new Image(),
    item_freeze: new Image(),
    item_gold: new Image(),
};
```

Bạn generate được ảnh nào, gửi tôi → tôi integrate vào code.
