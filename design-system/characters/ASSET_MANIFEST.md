# 🎨 CHARACTER ASSETS MANIFEST
**VInaStudy Bot — Design System v6**

## 📁 Folder Structure
```
design-system/
├── characters/
│   ├── ASSET_MANIFEST.md (this file)
│   ├── playable/
│   │   ├── lac-tuong/
│   │   │   ├── lac-tuong-male-avatar.png      (1024×1024 transparent)
│   │   │   ├── lac-tuong-male-card.png        (1024×1024 dark bg)
│   │   │   ├── lac-tuong-male-sprite.png      (512×512 transparent)
│   │   │   ├── lac-tuong-female-avatar.png
│   │   │   ├── lac-tuong-female-card.png
│   │   │   └── lac-tuong-female-sprite.png
│   │   ├── dao-si/
│   │   │   ├── dao-si-male-avatar.png
│   │   │   ├── dao-si-male-card.png
│   │   │   ├── dao-si-male-sprite.png
│   │   │   ├── dao-si-female-avatar.png
│   │   │   ├── dao-si-female-card.png
│   │   │   └── dao-si-female-sprite.png
│   │   ├── no-than/
│   │   │   ├── no-than-male-avatar.png
│   │   │   ├── no-than-male-card.png
│   │   │   ├── no-than-male-sprite.png
│   │   │   ├── no-than-female-avatar.png
│   │   │   ├── no-than-female-card.png
│   │   │   └── no-than-female-sprite.png
│   │   └── than-tuong/
│   │       ├── than-tuong-male-avatar.png
│   │       ├── than-tuong-male-card.png
│   │       ├── than-tuong-male-sprite.png
│   │       ├── than-tuong-female-avatar.png
│   │       ├── than-tuong-female-card.png
│   │       └── than-tuong-female-sprite.png
│   ├── boss/
│   │   ├── ho-tinh-portrait.png               (1024×1024 main)
│   │   ├── ho-tinh-card.png                   (1024×1024 card variant)
│   │   └── ho-tinh-wide.png                   (1920×800 banner)
│   ├── npc/
│   │   ├── thay-long/
│   │   │   ├── thay-long-portrait.png         (1024×1024)
│   │   │   ├── thay-long-avatar.png           (256×256 for dialogs)
│   │   │   └── thay-long-sprite.png           (512×512)
│   │   └── (future NPCs...)
│   └── css/
│       ├── character-avatars.css
│       ├── character-cards.css
│       ├── boss-screen.css
│       └── npc-dialogs.css
```

---

## 📊 CHARACTER ASSET SPECIFICATIONS

### PLAYABLE CHARACTERS (8 total: 4 classes × 2 genders)

#### 🔴 **LẠC TƯỚNG (Warrior) — Red #C0332E**
```
Male Version:
  - Avatar (1024×1024): Bust portrait, transparent background, slight right-facing
  - Card (1024×1024): Full portrait with dark indigo #110A1C background
  - Sprite (512×512): Cropped bust for battle animation

Female Version:
  - Avatar (1024×1024): Bust portrait, transparent background, slight left-facing
  - Card (1024×1024): Full portrait with dark indigo background
  - Sprite (512×512): Cropped bust for battle animation

Status: ✅ Generated & Approved
```

#### 🟣 **ĐẠO SĨ (Mage) — Purple #5E2A78**
```
Male Version:
  - Avatar (1024×1024): Bust with staff visible, transparent, right-facing
  - Card (1024×1024): Full robe portrait with dark background
  - Sprite (512×512): Staff visible for battle

Female Version:
  - Avatar (1024×1024): Bust with staff visible, transparent, left-facing
  - Card (1024×1024): Full robe portrait with dark background
  - Sprite (512×512): Staff visible for battle

Status: ✅ Generated & Approved
```

#### 🟢 **NỎ THẦN (Archer) — Jade Teal #246B4A**
```
Male Version:
  - Avatar (1024×1024): Bust with crossbow visible, transparent, right-facing
  - Card (1024×1024): Full standing pose with crossbow, dark background
  - Sprite (512×512): Crossbow visible for battle

Female Version:
  - Avatar (1024×1024): Bust with crossbow visible, transparent, left-facing
  - Card (1024×1024): Full standing pose with crossbow, dark background
  - Sprite (512×512): Crossbow visible for battle

Status: ✅ Generated & Approved
```

#### 🔵 **THẦN TƯỚNG (Knight) — Indigo Blue #1A3A5C**
```
Male Version:
  - Avatar (1024×1024): Bust with shield visible, transparent, right-facing
  - Card (1024×1024): Full armor portrait with shield & spear, dark background
  - Sprite (512×512): Shield visible for battle

Female Version:
  - Avatar (1024×1024): Bust with shield visible, transparent, left-facing
  - Card (1024×1024): Full armor portrait with shield & spear, dark background
  - Sprite (512×512): Shield visible for battle

Status: ✅ Generated & Approved
```

---

### BOSS CHARACTERS (1 total)

#### 🦊 **HỒ TINH (Nine-tailed Fox Spirit Boss)**
```
Assets:
  - Portrait (1024×1024): Main boss image, dark gradient bg, golden border frame
  - Card (1024×1024): Alternative card style with decorative frame
  - Wide Banner (1920×800): For boss intro cinematic screen

Features:
  - 9 golden glowing tails (numbered 1-9 in neon blue)
  - Floating math symbols (+ − × ÷ = √ ½ △ ∑) in blue aura
  - Cold commanding expression, NOT seductive
  - Golden ornate fan weapon
  - Red silk áo thụng robe (modest)
  - Golden lotus ornaments in black hair

Status: ✅ Generated & Approved (v2.1)
```

---

### NPC CHARACTERS (1 currently, expandable)

#### 👨‍🏫 **THẦY LONG (Teacher NPC)**
```
Role: Math teacher, mentor figure, quest giver, lesson guide
Age: ~40-50, wise, approachable, encouraging
Appearance: Traditional Vietnamese teacher attire
Assets to Create:
  - Portrait (1024×1024): For dialog/cutscene scenes
  - Avatar (256×256): For dialog boxes & character portraits
  - Sprite (512×512): For classroom/map scenes

Status: 🔄 To be designed
```

---

## 🎨 FORMAT SPECIFICATIONS

### Avatar Format (1024×1024, Transparent PNG)
- **Use Case:** Character selection screen, battle HUD, profile cards
- **Content:** Bust portrait from shoulders up
- **Background:** Transparent (no background)
- **Frame:** Optional faction-colored border (CSS applied separately)
- **Quality:** High DPI, crisp details

### Card Format (1024×1024, Dark Background)
- **Use Case:** Character showcase, class selection screen, stat screens
- **Content:** Full portrait or bust with detailed view
- **Background:** Dark indigo gradient #110A1C to #221640 (NG_HOABAO standard)
- **Border:** Golden ornate frame with Vietnamese hoa văn patterns (SVG overlay)
- **Effects:** Subtle glow, shadow depth

### Boss Portrait (1024×1024, Decorative)
- **Use Case:** Boss intro screen, encounter cinematic
- **Content:** Full body or 3/4 body, dramatic pose
- **Background:** Dark with atmospheric effects (mist, clouds, ruins)
- **Border:** Ornate golden frame, more elaborate than playable characters
- **Effects:** Glow, particle effects hints

### Sprite Format (512×512, Transparent PNG)
- **Use Case:** Battle animation, in-game sprites, small UI elements
- **Content:** Cropped bust from avatar, optimized for small display
- **Background:** Transparent
- **Quality:** Slightly reduced DPI for performance
- **Animation:** Can be tiled/animated with CSS sprite sheets

---

## 📋 CSS STYLING (Referenced Files)

### character-avatars.css
```css
.character-avatar {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  border: 3px solid var(--faction-color);
  box-shadow: 0 0 15px var(--faction-glow);
  background: var(--bg-panel);
  overflow: hidden;
  position: relative;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Faction-specific */
.avatar-lac-tuong { --faction-color: #C0332E; --faction-glow: #FF5555; }
.avatar-dao-si { --faction-color: #5E2A78; --faction-glow: #9966FF; }
.avatar-no-than { --faction-color: #246B4A; --faction-glow: #66FFCC; }
.avatar-than-tuong { --faction-color: #1A3A5C; --faction-glow: #6699FF; }
```

### character-cards.css
```css
.character-card {
  width: 300px;
  aspect-ratio: 1;
  position: relative;
  border: 8px solid var(--faction-color);
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.7);
}

.character-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
  pointer-events: none;
}
```

### boss-screen.css
```css
.boss-encounter {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0F0A15 0%, #2A1535 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.boss-portrait {
  width: 600px;
  height: 600px;
  margin-bottom: 40px;
  border: 12px solid #C8960C;
  border-radius: 8px;
  box-shadow: 0 0 40px #C8960C, inset 0 0 40px rgba(200,150,12,0.3);
  overflow: hidden;
}

.boss-portrait img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

---

## ✅ INTEGRATION CHECKLIST

- [ ] Create all folder directories
- [ ] Generate/place all character PNG files (avatars, cards, sprites)
- [ ] Generate boss character assets
- [ ] Design thầy Long character (portrait, avatar, sprite)
- [ ] Create CSS files for character styling
- [ ] Update HTML game pages with image references
- [ ] Test responsive scaling on mobile/tablet
- [ ] Optimize image file sizes for web
- [ ] Create sprite animation sheets (if needed)
- [ ] Add character selection UI screen
- [ ] Add boss encounter screen (Hồ Tinh intro)
- [ ] Add NPC dialog system (thầy Long conversations)

---

**Asset Manifest v1.0**  
Created: 2026-05-26  
Reference: CHARACTER_DESIGN.md v2.1 · palette-final.html v6
