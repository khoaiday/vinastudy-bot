#!/usr/bin/env python3
"""
VInaStudy — Claude API Content Generator
Auto-generates kịch bản lịch sử + bài tập toán cho tất cả 13 ải.

Usage:
    python generate_content.py --ai 8              # Generate ải 8 only
    python generate_content.py --ai 8 9 10         # Generate ải 8, 9, 10
    python generate_content.py --all               # Generate tất cả ải còn thiếu
    python generate_content.py --all --force       # Ghi đè kể cả file đã có
    python generate_content.py --ai 8 --dry-run    # Xem prompt, không gọi API
    python generate_content.py --list              # Liệt kê trạng thái tất cả ải

Requirements:
    pip install anthropic
    Set ANTHROPIC_API_KEY in environment or .env file
"""

import anthropic
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
SCENARIOS_DIR.mkdir(exist_ok=True)

DEFAULT_MODEL = "claude-opus-4-5"
MAX_TOKENS = 8000

# ═══════════════════════════════════════════════════════════════════════════════
# GAME DATA — Toàn bộ 13 ải
# ═══════════════════════════════════════════════════════════════════════════════

AILS = [
    {
        "id": 1, "buoi": 1,
        "ten": "Trứng Tiên Nở Trăm Con",
        "subtitle": "Biển Cả Và Trăm Người Con",
        "thoi_ky": "~2879 TCN — Hồng Bàng, Lạc Việt sơ khai",
        "boi_canh": (
            "Bờ biển Hồng Bàng. Lạc Long Quân và Âu Cơ chia tay — 100 người con trong bọc trứng "
            "phải được chia đôi: 50 theo cha xuống biển, 50 theo mẹ lên núi Nghĩa Lĩnh. "
            "Ngư Tinh — quái ngư nghìn tuổi từ phương Bắc — tung Lưới Hỗn Độn xóa sạch mọi "
            "phép đếm và phép chia đôi trong tâm trí dân Lạc Việt."
        ),
        "vai_choi": "🐉 Lạc Long Quân — Thủy Tổ người Việt, Vua Rồng Biển Lạc Việt",
        "dong_minh": ["🧚 Âu Cơ (Tiên Nữ)", "🥚 100 người con trong bọc trứng"],
        "boss": {
            "ten": "Ngư Tinh", "emoji": "🐟",
            "danh_hieu": "Quái Ngư Nghìn Tuổi",
            "co_che": "Lưới Hỗn Độn xóa sạch phép đếm và phép chia đôi — không ai đếm được 100, không chia được công bằng",
            "thiet_ke": "Cá khổng lồ đen bạc, vẩy như giáp đồng Đông Sơn, mắt đỏ rực từ đáy biển, đuôi vung tạo sóng cao 20 trượng",
            "don_vi_hp": "🌊 sóng biển", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Cộng và trừ trong phạm vi 100 · Chia đôi (chia 2) · Tính nhẩm · 50+50=100",
            "cap_do": "Buổi 1 — Nền tảng ôn tập, dễ nhất — vào game lần đầu",
            "dang_bai": [
                "Cộng nhẩm hai số trong phạm vi 100 (vd: 48+37)",
                "Phép chia đôi (vd: 68:2=?)",
                "Bài toán có lời văn: chia đều làm hai phần bằng nhau",
                "Câu khó (HSG): tìm số khi biết nửa của nó",
            ],
        },
        "tuyet_chieu": "💧 Thủy Hải Tổng Công — Điều khiển dòng nước và sóng biển, cộng trừ tức thì trong 100",
        "file_output": "scenarios/ai-1-lac-long-quan.md",
        "do_kho": "⭐ Ải 1 — Dễ nhất",
    },
    {
        "id": 2, "buoi": 2,
        "ten": "Mười Lăm Bộ Lạc Văn Lang",
        "subtitle": "Triều Đình Hùng Vương Sơ Lập",
        "thoi_ky": "~2879 TCN — Văn Lang, Hùng Vương thứ 1",
        "boi_canh": (
            "Phong Châu (Phú Thọ). Hùng Vương thứ 1 vừa lên ngôi cần đọc báo cáo dân đinh "
            "và lương thực từ 15 bộ lạc để cai trị đất nước. "
            "Mộc Tinh — cây cổ thụ nghìn năm từ phương Bắc — xâm nhập kho thẻ tre, "
            "đảo vị trí chữ số trong mọi con số: 345 thành 534, 208 thành 820."
        ),
        "vai_choi": "👑 Hùng Vương thứ 1 — Vị vua đầu tiên của nước Văn Lang",
        "dong_minh": ["🧙 Lạc Hầu (quan thần đầu triều)", "📜 Kho thẻ tre lưu trữ quốc gia"],
        "boss": {
            "ten": "Mộc Tinh", "emoji": "🌳",
            "danh_hieu": "Cây Cổ Thụ Nghìn Năm",
            "co_che": "Đảo vị trí chữ số trong mọi con số — 345 thành 534, không ai đọc được báo cáo chính xác",
            "thiet_ke": "Cây cổ thụ khổng lồ màu đen-xanh biết di chuyển, rễ như xúc tu bạch tuộc, lá rụng thành dao nhọn",
            "don_vi_hp": "🍃 cành cây", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Đọc và viết số có 3 chữ số · Số tròn trăm · Nhận biết hàng trăm-chục-đơn vị",
            "cap_do": "Buổi 2 — Đọc viết số, số tròn trăm",
            "dang_bai": [
                "Đọc số 3 chữ số bất kỳ (vd: 608 đọc là gì?)",
                "Viết số theo lời đọc (vd: Hai trăm bốn mươi lăm = ?)",
                "Số tròn trăm: điền số còn thiếu (100, 200, ?, 400...)",
                "Câu khó: cho biết hàng trăm=4, hàng chục=0, hàng ĐV=7 → số là bao nhiêu?",
            ],
        },
        "tuyet_chieu": "📜 Thiên Thư Giải Mã — Đọc và viết đúng mọi con số dù bị đảo lộn",
        "file_output": "scenarios/ai-2-van-lang.md",
        "do_kho": "⭐⭐ Ải 2",
    },
    {
        "id": 3, "buoi": 3,
        "ten": "Yêu Cáo Chín Đuôi Tây Hồ",
        "subtitle": "Dưới Đáy Hồ Huyền Bí",
        "thoi_ky": "Văn Lang sơ kỳ — Hùng Vương đời đầu",
        "boi_canh": (
            "Vùng hồ lớn phía tây Phong Châu (nay là Tây Hồ, Hà Nội). "
            "Hồ Tinh — cáo 9 đuôi nghìn tuổi — cướp của cải từ 5 bộ lạc và ẩn trong hang đá dưới đáy hồ. "
            "Cần so sánh số liệu mất mát của từng bộ lạc để định vị hang, nhưng "
            "Hồ Tinh dùng phép Huyễn Số xáo trộn thứ tự con số trong mọi báo cáo."
        ),
        "vai_choi": "🐉 Lạc Long Quân — Đại Vương Rồng Biển, trở lại diệt yêu trên đất liền",
        "dong_minh": ["👑 Hùng Vương", "🏹 Các Lạc Hầu"],
        "boss": {
            "ten": "Hồ Tinh", "emoji": "🦊",
            "danh_hieu": "Cáo Chín Đuôi",
            "co_che": "Huyễn Số xáo trộn thứ tự con số trong báo cáo mất mát — không biết bộ nào thiệt hại nhiều nhất để định vị hang",
            "thiet_ke": "Nữ nhân áo đỏ rực, 9 đuôi cáo vàng phát sáng ảo huyễn, mắt xanh lạnh, mỗi đuôi ẩn một con số bị đảo",
            "don_vi_hp": "🦊 đuôi cáo", "so_hp": 6,
        },
        "toan": {
            "chu_de": "So sánh số có 3 chữ số · Xếp thứ tự từ bé đến lớn (và ngược lại) · Tìm số lớn nhất/nhỏ nhất · Dấu >, <, =",
            "cap_do": "Buổi 3 — So sánh và sắp xếp số",
            "dang_bai": [
                "So sánh hai số 3 chữ số với dấu >, <, = (vd: 456 ☐ 465)",
                "Sắp xếp 3-4 số theo thứ tự từ bé đến lớn",
                "Tìm số lớn nhất/nhỏ nhất trong 4 số",
                "Câu khó: tìm số X thỏa mãn điều kiện (vd: số lớn hơn 450 nhưng nhỏ hơn 460)",
            ],
        },
        "tuyet_chieu": "🔮 Thiên Nhãn Thứ Tự — Nhìn ngay ra số nào lớn hơn, không cần tính từng bước",
        "file_output": "scenarios/ai-3-ho-tinh.md",
        "do_kho": "⭐⭐ Ải 3",
    },
    {
        "id": 4, "buoi": 4,
        "ten": "Tiếng Trống Thúc Quân",
        "subtitle": "Đứa Trẻ Ba Tuổi Xin Ra Trận",
        "thoi_ky": "~1200 TCN — Hùng Vương thứ 6, làng Phù Đổng",
        "boi_canh": (
            "Làng Phù Đổng, Hùng Vương thứ 6. Giặc Ân xâm lược từ phương Bắc. "
            "Cậu bé 3 tuổi đột nhiên nói được và xin 'ngựa sắt, giáp sắt, roi sắt' ra trận. "
            "Thợ rèn cần kế hoạch dãy số cách đều để sản xuất đủ giáp trong 7 ngày. "
            "Ân Cổ Sứ dùng Trống Vàng Ân phát sóng âm phá tan mọi quy luật dãy số."
        ),
        "vai_choi": "🥁 Thánh Gióng (Phù Đổng Thiên Vương) — Thiên Tướng nhập thân cậu bé làng Phù Đổng",
        "dong_minh": ["👑 Hùng Vương thứ 6", "🔨 Thợ rèn làng Phù Đổng"],
        "boss": {
            "ten": "Ân Cổ Sứ", "emoji": "🥁",
            "danh_hieu": "Pháp Sư Trống Vàng Ân",
            "co_che": "Trống Vàng Ân phát sóng âm phá tan quy luật — dãy số cách đều trong kế hoạch rèn giáp biến thành hỗn loạn",
            "thiet_ke": "Pháp sư cao lớn áo đen viền vàng, mặt như đúc đồng, cầm Trống Vàng Ân hoa văn xoáy hỗn độn",
            "don_vi_hp": "🥁 trống", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Dãy số tự nhiên cách đều · Nhận ra quy luật · Điền số thiếu · Dãy cách 2, cách 3, cách 5, cách 10",
            "cap_do": "Buổi 4 — Dãy số, quy luật số",
            "dang_bai": [
                "Điền số thiếu vào dãy cách đều (vd: 5, 10, ?, 20, 25)",
                "Nhận ra quy luật và tiếp tục dãy",
                "Dãy giảm dần cách đều (vd: 100, 95, ?, 85...)",
                "Câu khó: tìm quy luật khi thiếu nhiều số (vd: 3, ?, ?, 12, ?)",
            ],
        },
        "tuyet_chieu": "⚡ Thiên Lôi Liên Hoàn — Nhìn ngay ra quy luật số, dự đoán được số tiếp theo trong chớp mắt",
        "file_output": "scenarios/ai-4-thanh-giong.md",
        "do_kho": "⭐⭐⭐ Ải 4",
    },
    {
        "id": 5, "buoi": 5,
        "ten": "Đê Thần & Trận Hồng Thủy",
        "subtitle": "Cuộc Chiến Vĩnh Cửu Giữa Núi Và Biển",
        "thoi_ky": "Hùng Vương thứ 18 — Vùng châu thổ Sông Hồng",
        "boi_canh": (
            "Châu thổ Sông Hồng, Hùng Vương thứ 18. Thủy Tinh nổi cơn thịnh nộ sau khi thua "
            "trong cuộc cầu hôn Mị Nương, dâng lũ lụt khổng lồ. "
            "Sơn Tinh cần số liệu cộng chính xác để tính khối lượng đất đá đắp đê. "
            "Thủy Tinh tung Bọt Hỗn Độn xóa kết quả mọi phép cộng."
        ),
        "vai_choi": "🏔️ Sơn Tinh (Tản Viên Sơn Thánh) — Thần Núi trấn lũ bảo vệ dân",
        "dong_minh": ["👑 Hùng Vương thứ 18", "💑 Mị Nương"],
        "boss": {
            "ten": "Thủy Tinh", "emoji": "🌊",
            "danh_hieu": "Thủy Vương — Thần Biển Đông",
            "co_che": "Bọt Hỗn Độn xóa kết quả phép cộng và làm sai số nhớ — không tính được lượng đất cần đắp đê",
            "thiet_ke": "Người từ thắt lưng trở lên, phần dưới là vùng nước xoáy, áo xanh lam sẫm, tóc xanh đen, tay vung tạo sóng",
            "don_vi_hp": "🌊 đợt sóng", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Phép cộng số có 3 chữ số · Có nhớ và không có nhớ · Cộng nhiều số · Kiểm tra bằng ước lượng",
            "cap_do": "Buổi 5 — Phép cộng có nhớ",
            "dang_bai": [
                "Cộng 3 chữ số không nhớ (vd: 345+213)",
                "Cộng 3 chữ số có nhớ (vd: 456+278)",
                "Cộng 3 số (vd: A+B+C trong phạm vi 1000)",
                "Câu khó: bài toán lời văn tổng cộng 2 bước",
            ],
        },
        "tuyet_chieu": "🏔️ Địa Sơn Bất Động — Tính nhanh phép cộng có nhớ, không bao giờ quên số nhớ",
        "file_output": "scenarios/ai-5-son-tinh.md",
        "do_kho": "⭐⭐⭐ Ải 5",
    },
    {
        "id": 6, "buoi": 6,
        "ten": "Bếp Lửa Của Hoàng Tử Nghèo",
        "subtitle": "Bánh Chưng Bánh Dày Và Lời Hứa Của Vua",
        "thoi_ky": "Hùng Vương thứ 6 — Cung điện Phong Châu",
        "boi_canh": (
            "Hùng Vương thứ 6 tìm người kế vị: ai dâng lễ vật ý nghĩa nhất sẽ được ngôi vua. "
            "Lang Liêu — hoàng tử thứ 18 nghèo khó nhất — được Thần Nông báo mộng làm Bánh Chưng Bánh Dày. "
            "Gian Thần Ân lấy trộm nguyên liệu và xóa hồ sơ số lượng bằng phép trừ sai "
            "để Lang Liêu thất bại và hoàng tử giàu có kế vị."
        ),
        "vai_choi": "🍃 Lang Liêu — Hoàng tử thứ 18, người nghèo nhất nhưng có tâm hồn cao đẹp nhất",
        "dong_minh": ["👑 Hùng Vương thứ 6", "🌾 Thần Nông (báo mộng)"],
        "boss": {
            "ten": "Gian Thần Ân", "emoji": "🕵️",
            "danh_hieu": "Gián Điệp Bếp Núc",
            "co_che": "Lấy trộm nguyên liệu và xóa hồ sơ phép trừ — Lang Liêu không biết còn thiếu bao nhiêu để hoàn thành bánh",
            "thiet_ke": "Tạp dề bếp giả mạo, mắt ti hí, khi bị bắt quả tang lộ áo Ân đen viền vàng bên dưới",
            "don_vi_hp": "🥘 nồi bếp", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Phép trừ số có 3 chữ số · Có nhớ và không có nhớ · Tìm số bị trừ/số trừ · Bài toán phần còn lại",
            "cap_do": "Buổi 6 — Phép trừ có nhớ",
            "dang_bai": [
                "Trừ 3 chữ số không nhớ (vd: 567-234)",
                "Trừ 3 chữ số có nhớ (vd: 531-278)",
                "Tìm X trong: X - A = B (tìm số bị trừ)",
                "Câu khó: bài toán 'còn lại bao nhiêu' 2 bước",
            ],
        },
        "tuyet_chieu": "🍚 Ngũ Cốc Linh Nhãn — Nhìn thấy ngay phần bị lấy trộm, tính phép trừ tức thì",
        "file_output": "scenarios/ai-6-lang-lieu.md",
        "do_kho": "⭐⭐⭐ Ải 6",
    },
    {
        "id": 7, "buoi": 7,
        "ten": "Bí Ẩn Cổ Loa",
        "subtitle": "Tiếng Gà Gáy Lúc Bình Minh",
        "thoi_ky": "~257 TCN — Âu Lạc, An Dương Vương",
        "boi_canh": (
            "Thành Cổ Loa. Tường xây ban ngày, sáng sớm hôm sau đổ sập hoàn toàn — suốt 2 năm liên tiếp. "
            "Bạch Kê Tinh ẩn trong làng, tiếng gáy bình minh xóa tri thức phân biệt số và chữ số "
            "của thợ thuyền → đọc sai bản vẽ → xây sai kích thước → tường đổ."
        ),
        "vai_choi": "⚔️ Cao Lỗ — Tổng công trình sư thiên tài Âu Lạc, thiết kế Cổ Loa 3 vòng xoắn ốc",
        "dong_minh": ["🐢 Thần Kim Quy", "👑 An Dương Vương"],
        "boss": {
            "ten": "Bạch Kê Tinh", "emoji": "🐓",
            "danh_hieu": "Tinh Gà Trắng",
            "co_che": "Tiếng gáy bình minh xóa tri thức phân biệt số và chữ số — thợ đọc sai bản vẽ, xây sai kích thước",
            "thiet_ke": "Gà trắng mắt đỏ, 9 lông đuôi dài phát sáng xanh lạnh, mỗi lông ẩn chứa một chữ số 0-9",
            "don_vi_hp": "🪶 lông đuôi", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Phân biệt Số & Chữ số · Cấu tạo số tự nhiên · Giá trị theo vị trí (ABC = A×100 + B×10 + C)",
            "cap_do": "Buổi 7 — Giá trị vị trí, cấu tạo số",
            "dang_bai": [
                "Phân biệt chữ số và số: cái nào là chữ số, cái nào là số?",
                "Chữ số ở hàng nào trong số đã cho",
                "Giá trị thật của chữ số theo vị trí (vd: '3' trong 345 = 300)",
                "Câu khó: A43 + 4B6 + 25C so với ABC + 700",
            ],
        },
        "tuyet_chieu": "🔍 Thần Nhãn Vị Số — Nhìn thấu giá trị thật của từng chữ số theo vị trí",
        "file_output": "scenarios/ai-7-co-loa.md",
        "do_kho": "⭐⭐⭐ Ải 7",
    },
    {
        "id": 8, "buoi": 8,
        "ten": "Nỏ Thần Liên Châu",
        "subtitle": "Vũ Khí Hộ Quốc Từ Vuốt Rùa Vàng",
        "thoi_ky": "~257 TCN — Âu Lạc, sau khi Cổ Loa hoàn thành",
        "boi_canh": (
            "Xưởng đúc vũ khí bí mật dưới thành Cổ Loa. Thần Kim Quy tặng một chiếc vuốt để làm lẫy nỏ thần. "
            "Cao Lỗ thiết kế Nỏ Liên Hoàn bắn vạn mũi tên một lúc — nhưng bản đúc khuôn đồng bị nội gián "
            "Triệu Đà cài cắm phá hủy. Thông số kỹ thuật về cấu tạo số và so sánh số bị xóa khỏi bản vẽ."
        ),
        "vai_choi": "⚔️ Cao Lỗ — Nhà phát minh thiên tài, chế nỏ hộ quốc bảo vệ Âu Lạc",
        "dong_minh": ["🐢 Thần Kim Quy", "👑 An Dương Vương", "🔨 Thợ đúc đồng Cổ Loa"],
        "boss": {
            "ten": "Triệu Đà Nội Gián", "emoji": "🗡️",
            "danh_hieu": "Kẻ Cài Cắm Từ Phương Bắc",
            "co_che": "Phá hủy bản đúc khuôn đồng — xóa thông số về cấu tạo số 3 chữ số và điều kiện so sánh số trong bản vẽ nỏ thần",
            "thiet_ke": "Thợ đúc đồng giả mạo, mặc áo Âu Lạc bên ngoài nhưng ẩn giáp đen Triệu bên dưới. Khi bị lộ: biến thành chiến binh Triệu mặt sắt",
            "don_vi_hp": "⚙️ bánh răng khuôn đúc", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Cấu tạo số 3 chữ số (ôn sâu và nâng cao) · So sánh số · Tìm số thỏa điều kiện cho trước",
            "cap_do": "Buổi 8 — Nâng cao cấu tạo số + so sánh có điều kiện",
            "dang_bai": [
                "Phân tích cấu tạo: cho A×100+B×10+C, tìm số",
                "So sánh hai số có chữ số đặc biệt (vd: 4A3 và 43B)",
                "Tìm số X thỏa mãn: A < X < B và X có chữ số hàng chục là C",
                "Câu khó: tìm số lớn nhất/nhỏ nhất thỏa đồng thời 2 điều kiện",
            ],
        },
        "tuyet_chieu": "🏹 Liên Châu Bách Phát — Tính chính xác từng thông số, không bao giờ sai cấu tạo số",
        "file_output": "scenarios/ai-8-no-than.md",
        "do_kho": "⭐⭐⭐ Ải 8",
    },
    {
        "id": 9, "buoi": 9,
        "ten": "Hội Quân Mê Linh",
        "subtitle": "Tiếng Trống Khởi Nghĩa Năm 40",
        "thoi_ky": "40 SCN — Khởi nghĩa Hai Bà Trưng, Mê Linh (Vĩnh Phúc)",
        "boi_canh": (
            "Mê Linh, năm 40 SCN. Thái thú Tô Định giết Thi Sách — chồng Trưng Trắc — "
            "để phá tan cuộc khởi nghĩa. Nhưng Trưng Trắc phất cờ, tiếng trống nổi dậy khắp nơi. "
            "Các cánh quân từ khắp miền đổ về: quân Cửu Chân, quân Nhật Nam, quân voi chiến Mê Linh. "
            "Cần tính quân số, voi chiến, lương thực để sắp xếp doanh trại — "
            "nhưng Tô Định dùng Xích Thư Ma phong ấn mọi phép cộng trừ trong phạm vi 1000."
        ),
        "vai_choi": "🔥 Trưng Trắc — Nữ Vương Mê Linh, lãnh tụ khởi nghĩa giải phóng dân tộc",
        "dong_minh": ["⚔️ Trưng Nhị (em gái)", "🐘 Đội Voi Chiến Mê Linh", "🏹 Các Lạc Hầu"],
        "boss": {
            "ten": "Tô Định", "emoji": "⛓️",
            "danh_hieu": "Thái Thú Bạo Ngược — Kẻ Xích Tay Dân Tộc",
            "co_che": "Xích Thư Ma — bùa phong ấn phép cộng và trừ trong phạm vi 1000 — quân số hội tụ không tính được, doanh trại không sắp xếp được",
            "thiet_ke": "Quan Hán mập tham, áo bào đỏ thêu rồng Hán, đeo vòng vàng, tay cầm cuộn giấy Xích Thư đỏ. Khi bị tấn công lộ mặt hèn nhát co rúm",
            "don_vi_hp": "⛓️ xích", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Cộng/trừ có nhớ trong phạm vi 1000 · Bài toán hội tụ (tổng nhiều thành phần) · Bài toán số dư",
            "cap_do": "Buổi 9 — Cộng trừ phạm vi 1000",
            "dang_bai": [
                "Cộng có nhớ trong 1000 (vd: 567+389=?)",
                "Trừ có nhớ trong 1000 (vd: 843-567=?)",
                "Bài toán tổng hội quân: A+B+C+D=? (4 cánh quân)",
                "Câu khó: từ tổng và một số thành phần, tìm thành phần còn lại",
            ],
        },
        "tuyet_chieu": "🔥 Phượng Hoàng Hồi Sinh — Cộng trừ trong 1000 tức thì, không cần tính từng bước",
        "file_output": "scenarios/ai-9-me-linh.md",
        "do_kho": "⭐⭐⭐⭐ Ải 9",
    },
    {
        "id": 10, "buoi": 10,
        "ten": "Chiến Thuật Voi Chiến",
        "subtitle": "Sáu Mươi Lăm Thành Giải Phóng",
        "thoi_ky": "40-43 SCN — Thời Trưng Vương trị vì",
        "boi_canh": (
            "Chiến trường đồng bằng Bắc Bộ. Hai Bà Trưng tiến quân giải phóng 65 thành trì. "
            "Đội voi chiến — vũ khí bí mật của Mê Linh — cần được chia thành các đội hình theo hàng lối "
            "để phá kỵ binh Hán. Mỗi đội voi phải chia đều số con. "
            "Mã Viện — tướng Hán thiện chiến — dùng Bùa Hán Trận xóa bảng cửu chương và phép chia "
            "trong đầu binh lính Việt."
        ),
        "vai_choi": "🔥 Trưng Trắc — Nữ Vương chiến lược, chỉ huy trận đánh giải phóng",
        "dong_minh": ["⚔️ Trưng Nhị", "🐘 Phùng Thị Chính — Đội Trưởng Voi Chiến"],
        "boss": {
            "ten": "Mã Viện", "emoji": "🐴",
            "danh_hieu": "Phục Ba Tướng Quân — Thiện Chiến Nhất Hán Triều",
            "co_che": "Bùa Hán Trận xóa bảng cửu chương và phép chia trong đầu binh lính — không chia được đội hình → hỗn loạn trước kỵ binh",
            "thiet_ke": "Tướng Hán oai vệ trên ngựa trắng, giáp bạc Hán triều, cầm cờ Phục Ba. Theo sau là đội hình kỵ binh Hán hàng trăm người",
            "don_vi_hp": "🐴 kỵ binh", "so_hp": 6,
        },
        "toan": {
            "chu_de": "Bảng nhân 2, 3, 4, 5 · Phép chia tương ứng · Chia hết và chia có dư · Bài toán chia đều",
            "cap_do": "Buổi 10 — Bảng nhân và phép chia",
            "dang_bai": [
                "Bảng nhân (vd: 7×4=?, 8×5=?)",
                "Phép chia từ bảng nhân (vd: 24:4=?, 45:5=?)",
                "Chia có dư (vd: 25:4=6 dư 1)",
                "Câu khó: bài toán chia đều đội hình voi — N voi chia thành K đội, mỗi đội bao nhiêu voi?",
            ],
        },
        "tuyet_chieu": "🐘 Tượng Binh Trận Đồ — Nhân chia tức thì, chia đội hình nhanh hơn địch ra lệnh",
        "file_output": "scenarios/ai-10-voi-chien.md",
        "do_kho": "⭐⭐⭐⭐ Ải 10",
    },
    {
        "id": 11, "buoi": 11,
        "ten": "Trận Bạch Đằng — Cắm Cọc",
        "subtitle": "Bẫy Sắt Dưới Đáy Sông",
        "thoi_ky": "938 SCN — Ngô Quyền, sông Bạch Đằng",
        "boi_canh": (
            "Sông Bạch Đằng, tháng 12 năm 938. Ngô Quyền thiết kế trận địa cọc gỗ bịt sắt dưới lòng sông. "
            "Khi thủy triều lên — cọc chìm, hạm đội Nam Hán đi vào. Khi thủy triều xuống — cọc lộ ra, "
            "chiến thuyền địch bị đâm thủng. Cần tính chính xác số cọc, khoảng cách và thời điểm thủy triều. "
            "Lưu Hoằng Tháo — Thái tử Nam Hán — dùng Phong Thủy Ấn phong ấn phép nhân và đo lường."
        ),
        "vai_choi": "⚓ Ngô Quyền — Đại Thắng Bạch Đằng, Khai Quốc Vương nước Việt độc lập",
        "dong_minh": ["🔨 Đội Thợ Cọc Bạch Đằng (hàng nghìn người)", "🌊 Dòng sông Bạch Đằng (đồng minh tự nhiên)"],
        "boss": {
            "ten": "Lưu Hoằng Tháo", "emoji": "⛵",
            "danh_hieu": "Thái Tử Nam Hán — Thủy Quân Kiêu Ngạo",
            "co_che": "Phong Thủy Ấn phong ấn phép nhân và đo lường — không tính được số cọc cần cắm và thời điểm thủy triều",
            "thiet_ke": "Thái tử trẻ kiêu ngạo trên chiến thuyền lớn, áo bào vàng Nam Hán, cờ rồng. Lộ vẻ hoảng loạn khi cọc cắm trúng thuyền",
            "don_vi_hp": "⛵ chiến thuyền", "so_hp": 7,
        },
        "toan": {
            "chu_de": "Phép nhân số có 2 chữ số với 1 chữ số · Bài toán đo lường (dài, rộng, chu vi) · Bài toán thời gian (giờ, phút)",
            "cap_do": "Buổi 11 — Nhân có nhớ + đo lường + thời gian",
            "dang_bai": [
                "Nhân có nhớ (vd: 34×3=?, 25×4=?)",
                "Tính chu vi hình chữ nhật: C = (dài+rộng)×2",
                "Đổi đơn vị đo: m ↔ dm ↔ cm",
                "Câu khó: bài toán thủy triều — thủy triều lên lúc 6 giờ, mỗi giờ lên 3dm, bao giờ đạt độ cao X?",
            ],
        },
        "tuyet_chieu": "⚓ Hải Thần Trận Pháp — Tính nhân và đo lường trong chớp mắt, cắm đúng từng cọc",
        "file_output": "scenarios/ai-11-bach-dang-coc.md",
        "do_kho": "⭐⭐⭐⭐ Ải 11",
    },
    {
        "id": 12, "buoi": 12,
        "ten": "Trận Bạch Đằng — Thủy Triều Phán Xét",
        "subtitle": "Giờ Khắc Nước Rút",
        "thoi_ky": "938 SCN — Sáng ngày quyết chiến, sông Bạch Đằng",
        "boi_canh": (
            "Bình minh ngày quyết chiến. Hạm đội Nam Hán 500 chiến thuyền đã tiến vào bẫy cọc. "
            "Nước bắt đầu rút. Cọc lộ dần lên mặt nước. Ngô Quyền phải ra lệnh tấn công "
            "đúng thời điểm — sớm quá địch thoát được, muộn quá trời tối mất lợi thế. "
            "Hạm đội Nam Hán điên cuồng phản công, tạo Ma Trận Hỗn Độn phá mọi phép tính chia đội của quân Việt."
        ),
        "vai_choi": "⚓ Ngô Quyền — Thống soái trận đánh thay đổi lịch sử nghìn năm",
        "dong_minh": ["⚔️ Toàn bộ quân Việt trên bờ và thuyền nhỏ", "🌊 Thủy triều sông Bạch Đằng"],
        "boss": {
            "ten": "Hạm Đội Nam Hán", "emoji": "🔱",
            "danh_hieu": "500 Chiến Thuyền Phương Bắc",
            "co_che": "Ma Trận Hỗn Độn — điên cuồng tấn công phá vỡ mọi phép tính chia đội phản công của Ngô Quyền",
            "thiet_ke": "Hàng loạt chiến thuyền bốc lửa trên sông, binh Hán hoảng loạn, nước đỏ. Mỗi đợt tấn công là một đợt sóng thuyền lửa",
            "don_vi_hp": "🔱 đợt tấn công", "so_hp": 7,
        },
        "toan": {
            "chu_de": "Phép chia có nhớ · Giải toán có lời văn hai phép tính · Bài toán thời gian · Tổng hợp nhân-chia",
            "cap_do": "Buổi 12 — Chia có nhớ + toán lời văn 2 bước",
            "dang_bai": [
                "Chia có nhớ (vd: 96:3=?, 84:4=?)",
                "Bài toán 2 phép tính có lời văn",
                "Tính giờ phút: thủy triều rút trong bao nhiêu giờ, từ lúc X đến lúc nào?",
                "Câu khó: tổng hợp — X chiến thuyền chia thành A nhóm, mỗi nhóm Y thuyền, còn thừa bao nhiêu?",
            ],
        },
        "tuyet_chieu": "⚡ Phong Lôi Tổng Tấn Công — Ra lệnh tấn công đúng thời điểm, tính chia siêu tốc",
        "file_output": "scenarios/ai-12-bach-dang-tran.md",
        "do_kho": "⭐⭐⭐⭐⭐ Ải 12",
    },
    {
        "id": 13, "buoi": 13,
        "ten": "Cờ Lau Tập Trận",
        "subtitle": "Đinh Bộ Lĩnh Dẹp Loạn 12 Sứ Quân",
        "thoi_ky": "944-968 SCN — Từ cánh đồng cờ lau đến ngai vàng Hoa Lư",
        "boi_canh": (
            "Hoa Lư (Ninh Bình). Đinh Bộ Lĩnh — từ cậu bé dẫn bạn chơi trận giả bằng cờ lau trên đồng "
            "đến vị anh hùng dẹp loạn 12 sứ quân, thống nhất đất nước sau loạn 12 sứ quân hỗn chiến. "
            "Ải cuối — 12 sứ quân cài 12 bùa toán học khác nhau, mỗi bùa phá một kỹ năng đã học từ ải 1-12. "
            "Đánh bại từng bùa = thu phục từng sứ quân."
        ),
        "vai_choi": "👑 Đinh Bộ Lĩnh — Đinh Tiên Hoàng, Hoàng Đế Đầu Tiên Đại Cồ Việt (968 SCN)",
        "dong_minh": ["⚔️ Đinh Điền, Nguyễn Bặc (tướng tâm phúc)", "🌾 Dân khắp 12 châu ủng hộ"],
        "boss": {
            "ten": "Liên Minh 12 Sứ Quân", "emoji": "🏯",
            "danh_hieu": "Mười Hai Thế Lực Chia Cắt Đất Nước",
            "co_che": "Ma Trận Chia Cắt — 12 sứ quân tạo 12 bùa toán học khác nhau ôn lại toàn bộ kiến thức từ ải 1-12. Đánh bại từng bùa = thu phục từng sứ quân",
            "thiet_ke": "12 tướng lĩnh mặc giáp 12 màu khác nhau, đứng thành vòng tròn trên bản đồ Đại Việt. Mỗi người bị đánh bại thì quỳ xuống và vùng lãnh thổ sáng màu vàng",
            "don_vi_hp": "🏯 thành lũy", "so_hp": 8,
        },
        "toan": {
            "chu_de": "Giải toán có lời văn tổng hợp (3-4 bước) · Ôn tập toàn bộ ải 1-12 · Điền dấu phép tính · Toán đố sáng tạo",
            "cap_do": "Buổi 13 — Ải cuối, khó nhất, tổng hợp",
            "dang_bai": [
                "Toán lời văn 3 bước (kết hợp cộng trừ nhân chia)",
                "Điền dấu +−×÷ vào ô trống để phép tính đúng",
                "Bài ôn tập bất ngờ từ ải ngẫu nhiên (ải 1→12)",
                "Câu sáng tạo: một bài toán có nhiều cách giải, tìm cách ngắn nhất",
            ],
        },
        "tuyet_chieu": "👑 Thiên Hạ Nhất Thống — Giải được mọi bài toán bằng mọi phương pháp",
        "file_output": "scenarios/ai-13-dinh-bo-linh.md",
        "do_kho": "⭐⭐⭐⭐⭐ Ải 13 — Ải cuối, tổng hợp, khó nhất",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT (sẽ được cache — chỉ tốn full price lần đầu)
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
# VAI TRÒ CỦA BẠN
Bạn là người viết kịch bản game giáo dục VInaStudy. Tạo kịch bản nhập vai lịch sử Việt Nam kết hợp bài tập Toán lớp 3 nâng cao (HSG).

# GAME: CHIẾN BINH TOÁN — VINASTUDY

## Đối tượng
Học sinh lớp 3, 8-9 tuổi, chương trình ôn luyện HSG (nâng cao, không phải đại trà).
Nền tảng: Telegram WebApp (HTML/CSS/JS).

## Cốt truyện bao quát
Năm 2026, một thực thể hắc ám từ phương Bắc can thiệp vào trục thời gian, xóa sổ chiến công lịch sử Việt Nam. Cỗ máy Đông Sơn — công nghệ cổ đại của tổ tiên — thức giấc và triệu tập **Chiến Binh Toán** (học sinh lớp 3) xuyên thời gian về quá khứ để VÁ LẠI LỊCH SỬ bằng tri thức toán học.

## Nhân vật đồng hành (xuất hiện ở MỌI ải)
- **Thầy Long**: Mentor ở năm 2026, kết nối qua bộ đàm holographic hình trống đồng nhỏ. Giọng trầm ấm, học thức, khuyến khích học sinh. Giảng giải toán học và bối cảnh lịch sử. Khi học sinh đúng → ca ngợi; khi sai → gợi ý nhẹ nhàng.
- **Cỗ máy Đông Sơn**: Trợ lý AI (hình tượng trống đồng phát sáng, giọng máy). Phân tích kỹ thuật, kích hoạt Hệ Thống Gợi Mở (scaffolding) khi học sinh sai 2 lần liên tiếp.

## Cơ chế Boss
- Mỗi ải có 1 Boss do thực thể phương Bắc tạo ra để phá hoại lịch sử Việt.
- Boss có CƠ CHẾ PHÁ HOẠI cụ thể liên quan trực tiếp đến chủ đề toán của ải đó.
- Học sinh trả lời đúng câu hỏi toán → tấn công Boss → giải phóng phong ấn.
- **HP Học sinh**: ❤️❤️❤️ (3 tim — mất 1 tim mỗi lần sai).
- **HP Boss**: biểu tượng phù hợp × số lượng (thường 6-8).
- Sai 2 lần cùng một câu → Cỗ máy Đông Sơn kích hoạt scaffolding 2 bước.
- Tim về 0 → Game Over → thử lại (không mất tiến độ ải).

# YÊU CẦU TOÁN HỌC (QUAN TRỌNG)
- Cấp độ: **Lớp 3 HSG nâng cao** — khó hơn chương trình đại trà, phù hợp học sinh giỏi.
- Câu hỏi Boss: **6 câu** (hoặc 7-8 với ải khó), tăng dần độ khó:
  - 🌱 Câu 1-2: Nhận biết, áp dụng trực tiếp công thức.
  - ⚔️ Câu 3-4: Vận dụng, kết hợp 2 bước.
  - 🏹 Câu 5: Vận dụng cao — học sinh giỏi mới làm được nhanh.
  - 🏆 Câu cuối: **Nâng cao HSG thật sự** — câu ràng buộc, biến chứa chữ, hoặc cần suy luận đặc biệt.
- Mỗi câu: **4 đáp án A/B/C/D**, 1 đúng, 3 sai **hợp lý** (không được sai quá rõ ràng).
- Câu sai phổ biến: cho đáp án từ lỗi sai điển hình của học sinh (vd: bỏ số nhớ, đọc sai hàng...).
- Mỗi câu có **2 gợi ý scaffolding** (bước 1 và bước 2) — gợi ý từng bước, KHÔNG cho đáp án thẳng.
- Câu giải thích đáp án đúng (Thầy Long nói) — liên kết lại lịch sử.
- **Tối thiểu 3 giây** mỗi câu (chặn đoán mò).

# PHONG CÁCH VIẾT
- **Ngôn ngữ**: Tiếng Việt thuần, tự nhiên.
- **Nhập vai ngôi thứ nhất**: Học sinh **LÀ** nhân vật lịch sử. Thầy Long gọi nhân vật bằng tên ("Cao Lỗ!", "Lạc Long Quân!") hoặc "em". Nhân vật lịch sử xưng "ta" hoặc "tôi".
- **Lịch sử**: Trung thực với nguồn sử liệu Việt Nam, có thể thêm yếu tố huyền thoại phù hợp.
- **Cảm xúc**: Hùng tráng, kịch tính, thiêng liêng nhưng không quá bạo lực — phù hợp trẻ 8-9 tuổi.
- **Thầy Long**: Luôn kết nối toán học với bối cảnh lịch sử ("Vì sao phép trừ lại quan trọng lúc này...").
- **Cỗ máy Đông Sơn**: Giọng máy, ngắn gọn, kỹ thuật ("Phân tích hoàn tất, tướng quân...").
- **Boss**: Có lời thoại riêng, tính cách phản diện rõ nhưng không tàn ác thái quá.

# ĐỊNH DẠNG ĐẦU RA (TUÂN THỦ CHÍNH XÁC)

```
# ẢI [N]: [TÊN IN HOA]
## "[Subtitle]"

> **Toán:** Buổi [N] — [Chủ đề toán]
> **Tuyệt chiêu:** [emoji] **[Tên tuyệt chiêu]** — [Mô tả ngắn]
> **Mini-game 1:** [tên file] — [Mô tả]
> **Mini-game 2:** [tên file] — [Mô tả]
> **Boss:** [emoji] **[Tên Boss]** ([Tên Hán] — [Mô tả]) — [Cơ chế phá hoại]
> **Vai chơi:** [emoji] **[Tên Nhân Vật]** — [Mô tả ngắn]
> **Đồng minh:** [emoji] Tên1 · [emoji] Tên2
> **Bối cảnh lịch sử:** [Thời kỳ và mô tả ngắn]
> **Độ khó:** [số sao] [mô tả]

---

## 📜 TƯ LIỆU LỊCH SỬ (Nền tảng kịch bản)

### Bối cảnh: [Tiêu đề]
[2-3 đoạn bối cảnh lịch sử, có trích dẫn sử liệu thật nếu có]

### [Chủ thể/Địa điểm quan trọng]
[Thông tin chi tiết, có thể dùng bullet points và/hoặc ASCII art]

### Thủ phạm: [Tên Boss]
[Mô tả Boss, nguồn gốc, cơ chế phá hoại liên quan đến toán]

---

## 🎬 KỊCH BẢN CHI TIẾT

### CẢNH MỞ — Em là [Tên Nhân Vật]

> *[Mô tả cảnh mở — âm thanh, hình ảnh, bầu không khí]*

**Thầy Long:**
> "[Lời thoại giới thiệu — kể cho học sinh biết nhân vật là ai, nhiệm vụ là gì, tại sao toán học quan trọng lúc này]"

> *[Tiếp tục mô tả cảnh, giới thiệu đồng minh, tình huống nguy cấp]*

**[Tên nhân vật đồng minh]** *(mô tả)*:
> "[Lời thoại — đặt ra vấn đề cần giải quyết]"

**Cỗ máy Đông Sơn** *(giọng máy, từ trống đồng)*:
> "[Phân tích tình huống kỹ thuật, xác định nguyên nhân liên quan đến toán]"

---

### CẢNH 1 — [Tên cảnh]

> *[Mô tả bối cảnh]*

[Lời thoại và tình huống...]

---

### CẢNH 2 — [Tên cảnh] (Thường là phần lý thuyết)

> *[Không gian chuyển sang không gian học — màu sắc đặc trưng của ải]*

**Thầy Long:**
> "[Giảng bài — kết nối lịch sử với toán học một cách tự nhiên]"

---

#### 📖 KIẾN THỨC 1 — [Tiêu đề]

```
[Box kiến thức — dùng ASCII art box nếu phù hợp, hoặc trình bày rõ ràng]
```

**Thầy Long:**
> "[Giải thích thêm, ví dụ cụ thể liên quan đến câu chuyện]"

---

#### 📖 KIẾN THỨC 2 — [Tiêu đề]
...

---

### CẢNH 3 — Rèn Tuyệt Chiêu (Mini-game)

> *Cỗ máy Đông Sơn: "[Giới thiệu mini-game]"*

**Mini-game 1 — [Tên]:**
> [Mô tả cơ chế mini-game]

**Mini-game 2 — [Tên]:**
> [Mô tả cơ chế mini-game]

---

### CẢNH 4 — [Tên Boss] lộ diện

> *[Cảnh Boss xuất hiện — không khí kịch tính]*

**[Tên Boss]** *(mô tả)*:
> "[Lời đe dọa — liên quan đến cơ chế phá hoại toán học]"

**Cỗ máy Đông Sơn:**
> "[Giải thích cơ chế Boss, cách tấn công Boss bằng toán]"

---

## ⚔️ TRẬN BOSS — [N] [ĐƠN VỊ HP]

*HP System:*
- **[Tên nhân vật]:** ❤️❤️❤️ (3 tim — mất 1 mỗi lần sai)
- **[Tên Boss]:** [emoji]×[số] ([N] lần — mỗi câu đúng phá 1)
- Sai 2 lần cùng câu → Cỗ máy Đông Sơn kích hoạt gợi ý 2 bước
- Tim về 0 → Game Over → Thử lại boss (không mất tiến độ)

---

### [Emoji HP] [ĐƠN VỊ] 1 — [Tên câu hỏi] ([Emoji độ khó])

> *[Cảnh ngắn — diễn tiến câu chuyện, đặt tình huống cho câu hỏi]*

**Câu hỏi:**
> [Đề bài câu hỏi, có thể dùng **bold** cho số quan trọng]

- ○ [Đáp án A sai] &emsp; ● **[Đáp án B đúng]** ✅ &emsp; ○ [Đáp án C sai] &emsp; ○ [Đáp án D sai]

> **Đúng:** *Thầy Long: "[Giải thích ngắn + kết nối lịch sử]"*

> **Sai lần 1 → Cỗ máy Đông Sơn (Bước 1):**
> "💡 [Gợi ý bước 1 — không cho đáp án, chỉ hướng dẫn cách suy nghĩ]"

> **Sai lần 2 → (Bước 2):**
> "💡 [Gợi ý bước 2 — chi tiết hơn, dẫn dắt gần đến đáp án nhưng học sinh vẫn phải tự tính]"

---

[Lặp lại cho câu 2, 3... đến câu cuối]

---

### [Emoji HP] [ĐƠN VỊ] [CUỐI] — Trận cuối: [Tên] (🏆)

[Câu khó nhất — HSG thật sự]

> **Đúng → Animation:** [Boss bị đánh bại]

---

### CẢNH 5 — [Tên đồng minh] hạ thủ / [Boss] thất bại

> *[Cảnh Boss bị đánh bại — liên kết trở lại câu chuyện lịch sử]*

---

### CẢNH KẾT — [Tên — kết quả lịch sử]

> *[Timelapse hoặc cảnh kết — lịch sử được vá lại, nhiệm vụ hoàn thành]*

**[Tên nhân vật]** *(nghẹn ngào)*:
> "[Lời kết — liên hệ toán học với chiến thắng lịch sử]"

**Thầy Long:**
> "Tuyệt vời! [Nhận xét về chiến thắng]. Bài học hôm nay: **[1-2 câu tóm tắt kiến thức toán, dạng: 'Từ khóa toán 1 · Từ khóa 2 · Kết luận']**"

---

## 🎯 THIẾT KẾ MINI-GAME: [Tên mini-game 1]
> [Mô tả mini-game để dev implement]

---

## 🎯 THIẾT KẾ MINI-GAME 2: [Tên mini-game 2]
> [Mô tả mini-game để dev implement]

---

## 📊 NGÂN HÀNG CÂU HỎI BOSS (Mở rộng)

### Nhóm 🌱 — Nhận biết cơ bản
1. [Dạng bài 1]
2. [Dạng bài 2]
3. [Dạng bài 3]

### Nhóm ⚔️ — Vận dụng trực tiếp
1. [...]

### Nhóm 🏹 — Vận dụng cao
1. [...]

---

## 🗨️ LỜI THOẠI THEO TÌNH HUỐNG

**Trả lời đúng lần đầu:**
> *Thầy Long:* "[...]"
> *Cỗ máy Đông Sơn:* "[...]"

**Trả lời sai lần 1:**
> *Thầy Long:* "[...]"

**Trả lời sai lần 2 → Scaffolding:**
> *Thầy Long:* "Cỗ máy Đông Sơn — hỗ trợ đi!"

**Mất tim:**
> *Thầy Long:* "[...]"

**Hoàn thành [N]/[N]:**
> *Thầy Long:* "[Tên nhân vật] — [Tên học sinh]! [Số câu đúng] câu đúng trong [Y giây]. [Kết quả lịch sử] — một phần nhờ bộ óc của em hôm nay!"

---

## 🏅 PHẦN THƯỞNG

| Thành tích | Điều kiện | Phần thưởng |
|---|---|---|
| [Tên thành tích 1] | Hoàn thành ải | Huy hiệu + mở Ải [N+1] |
| [Tên thành tích 2] | Trả lời đúng trong < 5 giây/câu | Huy hiệu đặc biệt |
| [Tên thành tích 3] | [N]/[N] đúng, không dùng scaffolding | Huy hiệu vàng |
| [Tên thành tích 4] | [Điều kiện đặc biệt liên quan lịch sử] | [Phần thưởng đặc biệt] |

---

## 🎨 THIẾT KẾ VISUAL

- **Bầu trời/Bối cảnh:** [Mô tả màu sắc, thời điểm, bầu không khí]
- **Boss:** [Mô tả visual chi tiết khi xuất hiện và khi bị tấn công]
- **Nhân vật chính:** [Mô tả visual ngắn]
- **Mini-game:** [Layout và cơ chế tương tác]
- **Boss battle:** [Hiệu ứng khi đúng/sai]

---

## 🔧 GHI CHÚ KỸ THUẬT

- **State:** `INTRO → THEORY → MINIGAME_1 → MINIGAME_2 → BOSS_SCENE → BOSS_BATTLE → WIN`
- **Boss sẵn dùng:** [N] câu hỏi cố định theo thứ tự (ổn định cho MVP)
- **Thời gian tối thiểu mỗi câu boss:** 3 giây (chặn đoán mò)
- **Adaptive:** sau boss, có thể mở rộng sang Question Bank ngẫu nhiên theo nhóm 🌱⚔️🏹🏆

---

*Ải [N] · [Địa điểm] · [Năm/Thế kỷ] · [Tên triều đại/giai đoạn]*
*Toán Lớp 3 HSG: Buổi [N] — [Chủ đề toán]*
*Nguồn lịch sử: [Sử liệu tham khảo]*
```

# NGUYÊN TẮC QUAN TRỌNG
1. Câu hỏi Boss PHẢI gắn chặt với câu chuyện — học sinh làm toán VÌ câu chuyện cần, không phải làm toán xong mới có chuyện.
2. Lịch sử phải chính xác — đừng bịa đặt sự kiện, nhân vật thật có thể nói lời thoại hư cấu nhưng không trái lịch sử.
3. Đáp án sai phải hợp lý — chọn đáp án sai từ lỗi sai điển hình của học sinh lớp 3.
4. Scaffolding không được cho đáp án thẳng — phải để học sinh tự tính bước cuối.
5. Mỗi ải phải có ít nhất 1 câu hỏi tích hợp chữ số/biến (HSG), không chỉ toán số cụ thể.
""".strip()


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def build_scenario_prompt(ai: dict) -> str:
    """Xây dựng user prompt để generate kịch bản đầy đủ cho một ải."""
    boss = ai["boss"]
    toan = ai["toan"]
    dong_minh = " · ".join([f"{a}" for a in ai["dong_minh"]])

    lines = [
        f"# TẠO KỊCH BẢN ẢI {ai['id']}: {ai['ten'].upper()}",
        f'## "{ai["subtitle"]}"',
        "",
        "## DỮ LIỆU ẢI",
        f"- **ID**: Ải {ai['id']} · Buổi {ai['buoi']}",
        f"- **Thời kỳ lịch sử**: {ai['thoi_ky']}",
        f"- **Bối cảnh**: {ai['boi_canh']}",
        f"- **Vai chơi (học sinh là)**: {ai['vai_choi']}",
        f"- **Đồng minh**: {dong_minh}",
        "",
        "## BOSS",
        f"- **Tên**: {boss['emoji']} {boss['ten']} — {boss['danh_hieu']}",
        f"- **Cơ chế phá hoại**: {boss['co_che']}",
        f"- **Thiết kế visual**: {boss['thiet_ke']}",
        f"- **HP Boss**: {boss['don_vi_hp']} × {boss['so_hp']} (= {boss['so_hp']} câu hỏi)",
        "",
        "## TOÁN HỌC",
        f"- **Chủ đề**: {toan['chu_de']}",
        f"- **Cấp độ**: {toan['cap_do']}",
        "- **Dạng bài Boss** (từ dễ đến khó):",
        *[f"  {i+1}. {d}" for i, d in enumerate(toan["dang_bai"])],
        "",
        "## TUYỆT CHIÊU",
        f"- {ai['tuyet_chieu']}",
        "",
        "## ĐỘ KHÓ",
        f"- {ai['do_kho']}",
        "",
        "---",
        "",
        "## YÊU CẦU",
        f"Tạo TOÀN BỘ kịch bản đầy đủ cho Ải {ai['id']} theo định dạng trong System Prompt.",
        "Bao gồm:",
        "1. Header metadata block đầy đủ",
        "2. TƯ LIỆU LỊCH SỬ: 2-3 mục, có trích dẫn sử liệu thật nếu có",
        f"3. KỊCH BẢN CHI TIẾT: CẢNH MỞ + CẢNH 1 + CẢNH 2 (lý thuyết, ≥2 mục kiến thức) + CẢNH 3 (mini-game) + CẢNH 4 (Boss lộ diện)",
        f"4. TRẬN BOSS: {boss['so_hp']} câu hỏi đầy đủ (đề bài + 4 đáp án + scaffolding 2 bước + giải thích đúng)",
        "5. CẢNH 5 + CẢNH KẾT",
        "6. Mini-game design (2 mini-games)",
        "7. Ngân hàng câu hỏi mở rộng (≥9 câu theo 3 nhóm)",
        "8. Lời thoại theo tình huống",
        "9. Phần thưởng (4 huy hiệu)",
        "10. Thiết kế visual",
        "11. Ghi chú kỹ thuật",
        "",
        "Câu hỏi Boss: tăng dần độ khó 🌱🌱 → ⚔️⚔️ → 🏹 → 🏆",
        "Câu cuối (🏆) phải là dạng HSG thật sự (có biến chữ, ràng buộc, hoặc suy luận đặc biệt).",
        "Đáp án sai phải hợp lý (từ lỗi sai điển hình).",
        "Scaffolding không được cho đáp án thẳng.",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# API CALL
# ═══════════════════════════════════════════════════════════════════════════════

def generate_scenario(ai: dict, client: anthropic.Anthropic, model: str, dry_run: bool = False) -> str:
    """Gọi Claude API để generate kịch bản. Trả về markdown content."""
    prompt = build_scenario_prompt(ai)

    if dry_run:
        print("\n" + "="*70)
        print(f"[DRY RUN] Ải {ai['id']}: {ai['ten']}")
        print("="*70)
        print("[SYSTEM PROMPT] (xem biến SYSTEM_PROMPT)")
        print("\n[USER PROMPT]:")
        print(prompt)
        return ""

    print(f"  → Gọi API cho Ải {ai['id']}: {ai['ten']}...")

    message = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # Cache system prompt
            }
        ],
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    content = message.content[0].text
    usage = message.usage
    print(f"     ✓ Tokens — input: {usage.input_tokens}, output: {usage.output_tokens}", end="")
    if hasattr(usage, "cache_read_input_tokens") and usage.cache_read_input_tokens:
        print(f", cache_read: {usage.cache_read_input_tokens}", end="")
    if hasattr(usage, "cache_creation_input_tokens") and usage.cache_creation_input_tokens:
        print(f", cache_created: {usage.cache_creation_input_tokens}", end="")
    print()

    return content


# ═══════════════════════════════════════════════════════════════════════════════
# FILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def get_output_path(ai: dict) -> Path:
    return BASE_DIR / ai["file_output"]


def file_exists(ai: dict) -> bool:
    return get_output_path(ai).exists()


def save_scenario(ai: dict, content: str) -> Path:
    path = get_output_path(ai)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Prepend generation metadata
    header = (
        f"<!-- Generated by generate_content.py · {datetime.now().strftime('%Y-%m-%d %H:%M')} -->\n"
        f"<!-- Ải {ai['id']} · Buổi {ai['buoi']} · {ai['thoi_ky']} -->\n\n"
    )
    path.write_text(header + content, encoding="utf-8")
    print(f"     ✓ Saved → {path}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CLI
# ═══════════════════════════════════════════════════════════════════════════════

def list_status():
    print("\n📋 TRẠNG THÁI CÁC ẢI:")
    print("-" * 60)
    for ai in AILS:
        path = get_output_path(ai)
        exists = path.exists()
        status = "✅" if exists else "❌"
        size = f"({path.stat().st_size // 1024}KB)" if exists else "(chưa có)"
        print(f"  Ải {ai['id']:2d} | {status} | {ai['ten']:<35} | {size}")
    print()


def run(args):
    # Load API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        # Try .env file
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
        if not api_key:
            print("❌ Lỗi: Không tìm thấy ANTHROPIC_API_KEY.")
            print("   Set environment variable: set ANTHROPIC_API_KEY=sk-ant-...")
            print("   Hoặc thêm vào file .env: ANTHROPIC_API_KEY=sk-ant-...")
            sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key) if not args.dry_run else None

    # Determine which ải to process
    if args.list:
        list_status()
        return

    if args.all:
        target_ails = AILS
    elif args.ai:
        ids = set(args.ai)
        target_ails = [a for a in AILS if a["id"] in ids]
        if not target_ails:
            print(f"❌ Không tìm thấy ải: {ids}")
            sys.exit(1)
    else:
        print("Dùng --ai N [N...] hoặc --all để chỉ định ải cần generate.")
        print("Dùng --list để xem trạng thái tất cả ải.")
        sys.exit(1)

    model = args.model or DEFAULT_MODEL

    print(f"\n🎮 VInaStudy Content Generator")
    print(f"   Model: {model}")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'GENERATE'}")
    print(f"   Ải: {[a['id'] for a in target_ails]}")
    if not args.force:
        skip = [a for a in target_ails if file_exists(a)]
        if skip:
            print(f"   ⚠️  Bỏ qua (đã có file, dùng --force để ghi đè): {[a['id'] for a in skip]}")
        target_ails = [a for a in target_ails if not file_exists(a)] if not args.force else target_ails
    print()

    if not target_ails:
        print("Không có ải nào cần generate. Dùng --force để ghi đè file đã có.")
        return

    total = len(target_ails)
    for i, ai in enumerate(target_ails, 1):
        print(f"[{i}/{total}] Ải {ai['id']}: {ai['ten']}")
        try:
            content = generate_scenario(ai, client, model, dry_run=args.dry_run)
            if content and not args.dry_run:
                save_scenario(ai, content)
        except anthropic.APIError as e:
            print(f"     ❌ API Error: {e}")
        except Exception as e:
            print(f"     ❌ Error: {e}")
            raise
        print()

    if not args.dry_run:
        print(f"✅ Hoàn thành! Generated {total} kịch bản.")
        list_status()


def main():
    parser = argparse.ArgumentParser(
        description="VInaStudy — Auto-generate kịch bản lịch sử + bài tập toán",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python generate_content.py --list
  python generate_content.py --ai 8 9 10
  python generate_content.py --all
  python generate_content.py --ai 8 --dry-run
  python generate_content.py --all --force --model claude-sonnet-4-5
        """,
    )
    parser.add_argument("--ai", type=int, nargs="+", metavar="N",
                        help="Số thứ tự ải cần generate (vd: --ai 8 9 10)")
    parser.add_argument("--all", action="store_true",
                        help="Generate tất cả ải còn thiếu")
    parser.add_argument("--force", action="store_true",
                        help="Ghi đè file đã có")
    parser.add_argument("--dry-run", action="store_true",
                        help="Chỉ hiển thị prompt, không gọi API")
    parser.add_argument("--list", action="store_true",
                        help="Liệt kê trạng thái tất cả ải")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"Model Claude (default: {DEFAULT_MODEL})")

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
