# GEMINI WORKFLOW — Quy trình giao việc code game cho Gemini

## Phân công rõ ràng

| Người | Phụ trách |
|-------|-----------|
| **Claude (Cowork)** | UI/UX, loadout.html, battle.html, art direction, prompt gen, review |
| **Gemini** | Game engine code (index_3d.html), Three.js logic, algorithm, pathfinding, enemy AI |

---

## Cách giao việc cho Gemini

### Bước 1 — Claude tạo task card trong `GEMINI_TASKS.md`

Format chuẩn:

```
## [TASK-XXX] Tên task
**File:** daiviet_defense/index_3d.html
**Mô tả:** [mô tả rõ bài toán cần giải]
**Input:** [state/data đầu vào]
**Output mong đợi:** [kết quả cụ thể]
**Constraints:** Không thay đổi: [danh sách thứ không được sửa]
**Context:** Đọc AI_CONTEXT.md section [X] trước khi làm
**Status:** TODO → IN_PROGRESS → REVIEW → DONE
```

### Bước 2 — Gemini nhận task

Gemini đọc `GEMINI_TASKS.md`, chọn task `TODO`, cập nhật status → `IN_PROGRESS`, làm việc.

### Bước 3 — Gemini bàn giao

Khi xong: cập nhật status → `REVIEW`, ghi rõ:
- Files đã sửa
- Logic đã thay đổi
- Cần Claude test gì

### Bước 4 — Claude review và merge

Claude đọc diff, test, nếu OK → status `DONE`, update `task.md`.

---

## GEMINI_TASKS.md — Task backlog hiện tại

### [TASK-001] Fix camera fit — map fill toàn màn hình
**File:** `daiviet_defense/index_3d.html`  
**Mô tả:** Camera Three.js orthographic chưa fit đúng màn hình landscape. Map bị crop hoặc thừa viền đen/nâu xung quanh. Cần camera tự động tính frustum để map background (16:9) fill 100% viewport bất kể device.  
**Constraints:** Không sửa HUD, buildBar, pauseMenu HTML. Không sửa map texture loading code.  
**Context:** Đọc `AI_CONTEXT.md` section 7, `daiviet_defense/index_3d.html` — tìm `computeCameraFrustum`, `CAM_HEIGHT`, `PLANE_W`, `PLANE_H`.  
**Status:** TODO

---

### [TASK-002] Enemy path — chạy từ trái ngoài màn vào cổng thành phải
**File:** `daiviet_defense/index_3d.html`  
**Mô tả:** Quân địch cần xuất hiện từ ngoài cạnh trái màn hình (x = -EXTEND_X), đi thẳng theo row START.y, đến cổng thành (x = EXIT.x + EXTEND_X) rồi "chui vào" cổng và biến mất. Hiện tại enemies spawn tại x=0 (trong grid) thay vì ngoài màn.  
**Output:** Enemy fade-in ở cạnh trái, walk across, fade-out ở cổng phải.  
**Constraints:** Không thay đổi BFS pathfinding trong grid. Không sửa tower placement logic.  
**Status:** TODO

---

### [TASK-003] Wave progression — wave counter + enemy mix theo GAME_BALANCE.md
**File:** `daiviet_defense/index_3d.html`  
**Mô tả:** Triển khai đúng 15 waves theo bảng trong `daiviet_defense/GAME_BALANCE.md`. Hiện tại wave chỉ spawn scout. Cần spawn đúng mix enemy theo từng wave.  
**Status:** TODO

---

### [TASK-004] Win/Lose screen + stars
**File:** `daiviet_defense/index_3d.html`  
**Mô tả:** Khi clear wave 15 → Win screen (⭐⭐⭐ tùy HP còn lại). Khi HP=0 → Lose screen. Cả 2 có nút [CHƠI LẠI] và [QUAY VỀ BẢN ĐỒ → map.html].  
**Star logic:** 3⭐ = HP > 20, 2⭐ = HP 10-20, 1⭐ = HP < 10.  
**Status:** TODO

---

## Quy tắc bất biến cho Gemini

1. **Không bao giờ** sửa `loadout.html`, `battle.html`, `map.html`, `task.md`, `AI_CONTEXT.md` trừ khi task yêu cầu rõ ràng
2. **Luôn** đọc `AI_CONTEXT.md` trước khi bắt đầu
3. **Luôn** cập nhật `task.md` sau khi hoàn thành
4. Design system: Philosopher + Lora · Đỏ son #C0332E · Vàng nghệ #C8960C · Mực tàu #050A1F
5. **Không** tự ý đổi tên biến/function đang dùng ở chỗ khác

---

## Hiện trạng game (để Gemini nắm context)

- **URL:** `https://app.soichido.vn/daiviet_defense/index_3d.html`
- **Map background:** `assets/map_bg_coloa_1.jpg` (đã load, xanh lá + cổng thành phải)
- **Path:** thẳng từ trái sang phải, row 5/11
- **Orange tint:** ĐÃ FIX (xóa fog, mist, bloom, đổi lights về neutral)
- **Placeholder boxes:** ĐÃ ẨN (detail/spawn/weapon models visible=false)
- **Đang lỗi:** mistPlane reference đã xóa trong animate loop
