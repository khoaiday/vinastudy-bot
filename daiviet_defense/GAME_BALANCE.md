# ĐẠI VIỆT DEFENSE — Game Balance Sheet
## Baseline: Fieldrunners 2 mechanics + Vietnamese theming

**Nguồn data baseline:**
- libgame.so binary strings (airstrike, combo configs)
- Public FR2 wiki/community guides (DPS, cost, range values)
- Adapted for Đại Việt Defense scale (50 px grid, 16x11)

---

## 🏰 TOWER STATS — 9 towers, 3 upgrade levels each

### Damage Tower Tier (theo cost từ thấp → cao)

| # | Tower | Cost | Upg Lv2 | Upg Lv3 | DPS Lv1/2/3 | Range | Fire Rate | Special |
|---|---|---|---|---|---|---|---|---|
| 1 | **Nỏ Liên Châu** (Gatling) | 40 | 30 | 50 | 35 / 70 / 105 | 2.5 | 0.5s | Fast single-target |
| 2 | **Bẫy Nhựa** (Goo/Slow) | 55 | 35 | 60 | 12 / 24 / 36 | 2.5 | 1.0s | Slow 40%/60%/75% |
| 3 | **Thần Cơ Pháo** (Cannon/AoE) | 80 | 50 | 80 | 100 / 200 / 300 | 3.5 | 1.6s | Splash radius 1.8 |
| 4 | **Bẫy Chông** (Mine/Trap) | 90 | 60 | 100 | 1500 dmg/mine | 1.0 | One-shot | Damage on step |
| 5 | **Hỏa Tháp** (Flame/DoT) | 100 | 60 | 100 | 300 / 600 / 900 | 2.5 | Continuous | Burn DoT |
| 6 | **Trống Lệnh** (Power Buff) | 120 | 80 | 120 | — | 1.5 | — | +25%/50%/75% nearby |
| 7 | **Đàn Hương** (Plague/Poison) | 140 | 80 | 130 | 200 / 400 / 600 | 2.5 | DoT | Spread to nearby |
| 8 | **Lôi Tháp** (Tesla/Chain) | 180 | 100 | 150 | 700 / 1400 / 2100 | 2.5 | 0.85s | Chain 3 targets |
| 9 | **Thần Cơ Đại Pháo** (Railgun) | 250 | 150 | 200 | 850 / 1700 / 2550 | 5.5 | 2.0s | Pierce line |

**Targeting modes per tower:** First / Last / Strongest / Weakest / Nearest (player choice)

---

## 👾 ENEMY STATS — 11 types

| # | Enemy | HP base | Speed | Reward | Special |
|---|---|---|---|---|---|
| 1 | **Lính Trinh Sát** (Scout) | 50 | 1.6 | 12 | Fast, weak |
| 2 | **Bộ Binh** (Infantry) | 120 | 1.0 | 18 | Standard |
| 3 | **Voi Chiến** (Heavy/Tank) | 300 | 0.55 | 35 | High HP, slow |
| 4 | **Kị Binh Áo Xanh** (Speedster) | 75 | 2.2 | 20 | **Slow-immune** |
| 5 | **Quạ Sắt** (Air/Flying) | 130 | 1.2 | 30 | Flies over towers |
| 6 | **Pháp Sư** (Medic) | 100 | 0.9 | 40 | **Heals 8 HP/s nearby** |
| 7 | **Xe Trâu** (Transport) | 200 | 0.7 | 25 | Drops 4 Scouts on death |
| 8 | **Lính Bom** (Explosive) | 80 | 1.3 | 15 | Explodes (40% maxHP AoE) |
| 9 | **Khí Cầu** (Blimp) | 600 | 0.35 | 50 | Slow, very tough air |
| 10 | **Đại Tướng** (Boss) | 1500 | 0.4 | 200 | Final wave |
| 11 | **Quái Vô Hình** (Stealth) | 90 | 1.4 | 35 | Invisible to standard targeting |

**HP scaling per wave:** `hp_base × (1 + waveNum × 0.25)`

---

## 🌊 WAVE PROGRESSION — 15 waves

| Wave | Enemy mix | Difficulty notes |
|---|---|---|
| 1 | 5 Scout | Tutorial |
| 2 | 4 Scout + 3 Infantry | |
| 3 | 2 Scout + 5 Infantry + 1 Heavy | First heavy |
| 4 | 3 Infantry + 3 Air | **Air intro!** |
| 5 | 3 Scout + 4 Infantry + 1 Heavy + 2 Speedster | Speedsters! |
| 6 | 2 Scout + 5 Infantry + 2 Heavy + 1 Medic + 2 Air | First medic |
| 7 | 1 Heavy + 5 Air + 1 Blimp | **Air swarm** |
| 8 | 4 Scout + 6 Infantry + 2 Transport | Transports! |
| 9 | 3 Scout + 4 Infantry + 3 Heavy + 2 Medic + 3 Speedster | Mixed |
| 10 | 5 Infantry + 2 Heavy + 4 Explosive | **Boom wave** |
| 11 | 8 Infantry + 3 Heavy + 3 Air + 2 Medic + 1 Transport | Hard mix |
| 12 | 4 Infantry + 6 Air + 2 Blimp | **Air force** |
| 13 | 4 Infantry + 4 Heavy + 4 Speedster + 2 Medic + 3 Air | Speed rush |
| 14 | 8 Infantry + 5 Heavy + 4 Air + 3 Transport + 3 Explosive | Chaos |
| 15 | 6 Infantry + 3 Heavy + 3 Air + 1 BOSS + 2 Medic + 1 Blimp + 3 Speedster | **BOSS FINAL** |

---

## ⚡ AIRSTRIKE METER (from FR2 binary)

```
gAirstrikeMeterMaxPoints           = 100
gAirstrikeAttackTimer              = 3.0 seconds
gAirstrikeAttackWidth              = 2.0 cells wide

POINT GAIN:
  per kill (single)        +4
  per combo kill           +12 (when combo > 3)
  per mega combo kill      +25 (when combo > 8)
  per perfect (wave clear) +15
  per HP lost              +20 (consolation)

AIRSTRIKE DAMAGE:
  per cell hit             60% of enemy maxHP
  elite damage percent     150% (vs heavy/blimp/boss)
```

---

## 🔥 COMBO SYSTEM (from FR2 binary)

```
gDefaultMinComboRequirement      = 3 kills in 1.2s
gDefaultMinMegaComboRequirement  = 8 kills in 1.2s
gDefaultComboBonus               = 5 × comboCount (gold)
gDefaultMegaComboBonus           = 15 × comboCount (gold)

COMBO_WINDOW                     = 1200 ms
```

---

## 💰 ECONOMY

```
STARTING:
  Gold        = 350
  HP          = 30
  Items       = [Bomb x1, Freeze x1, Gold x1]

WAVE REWARD:
  base        = 80 gold
  per wave    = +15 gold per wave number
  formula     = 80 + currentWave × 15

LIFE LOSS:
  per enemy escape = -1 HP

LOSS CONDITION:
  HP = 0

WIN CONDITION:
  Survive all 15 waves
```

---

## 🎯 TOWER PLACEMENT RULES

```
GRID:           16 × 11 cells
CELL SIZE:      50 px
START GATE:     (0, 5) — left center
EXIT GATE:      (15, 5) — right center

NO TOWER:
  - On enemy path row (y=5)
  - On occupied cells
  - On start/exit gates
  - On obstacles (level-dependent)

BLOCKING PREVENTION:
  - BFS path check after each placement
  - If placement breaks path → reject + red warning
```

---

## 📊 TARGETING PRIORITY MODES (FR2 standard)

Per-tower toggle:

| Mode | Logic |
|---|---|
| **First** | Furthest along path (default) |
| **Last** | Closest to spawn |
| **Strongest** | Highest current HP |
| **Weakest** | Lowest current HP |
| **Nearest** | Closest to tower |

---

## 🎚 DIFFICULTY MULTIPLIERS

```
EASY:    HP × 0.7, Reward × 1.2
NORMAL:  HP × 1.0, Reward × 1.0
HARD:    HP × 1.5, Reward × 0.85
```
