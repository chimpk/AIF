# 503043 – Introduction to Artificial Intelligence (Final Project)

Repository cho đồ án cuối kỳ môn Trí tuệ Nhân tạo gồm 3 bài toán độc lập:
- **Task 1:** N-Queens (Propositional Logic / PySAT Glucose3 & Local Search Min-Conflicts) — **Người A**
- **Task 2:** Tank Battle (Adversarial Search Minimax/Alpha-Beta, PyGame UI & Plugin Arena) — **AI: Người A | Engine & UI: Người B**
- **Task 3:** Kakuro (CSP, Constraint Propagation FC/GAC, Backtracking & Domain Visualization UI) — **Người B**

---

## 1. Tài liệu hướng dẫn cho nhóm (Đọc trước khi code)

Toàn bộ tài liệu nằm gọn trong 2 file dễ đọc tại thư mục [`docs/`](docs/):
1. **[`docs/01_tong_quan_va_phan_cong.md`](docs/01_tong_quan_va_phan_cong.md)**: Bảng chia việc A/B, cách làm song song không chờ nhau, checklist 6 tuần và quy tắc Git.
2. **[`docs/02_huong_dan_code_3_bai.md`](docs/02_huong_dan_code_3_bai.md)**: Giải thích thuật toán từng bài dễ hiểu + bảng danh sách các file và hàm mỗi người cần viết.

---

## 2. Cài đặt môi trường (Python 3.11)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## 3. Lệnh chạy từng bài (sau khi cài đặt)

```bash
# Task 1: N-Queens
python -m task1_nqueens solve --method sat --n 8 --show
python -m task1_nqueens solve --method mc-max --n 100 --seed 0

# Task 2: Tank Battle
python -m task2_tank_battle gui
python -m task2_tank_battle match --p0 A-H_ALPHABETA --p1 random --map src/task2_tank_battle/maps/small_7x7.map --headless

# Task 3: Kakuro
python -m task3_kakuro solve --puzzle src/task3_kakuro/data/puzzles/large_9x9.json --preset mac-mrvdeg-lcv
python -m task3_kakuro ui --puzzle src/task3_kakuro/data/puzzles/large_9x9.json
```
