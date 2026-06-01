# ĐẠI VIỆT DEFENDER — MASTER STYLE GUIDE
## Visual language cho toàn bộ game assets

**STYLE REFERENCE FILES:**
- `design-system/MASTER_STYLE_REFERENCE.jpg` — Lính chibi Đại Việt (enemy/character style)
- `design-system/MAP_STYLE_REFERENCE.jpg` — Thành Cổ Loa aerial (map/environment style)

Hai file này là **chuẩn mực tuyệt đối**. Mọi asset phải match một trong hai reference.

---

## 1. CHARACTER STYLE DNA

### Tỷ lệ nhân vật
- **Chibi 1:1.5** — đầu chiếm ~35% tổng chiều cao
- Tay và chân ngắn, cơ thể compact, biểu cảm phóng đại
- Không photorealistic — stylized 3D cinematic

### Giáp & vũ khí
- **Sắt rèn** màu xám tối `#2A2A3A` với texture hammered/worn
- **Viền đồng vàng** `#C8960C` trên mép giáp và khớp nối
- **Hoa văn Đông Sơn** khắc chìm trên mặt giáp (pattern hình học vuông xoắn ốc)
- Vũ khí: đồng/sắt cổ đại — giáo, kiếm, nỏ, trống đồng

### Màu sắc
| Token | Hex | Dùng cho |
|-------|-----|---------|
| Đỏ son | `#C0332E` | Vải, cờ, điểm nhấn |
| Vàng đồng | `#C8960C` | Viền giáp, huy hiệu |
| Sắt đen | `#2A2A3A` | Giáp, vũ khí |
| Đỏ thẫm | `#8B0000` | Khăn quàng, áo lót |
| Đất nâu | `#6B3A2A` | Da, gỗ |

### Ánh sáng & atmosphere
- **Key light**: Warm orange-red từ phía trước-dưới (như lửa trận)
- **Rim light**: Ánh lửa vàng từ phía sau
- **Particles**: Tàn lửa nhỏ, bụi đất đỏ bay
- **Background**: Bầu trời đỏ cam kịch tính, khói chiến trường
- **Mood**: Epic, fierce, Đại Việt lịch sử hào hùng

---

## 2. TOWER STYLE DNA

Towers = vũ khí chiến tranh cổ đại đặt trên **đế đồng tròn Đông Sơn**:
- Level 1: Vũ khí đơn giản, đế gỗ/đồng nhỏ
- Level 2: Có bệ đỡ cao hơn, thêm chi tiết
- Level 3: Kiến trúc đầy đủ, chạm khắc Đông Sơn rực rỡ

**Style**: 3/4 isometric từ trên xuống, nền trắng, bóng đổ nhẹ
**Reference**: `daiviet_defense/assets/icons/icon_arrow.png`

---

## 3. ENEMY SPRITE DNA

Dựa trực tiếp từ MASTER_STYLE_REFERENCE.jpg:
- Lính chibi tỷ lệ 1:1.5, giáp Đông Sơn
- Mỗi loại lính có màu vải khác nhau (đỏ=thường, xanh=kị binh, đen=tinh nhuệ)
- Animation: chạy compact, dứt khoát, hơi cường điệu

---

## 4. BASE PROMPT TEMPLATE

### Cho nhân vật/lính:
```
[MÔ TẢ NHÂN VẬT], chibi 1:1.5 proportion Vietnamese ancient warrior,
dark hammered iron armor with Đông Sơn geometric engravings and gold-bronze trim,
crimson red fabric scarf, fierce expression,
dramatic warm orange-red battlefield lighting with fire sparks,
3D cinematic stylized render, high quality,
[GÓC NHÌN: top-down / side view / 3/4 isometric]
```

### Cho tower icons:
```
Stylized 3D game icon, ancient Vietnamese [TÊN VŨ KHÍ],
sitting on LOW FLAT CIRCULAR BRONZE BASE with Đông Sơn engravings,
dark hammered iron and gold-bronze tones #C8960C,
3/4 isometric view slightly from above, object ~60% frame height,
white background, soft drop shadow, stylized NOT photorealistic
```

### Cho map/environment:
```
Top-down tower defense game map background, ancient Vietnamese Đại Việt Cổ Loa theme,
aerial view, lush bright green rice paddy fields, winding blue rivers and moats,
karst limestone mountains on edges, golden sunset warm lighting from far horizon,
Vietnamese wooden watchtowers with red-brown tiled roofs at fortress gates,
Cổ Loa spiral concentric stone walls, tall green rounded trees,
hand-painted cinematic game art, vibrant saturated colors, epic atmosphere,
NO characters, NO path drawn, flat playable terrain in center
```

**Reference file:** `design-system/MAP_STYLE_REFERENCE.jpg`

**Map Style DNA:**
- Góc nhìn: Aerial ~75° (slightly angled top-down)
- Màu chủ: Xanh lá #4A8A2A, Xanh nước #3A7AB8, Vàng hoàng hôn #E8900C
- Địa hình đặc trưng: Thành xoắn ốc Cổ Loa, ruộng bậc thang, sông uốn, núi karst
- Kiến trúc: Tháp gỗ mái ngói, cổng thành đá cuội, đèn lồng đỏ
- Atmosphere: Golden hour sunset, warm haze, depth of field xa

---

## 5. NEGATIVE PROMPT CHUNG (dùng cho tất cả)
```
modern, sci-fi, western fantasy, photorealistic skin, blurry, 
watermark, text, frame border, Chinese/Japanese/Korean style,
low quality, duplicate, distorted anatomy
```

---

## 6. LEONARDO SETTINGS CHUẨN

- **Model**: Phoenix hoặc Leonardo Diffusion XL
- **Style**: None (để model tự quyết)
- **Guidance**: 7
- **Image Reference**: `MASTER_STYLE_REFERENCE.jpg` strength **0.25-0.35**
- **Variations**: 4 phương án, chọn 1 tốt nhất
- **Resolution**: 256×256 (icons), 512×512 (enemies), 2048×1136 (maps)
