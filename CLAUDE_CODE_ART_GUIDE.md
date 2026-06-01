# 🎮 ĐẠI VIỆT DEFENSE — ART & 3D GENERATION WORKFLOW FOR CLAUDE CODE

Tài liệu này hướng dẫn chi tiết cho Claude Code cách điều phối quy trình tự động hóa sinh tài nguyên game (2D & 3D) kết hợp kiểm duyệt thủ công qua **2 cửa duyệt nghiêm ngặt**.

---

## 🛡️ HƯỚNG DẪN DÀNH CHO CLAUDE (CLAUDE CODE SPECIFICATION)

Khi người dùng yêu cầu chạy quy trình thiết kế hoặc sinh asset mới, Claude hãy làm theo quy trình 2 bước dưới đây:

### 🌟 Nguyên tắc thiết kế quan trọng:
- **Level 1:** Vũ khí thô sơ đặt sát đất trên trục đỡ gỗ cực kỳ nhỏ gọn (không xây tháp cao rườm rà). Trực quan, ít chi tiết, stylized low-poly để dễ nhìn từ góc top-down.
- **Level 2:** Lắp đặt thêm tháp gỗ nhỏ hoặc bệ đá đơn giản để nâng chiều cao.
- **Level 3:** Tháp kiên cố hoàn chỉnh, mái che cổ phong, chạm khắc Đông Sơn đồng/vàng rực rỡ.

---

## 🛠️ QUY TRÌNH 2 BƯỚC (DOUBLE-GATE REVIEW)

### BƯỚC 1: SINH VÀ DUYỆT 2D CONCEPT (LEONARDO AI)
1. Đọc và chỉnh sửa prompt phù hợp yêu cầu trong file [prompts.json](file:///c:/Users/Nam/OneDrive/Desktop/vinastudy-bot/tools/asset_gen/prompts.json).
2. Gọi script để sinh ảnh cụ thể (ví dụ sinh icon tháp nỏ):
   ```bash
   node tools/asset_gen/asset_gen.js --id arrow_tower_icon --force
   ```
3. **Dừng lại ngay lập tức và yêu cầu duyệt:**
   - In đường dẫn file ảnh cục bộ ra terminal để người dùng click mở trực tiếp: [icon_arrow.png](file:///c:/Users/Nam/OneDrive/Desktop/vinastudy-bot/daiviet_defense/assets/icons/icon_arrow.png)
   - Chờ phản hồi từ người dùng. **Không được tự ý chuyển sang bước 3D khi chưa được phê duyệt.**
   - Nếu người dùng yêu cầu sửa đổi (ví dụ: *"cho bệ đỡ nhỏ hơn"*, *"đổi màu"*...) ➔ Cập nhật prompt và gen lại.

---

### BƯỚC 2: SINH VÀ DUYỆT 3D MODEL (MESHY.AI)
1. Khi người dùng gõ **"chốt 2d"** hoặc **"ok"** ➔ Tiến hành đồng bộ prompt 3D tương đương.
2. Gọi script sinh 3D Model:
   ```bash
   node tools/asset_gen/asset_gen.js --id arrow_tower_3d --force
   ```
3. **Dừng lại và yêu cầu duyệt:**
   - In đường dẫn file 3D `.glb` ra terminal để người dùng mở bằng 3D Viewer của Windows: [no_lien_chau_lv1.glb](file:///c:/Users/Nam/OneDrive/Desktop/vinastudy-bot/daiviet_defense/3d_assets/no_lien_chau_lv1.glb)
   - Hoặc hướng dẫn người dùng kéo thả vào [gltf-viewer.donmccurdy.com](https://gltf-viewer.donmccurdy.com/) để check xoay 360 độ.

---

### BƯỚC 3: TÍCH HỢP VÀ DEPLOY
1. Khi người dùng gõ **"chốt 3d"** hoặc **"ok"** ➔ Cập nhật mã nguồn trong [index_3d.html](file:///c:/Users/Nam/OneDrive/Desktop/vinastudy-bot/daiviet_defense/index_3d.html) để ánh xạ đúng mô hình `.glb` mới vào tháp tương ứng.
2. Hỗ trợ người dùng deploy nhanh lên môi trường Production (Railway):
   ```bash
   git add .
   git commit -m "feat: integrate approved 3D arrow tower model"
   git push origin main
   ```

---

## 📋 DANH SÁCH LỆNH TIỆN ÍCH CHO CLAUDE CODE
- **Kiểm tra trạng thái các asset trong game:**
  ```bash
  node tools/asset_gen/asset_gen.js --list
  ```
- **Sinh 1 asset cụ thể theo ID:**
  ```bash
  node tools/asset_gen/asset_gen.js --id [ID_ASSET] --force
  ```
