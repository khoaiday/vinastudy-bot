# KỊCH BẢN GAME: CHIẾN BINH TOÁN - GIẢI CỨU HỆ MẶT TRỜI TRÍ TUỆ

## 1. Bối cảnh (Lore)
- **Vũ trụ:** Hệ Mặt Trời Trí Tuệ (Matholar System) đang bị một thế lực bóng tối có tên là **Chúa Tể Hỗn Loạn** nhăm nhe xâm chiếm. Hắn đã thả các Quái Vật Toán Học đi phá hủy các hành tinh.
- **Nhân vật chính:** Người chơi vào vai một **CHIẾN BINH TOÁN** (Nam: Giáp xanh lá, Nữ: Giáp tím) mang trong mình năng lực giải mã các phép toán.
- **Vũ khí:** Máy Tính Năng Lượng. Khi trả lời đúng, vũ khí sẽ bắn ra Tia Laser Năng Lượng.
- **Trợ lý:** NPC Robot Mo-Mo. Khi Chiến Binh gặp khó khăn (nhập sai), Mo-Mo sẽ xuất hiện hỗ trợ đưa ra các gợi ý.

## 2. Bản đồ Chiến dịch (Map)
Bản đồ gồm nhiều Trạm (Zone), tương ứng với các chương học:
- **Trạm 1: Sao Thủy Cấp Tốc**
  - Ải 2: Quái Vật Ổ Khóa Số Học (Nhiệm vụ cấu tạo số)
  - Ải 3: Đốm Đen Tinh Nghịch 
- **Trạm 2: Sao Kim Rực Rỡ**
  - Ải 4: Đám Mây Bão Lóc Chóc
  - Ải 5: Quái Vật Máy Xóa Số
- **Trạm 3: Trái Đất & Sao Hỏa**
  - Ải 27: Truy Tìm Chúa Tể Hỗn Loạn

## 3. Cơ chế Gameplay (Core Loop)
1. **Trang chủ (Splash Screen):** Người chơi xem cốt truyện, chọn giới tính (nhận Avatar tương ứng) và nhập tên. Dữ liệu lưu vào `localStorage`.
2. **Bản đồ (Map):** Hiển thị các Ải. Các Ải đã hoàn thành sẽ được hóa Vàng (Gold), gắn 🏆 và đánh dấu "ĐÃ VƯỢT QUA".
3. **Trận chiến (Boss Battle):**
   - Trả lời đúng: Bắn tia Laser (Beam), trừ máu Boss. 
   - Trả lời sai lần 1: Robot Mo-Mo bay ra gợi ý, không trừ điểm.
   - Trả lời sai lần 2: Boss ra đòn (quả cầu hắc ám), trừ máu Chiến Binh.
4. **Hệ thống Phần thưởng:** Hoàn thành Ải (đạt >= 50% số câu đúng) sẽ nhận Huy hiệu 🏆 cho Ải đó. Hệ thống cập nhật tổng số huy hiệu lên Bản đồ.
5. **Lưu trữ (Tương lai):** Sẽ tích hợp tính năng Tự động Lưu tiến độ (Auto-save) và Hiển thị câu hỏi (Câu X/Y).
