# FIELDRUNNERS 2 — APK DECODE ANALYSIS
## Phân tích cấu trúc file để clone Đại Việt Defense

**Source:** `com.subatomicstudios.fieldrunners2_1.8-APK_Award.apk` (70.4 MB)  
**Engine:** Custom C++ (libgame.so 3.8 MB)  
**Audio Engine:** FMOD (libfmodevent.so + libfmodex.so)  
**Assets:** 2782 files, 81.4 MB (tất cả encrypted XOR, numbered 00000000-00002781)

---

## 1. FILE STRUCTURE TỔNG QUAN

```
fr2.apk (70.4 MB)
├── assets/                    ← 2782 files, 81.4 MB (ALL encrypted)
├── lib/
│   └── armeabi-v7a/
│       ├── libgame.so         ← 3.8 MB (game engine C++)
│       ├── libfmodevent.so    ← 362 KB (FMOD event system)
│       └── libfmodex.so       ← 851 KB (FMOD audio engine)
├── res/                       ← 419 files, 0.5 MB (Android UI resources)
├── classes.dex                ← 3.4 MB (Java launcher)
├── AndroidManifest.xml
└── resources.arsc
```

---

## 2. ASSETS PHÂN LOẠI THEO KÍCH THƯỚC

| Category | Files | Total Size | Likely Content |
|---|---|---|---|
| **LARGE (>1MB)** | 11 | 35.2 MB | Texture atlases (world map, backgrounds) |
| **MEDIUM (200KB-1MB)** | 24 | 14.9 MB | Audio tracks (BGM) + large sprite sheets |
| **SPRITE_SHEET (50-200KB)** | 152 | 12.7 MB | Tower/enemy sprite sheets, UI panels |
| **SMALL_SPRITE (10-50KB)** | 562 | 12.8 MB | Individual sprites, icons, particles |
| **CONFIG (<10KB)** | 2033 | 5.9 MB | Level configs, archetypes, animations, scripts |
| **TỔNG** | **2782** | **81.4 MB** | |

---

## 3. AUDIO SYSTEM (FMOD)

### Đã tìm thấy từ binary strings:

**FMOD Event File:**
- `FR2.fev` ← Master event bank (chứa tất cả SFX + music references)

**Music:**
- `Music_Theme.mp3` ← Main theme

**FMOD Event Paths (SFX categories):**
```
Enemies/
  Enemy_Air_Plane_Fokker_Light/Spawn
  Enemy_Soldier_Light/Spawn

UI/In_Game/
  Enemy_Escaped          ← khi địch thoát
  Invalid                ← click vị trí không hợp lệ
  Overdrive_Available    ← airstrike meter đầy
  Player_Low_Health      ← cảnh báo sắp thua
  Score_Counted
  Score_Counting_Down
  Score_Counting_Up
  Star_Meter_Fill
  Tower_Drag_Cancel      ← huỷ đặt tháp
  Victory_Cheer          ← thắng wave

UI/Licks/
  Defeat                 ← nhạc thua
  Victory                ← nhạc thắng

UI/Menu/
  Button_Press_Down      ← click UI
  Card_Out               ← chọn tower card
  FlipCard_Single        ← lật thẻ
  Scroll_FlipCard        ← scroll menu

Common/Explosions/
  Explosion_Airstrike    ← nổ airstrike
```

**Sound Config Keys:**
```
gSoundEnemyEscaped           ← SFX khi địch thoát
gSoundAirstrikeJet           ← SFX máy bay airstrike
gSoundOverdriveAvailable     ← SFX overdrive ready
gMusicDefaultVolume          ← volume nhạc mặc định
gMusicFadeInMilliseconds     ← fade in time
gMusicFadeOutMilliseconds    ← fade out time
gSoundEffectsDefaultVolume   ← volume SFX mặc định
gSoundGameSpeedPitchFactor   ← pitch thay đổi khi tăng tốc
gSoundLowPlayerHealthPitchFactor ← pitch khi sắp thua
```

### → DANH SÁCH AUDIO CẦN TẠO MỚI (SUNO + SFX)

**BGM (8 tracks — Suno AI):**
```
[ ] daiviet_battle_main.mp3     ← gameplay chính (loop)
[ ] daiviet_battle_intense.mp3  ← wave cao / boss (loop)
[ ] co_loa_theme.mp3            ← map Cổ Loa (loop)
[ ] bach_dang_theme.mp3         ← map Bạch Đằng (loop)
[ ] me_linh_theme.mp3           ← map Mê Linh (loop)
[ ] boss_wave.mp3               ← boss xuất kích (60s loop)
[ ] victory_daiviet.mp3         ← chiến thắng (30s, no loop)
[ ] defeat_daiviet.mp3          ← thất bại (20s, no loop)
```

**SFX (đã có Kenney CC0 — chỉ cần map):**
```
[✓] shoot_arrow_0-4.ogg        ← 5 variants nỏ bắn
[✓] shoot_bomb.ogg             ← pháo đồng
[✓] shoot_slow.ogg             ← goo/nhựa
[✓] shoot_flame.ogg            ← lửa phun
[✓] shoot_tesla.ogg            ← sét đánh
[✓] explode_big.ogg            ← nổ lớn
[✓] explode_sub.ogg            ← nổ trầm
[✓] hit_0-4.ogg                ← 5 variants trúng đích
[✓] buy.ogg                    ← mua tháp (coins)
[✓] deny.ogg                   ← click sai (metal)
[✓] leak.ogg                   ← địch thoát

CẦN THÊM:
[ ] enemy_spawn.ogg            ← địch xuất hiện
[ ] enemy_die_soldier.ogg      ← binh chết
[ ] enemy_die_heavy.ogg        ← voi/tank chết
[ ] enemy_die_air.ogg          ← không quân rơi
[ ] airstrike_incoming.ogg     ← máy bay lao tới
[ ] airstrike_explode.ogg      ← nổ airstrike
[ ] overdrive_ready.ogg        ← meter đầy
[ ] combo_hit.ogg              ← combo kill
[ ] mega_combo.ogg             ← mega combo
[ ] wave_start_horn.ogg        ← kèn báo wave
[ ] low_health_alarm.ogg       ← cảnh báo sắp thua
[ ] tower_upgrade.ogg          ← nâng cấp tháp
[ ] tower_sell.ogg             ← bán tháp
[ ] ui_button_click.ogg        ← click menu
[ ] ui_card_flip.ogg           ← chọn tháp (lật thẻ)
[ ] star_fill.ogg              ← nhận sao
```

---

## 4. MAP / LEVEL SYSTEM

### Maps tìm được từ binary:
```
Grasslands_Map1a.map     ← Zone 0: Đồng cỏ
Grasslands_Map3.map
Grasslands_Map4.map
Grasslands_Map5.map
City_Map0.map            ← Zone 1: Thành phố
City_Map2.map
Lavaflow_Map2.map        ← Zone 2: Núi lửa
Lavaflow_Map2a.map
Lavaflow_Map4.map
```

### Zone System (4 zones, mỗi zone có camera center riêng):
```
Zone 0: Grasslands   (gWorldMapZone0CameraCenterX/Y)
Zone 1: City/Desert  (gWorldMapZone1CameraCenterX/Y)
Zone 2: Lavaflow     (gWorldMapZone2CameraCenterX/Y)
Zone 3: Snow?        (gWorldMapZone3CameraCenterX/Y)
```

### Config files:
```
zones.cfg              ← zone definitions
enemyarchetypelist.cfg ← all enemy types
shop.cfg               ← tower shop / IAP
storePurchase.cfg      ← in-app purchases
achievements.cfg       ← achievement definitions
GameTips.cfg           ← tutorial tips
credits.cfg            ← credits
Localizable.csv        ← translations (all languages)
PlatformLocalizable.csv← platform-specific text
notifications.csv      ← push notifications
metadata.xml           ← game metadata
VersionList.txt        ← asset version manifest
```

### → DANH SÁCH MAP/LEVEL CẦN TẠO MỚI

```
ZONE 0 — ÂU LẠC (Cổ Loa):
[ ] co_loa_flat.json        ← Ải 1: thảo nguyên phẳng, 1 entry/exit
[ ] co_loa_hills.json       ← Ải 2: đồi + chướng ngại vật đá
[ ] co_loa_fortress.json    ← Ải 3: tường thành cố định

ZONE 1 — MÊ LINH (Hai Bà Trưng):
[ ] me_linh_jungle.json     ← Ải 4: rừng rậm, 2 entry points
[ ] me_linh_pass.json       ← Ải 5: đèo núi hẹp
[ ] me_linh_citadel.json    ← Ải 6: thành Mê Linh

ZONE 2 — BẠCH ĐẰNG (Ngô Quyền):
[ ] bach_dang_river.json    ← Ải 7: sông + 2 bờ, 3 entry
[ ] bach_dang_stakes.json   ← Ải 8: cọc nhọn pre-placed
[ ] bach_dang_ambush.json   ← Ải 9: phục kích, 4 entry

ZONE 3 — CỜ LAU (Đinh Bộ Lĩnh):
[ ] co_lau_valley.json      ← Ải 10: thung lũng phức tạp
[ ] co_lau_mountains.json   ← Ải 11: núi non hiểm trở
[ ] co_lau_throne.json      ← Ải 12: boss final, 4 entry
```

---

## 5. TOWER SYSTEM

### Tower Archetypes tìm được:
```
Tower_Polymorph.arc    ← biến hình địch thành dạng yếu
Tower_Power.arc        ← buff tháp lân cận
(25 towers total — tên khác lưu trong encrypted configs)
```

### Tower UI System:
```
GameMissionPrepForm      ← màn hình chọn tháp trước level
  HasPlayerEquippedGoodTowers() ← check player chọn đủ tháp
LoadTowerButtons()       ← load 6 tower slots
UpdateTowerButtons()     ← update available/locked state
OpenTowerMenu()          ← mở menu khi click tháp
CloseTowerMenu()         ← đóng
UpdateTowerMenu()        ← upgrade/sell panel
SetSelectedTowerArchetype() ← chọn loại tháp để đặt
```

### Tower Upgrade Effects:
```
Tower_Transition_Upgrade.fx   ← hiệu ứng nâng cấp lv1→2
Tower_Transition_Upgrade2.fx  ← hiệu ứng nâng cấp lv2→3
```

### Sprite naming pattern:
```
%s_v%d_%d.png → {tower_name}_v{version}_{frame}.png
Ví dụ: Gatling_v1_0.png, Gatling_v2_0.png, Gatling_v3_0.png
```

### → DANH SÁCH TOWER SPRITES CẦN TẠO MỚI

```
MỖI TOWER = base (3 levels) + turret (1 file rotate)
Format: 64x64 PNG, transparent background

5 TOWERS HIỆN CÓ:
[ ] nỏ_liên_châu_v1.png / _v2.png / _v3.png + _turret.png
[ ] bẫy_nhựa_v1.png / _v2.png / _v3.png + _turret.png
[ ] thần_cơ_pháo_v1.png / _v2.png / _v3.png + _turret.png
[ ] hỏa_tháp_v1.png / _v2.png / _v3.png + _turret.png
[ ] lôi_tháp_v1.png / _v2.png / _v3.png + _turret.png

TOWERS CẦN THÊM (clone FR2 mechanics):
[ ] power_tower_v1-3.png      ← buff tháp lân cận
[ ] polymorph_v1-3.png        ← biến hình
[ ] mine_tower_v1-3.png       ← rải mìn
[ ] laser_tower_v1-3.png      ← chùm laser cross

TOWER ICONS (cho tower selection menu):
[ ] icon_nỏ.png (32x32)
[ ] icon_bẫy.png
[ ] icon_pháo.png
[ ] icon_lửa.png
[ ] icon_sét.png
[ ] icon_power.png
[ ] icon_polymorph.png
[ ] icon_mine.png
[ ] icon_laser.png
```

---

## 6. ENEMY SYSTEM

### Enemy Archetypes tìm được:
```
Enemy_Soldier_Light.asc       ← bộ binh nhẹ (basic infantry)
Enemy_Soldier_Light.dol       ← 3D model data
Enemy_Air_Plane_Fokker_Light  ← không quân nhẹ (biplane)
Light_Soldier.arc             ← default spawn archetype
enemyarchetypelist.cfg        ← full list (encrypted)
```

### Enemy Event System:
```
Enemy_Escaped      ← khi 1 địch thoát qua exit
NotifyEnemyHit     ← khi tower bắn trúng
CheckLastEnemy     ← kiểm tra địch cuối cùng
IncrementEnemyEscaped ← đếm mạng mất
```

### → DANH SÁCH ENEMY SPRITES CẦN TẠO MỚI

```
MỖI ENEMY = walk spritesheet (4 dir × 4 frame) + death effect
Format: spritesheet PNG, transparent background

5 ENEMIES HIỆN CÓ:
[✓] Lính Trinh Sát (scout) — 1024x1024 static image
[✓] Bộ Binh (soldier) — 1024x1024 static image
[✓] Voi Chiến (heavy) — 1024x1024 static image
[✓] Quạ Sắt (air) — 1024x1024 static image
[✓] Đại Tướng (boss) — emoji only

CẦN NÂNG CẤP:
[ ] Tất cả enemy cần animated spritesheet (4 hướng × 4 frame)
    Hoặc giữ static + rotate theo hướng đi (đơn giản hơn)

ENEMIES CẦN THÊM MỚI (clone FR2):
[ ] medic_enemy.png       ← heal địch lân cận (green cross icon)
[ ] transport_enemy.png   ← drop 4 infantry khi chết
[ ] speed_enemy.png       ← áo xanh, immune slow
[ ] explosive_enemy.png   ← nổ khi chết, gây damage AoE
[ ] blimp_enemy.png       ← bay, HP cực cao, rất chậm
```

---

## 7. AIRSTRIKE / SPECIAL ATTACK SYSTEM

### Tìm được đầy đủ từ binary:

**Combo System:**
```
gDefaultComboBonus             ← điểm thưởng combo
gDefaultMegaComboBonus         ← điểm thưởng mega combo
gDefaultMinComboRequirement    ← số kill liên tục = 1 combo
gDefaultMinMegaComboRequirement← số kill = mega combo
Combo_Indicator.fx             ← particle effect combo
MegaCombo_Indicator.fx         ← particle effect mega
```

**Airstrike Meter:**
```
gAirstrikeMeterMaxPoints           ← điểm tối đa meter
gAirstrikeComboMeterChange         ← +bao nhiêu khi combo
gAirstrikePerfectMeterChange       ← +bao nhiêu khi perfect kill
gAirstrikeHealthLossMeterChange    ← +bao nhiêu khi mất mạng
```

**Airstrike Execution:**
```
gAirstrikeAttackTimer              ← thời gian tấn công
gAirstrikeAttackWidth              ← bề rộng vùng nổ
gAirstrikeCinematicDelayTime       ← delay cinematic
gAirstrikeEliteDamagePercent       ← % damage vs elite
gAirstrikeGridOffset               ← offset trên grid
Airstrike_Explosion.fx             ← particle nổ
gSoundAirstrikeJet                 ← SFX máy bay
Common/Explosions/Explosion_Airstrike ← FMOD event
```

### → IMPLEMENTATION CẦN LÀM

```
COMBO SYSTEM:
[ ] Đếm kills liên tiếp (enemy chết < 1s cách nhau)
[ ] Hiển thị "COMBO x3!" floating text
[ ] Mega combo (10+ kills) → "MEGA COMBO!" + gold bonus
[ ] Particle effects cho combo indicators

AIRSTRIKE METER:
[ ] UI: thanh meter bên cạnh (0-100%)
[ ] Tích điểm: +5% per kill, +15% per combo, +25% per mega
[ ] Khi 100%: nút ⚡ sáng lên, click để kích hoạt
[ ] Airstrike: máy bay bay qua, nổ dọc theo đường kẻ
[ ] Damage: giết hết enemy trong vùng nổ

ITEMS (3 consumables):
[ ] Bom thần (area damage tức thì)
[ ] Đông băng (freeze tất cả enemy 5s)
[ ] Vàng thêm (+50 gold ngay lập tức)
```

---

## 8. UI SPRITES CẦN TẠO

```
GAME HUD:
[ ] hud_gold_icon.png (24x24)
[ ] hud_heart_icon.png (24x24)
[ ] hud_wave_banner.png (full width, semi-transparent)
[ ] hud_airstrike_meter_bg.png
[ ] hud_airstrike_meter_fill.png
[ ] hud_combo_text_bg.png

TOWER SELECTION (pre-level):
[ ] tower_card_slot_empty.png (80x100)
[ ] tower_card_slot_locked.png
[ ] tower_card_selected_glow.png
[ ] tower_card_bg.png

PLACEMENT CURSORS:
[✓] PlacementCursorGood → green glow (code hiện tại)
[✓] PlacementCursorBad → red glow
[✓] Cursor → default mouse
[✓] Cursor_Invalid_Position → red X

MISC:
[ ] icon_sell.png (32x32) — đã có trong FR2
[ ] upgrade_star_empty.png
[ ] upgrade_star_filled.png
[ ] water_surface_tile.png — cho map Bạch Đằng
```

---

## 9. TỔNG HỢP TASK LIST

### PRIORITY 1 — Tuần 1-2 (Audio)
```
[ ] 8 BGM tracks (Suno AI)
[ ] 16 SFX files mới (Kenney CC0 + custom)
```

### PRIORITY 2 — Tuần 2-3 (Code Mechanics)
```
[ ] Combo system (kill counter + floating text)
[ ] Airstrike meter + execution
[ ] Pre-level tower selection (6 slots)
[ ] 3 consumable items
[ ] 4 enemy types mới (medic/transport/speed/explosive)
[ ] Power tower (buff) + Mine tower
[ ] Multi-entry maps
```

### PRIORITY 3 — Tuần 3-4 (Graphics)
```
[ ] Tower sprites lv1-3 + turret (5 towers × 4 files = 20)
[ ] Tower icons (9 icons × 1 file = 9)
[ ] Enemy sprites (10 enemies, static or animated)
[ ] Terrain tilesets (4 zones × ~5 tiles = 20)
[ ] UI sprites (~15 files)
[ ] Particle effect textures (~10)
```

### PRIORITY 4 — Tuần 4-5 (Maps & Polish)
```
[ ] 12 map configs (JSON)
[ ] Wave definitions (60 waves per map)
[ ] Difficulty scaling (Easy/Medium/Hard)
[ ] World map integration (link từ map.html)
[ ] Score/star system
[ ] Endless mode
```

**TỔNG: ~130 files cần tạo mới**
