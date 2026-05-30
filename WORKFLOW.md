# Quy trình làm việc VInaStudy Bot

## Phân vai

| Tài khoản | Tab Terminal | Vai trò |
|-----------|-------------|---------|
| nam.nguyenhuu@gmail.com | 🧑‍💻 Claude - Cá nhân | Tech Lead: thiết kế, phân task, review, merge |
| huongnt49@tcbs.com.vn | 🏢 Claude - Công ty | Dev: code feature, fix bug, viết test |

---

## Branch Strategy

```
main          ← production, chỉ Tech Lead merge vào
dev           ← integration branch, merge feature vào đây trước
feature/xxx   ← mỗi task một branch riêng
fix/xxx       ← branch fix bug
```

---

## Quy trình mỗi ngày

### 1. Tech Lead mở đầu ngày (tab Cá nhân)
```powershell
git checkout dev
git pull origin dev
# Xem TASKS.md, assign task cho Dev
```

### 2. Dev nhận task (tab Công ty)
```powershell
git checkout dev
git pull origin dev
git checkout -b feature/ten-task
# Code...
claude  # dùng Claude công ty để hỗ trợ
git add .
git commit -m "feat: mô tả task"
git push origin feature/ten-task
```

### 3. Tech Lead review và merge (tab Cá nhân)
```powershell
git checkout dev
git merge feature/ten-task
# Test chạy ok
git push origin dev
```

### 4. Release lên main (Tech Lead, cuối sprint)
```powershell
git checkout main
git merge dev
git push origin main
```

---

## File phân công task: TASKS.md

Tech Lead viết task vào TASKS.md, Dev đọc và thực hiện.

---

## Rules

- **Không ai commit thẳng vào `main`**
- **Dev chỉ làm trên `feature/` branch**
- **Tech Lead review trước khi merge vào `dev`**
- **Mỗi task = 1 branch = 1 commit rõ ràng**
