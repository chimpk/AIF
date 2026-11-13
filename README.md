# 503043 – Introduction to Artificial Intelligence (Final Project)

> **Trạng thái hiện tại:**
> - **Task 2 (Engine, Plugins, UI, CLI) & Task 3 (Kakuro CSP, Solver, Visualizer):** Đã hoàn thành 100% mã nguồn và kiểm thử trên nhánh `person-b`.
> - **Task 1 (N-Queens) & Task 2 (AI Search):** Scaffold sẵn sàng cho Người A triển khai trên nhánh `person-a`.

Repository cho đồ án cuối kỳ môn Trí tuệ Nhân tạo gồm 3 bài toán độc lập:
- **Task 1:** N-Queens (Propositional Logic / PySAT Glucose3 & Local Search Min-Conflicts) — **Người A**
- **Task 2:** Tank Battle (Adversarial Search Minimax/Alpha-Beta, PyGame UI & Plugin Arena) — **AI: Người A | Engine & UI: Người B | Contracts: A+B**
- **Task 3:** Kakuro (CSP, Constraint Propagation FC/GAC, Backtracking & Domain Visualization UI) — **Người B**

---

## 1. Tài liệu hướng dẫn cho nhóm (Đọc trước khi code)

Toàn bộ tài liệu nằm gọn trong 2 file dễ đọc tại thư mục [`docs/`](docs/):
1. **[`docs/01_tong_quan_va_phan_cong.md`](docs/01_tong_quan_va_phan_cong.md)**: Bảng chia việc A/B, cách làm song song không chờ nhau, checklist 6 tuần và quy tắc Git (`main`, `person-a`, `person-b`).
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
python -m pip install -e .
```

> **Lưu ý:** Luôn chạy `python -m pip install -e .` để mọi môi trường terminal (PowerShell, bash, pytest) đều nhận diện được các package trong `src/`. File `.env.example` (sao chép thành `.env`) chỉ hỗ trợ thêm cho VS Code IDE / Jupyter extension chứ không thay thế `pip install -e .` khi chạy trực tiếp từ terminal ngoài.

---

## 3. Cây thư mục & Phân quyền sở hữu (`A`, `B`, `A+B`)

```text
AIF/
├── README.md                                  # [A+B]
├── pyproject.toml                             # [A+B]
├── requirements.txt                           # [A+B]
├── requirements-dev.txt                       # [A+B]
├── .gitignore                                 # [A+B]
├── .gitattributes                             # [A+B]
├── .env.example                               # [A+B] Mẫu cấu hình PYTHONPATH=src cho VS Code
├── demo.txt                                   # [A+B] Placeholder URL video demo
├── docs/
│   ├── 01_tong_quan_va_phan_cong.md           # [A+B]
│   └── 02_huong_dan_code_3_bai.md             # [A+B]
├── src/
│   ├── task1_nqueens/                         # [Người A]
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── board.py
│   │   ├── encoding/
│   │   │   ├── __init__.py
│   │   │   ├── variable_mapper.py
│   │   │   ├── attack_lines.py
│   │   │   └── cnf_builder.py
│   │   ├── solvers/
│   │   │   ├── __init__.py
│   │   │   ├── sat_solver.py
│   │   │   ├── conflict_tracker.py
│   │   │   ├── selection_strategies.py
│   │   │   └── min_conflicts.py
│   │   └── benchmark/
│   │       ├── __init__.py
│   │       └── runner.py
│   ├── task2_tank_battle/
│   │   ├── __init__.py                        # [B]
│   │   ├── __main__.py                        # [B]
│   │   ├── contracts/                         # [A+B] Hợp đồng giao tiếp chung
│   │   │   ├── __init__.py
│   │   │   ├── types.py
│   │   │   ├── state.py
│   │   │   └── interfaces.py
│   │   ├── ai/                                # [Người A]
│   │   │   ├── __init__.py
│   │   │   ├── game_tree.py
│   │   │   ├── evaluator.py
│   │   │   ├── search.py
│   │   │   ├── move_ordering.py
│   │   │   ├── transposition.py
│   │   │   ├── iterative_deepening.py
│   │   │   └── search_agent.py
│   │   ├── benchmark/                         # [Người A]
│   │   │   ├── __init__.py
│   │   │   └── runner.py
│   │   ├── engine/                            # [Người B]
│   │   │   ├── __init__.py
│   │   │   ├── map_loader.py
│   │   │   ├── movement.py
│   │   │   ├── bullet_physics.py
│   │   │   └── rules.py
│   │   ├── plugins/                           # [Người B]
│   │   │   ├── __init__.py
│   │   │   ├── loader.py
│   │   │   ├── guard.py
│   │   │   ├── registry.py
│   │   │   └── builtin/
│   │   │       ├── __init__.py
│   │   │       └── random_agent.py
│   │   ├── ui/                                # [Người B]
│   │   │   ├── __init__.py
│   │   │   ├── app.py
│   │   │   └── renderer.py
│   │   └── maps/                              # [B: map thường | A: maps/scenarios/]
│   └── task3_kakuro/                          # [Người B]
│       ├── __init__.py
│       ├── __main__.py
│       ├── events.py
│       ├── verify.py
│       ├── model/
│       │   ├── __init__.py
│       │   ├── cell.py
│       │   ├── run.py
│       │   └── puzzle.py
│       ├── csp/
│       │   ├── __init__.py
│       │   ├── combinations.py
│       │   ├── constraint.py
│       │   ├── domains.py
│       │   └── csp.py
│       ├── propagation/
│       │   ├── __init__.py
│       │   ├── forward_checking.py
│       │   └── gac.py
│       ├── search/
│       │   ├── __init__.py
│       │   ├── heuristics.py
│       │   └── backtracking.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   └── trace_player.py
│       └── data/puzzles/
├── tests/                                     # [A+B theo từng thư mục con]
├── experiments/                               # [A: task1, task2 | B: task3]
└── report/                                    # [A+B]
```

---

## 4. Hướng dẫn chạy thử nghiệm các tính năng đã hoàn thành

### Task 3: Trực quan hóa & Giải Kakuro (Người B)
```bash
# Giao diện PyGame trực quan hóa miền giá trị và quá trình giải
python -m task3_kakuro ui --puzzle src/task3_kakuro/data/puzzles/large_9x9.json

# Giải và in kết quả kiểm chứng ra console
python -m task3_kakuro solve --puzzle src/task3_kakuro/data/puzzles/large_9x9.json --preset mac-mrvdeg-lcv
```

### Task 2: Đấu trường Bắn xe tăng (Người B Engine/UI & Plugin Arena)
```bash
# Giao diện PyGame điều khiển và đấu xe tăng
python -m task2_tank_battle gui

# Đấu đối kháng headless giữa các bot
python -m task2_tank_battle match --p0 tactical --p1 random --map src/task2_tank_battle/maps/small_7x7.map --headless --games 5
```

### Task 1: N-Queens (Dành cho Người A triển khai trên person-a)
```bash
python -m task1_nqueens solve --method sat --n 8 --show
python -m task1_nqueens solve --method mc-max --n 100 --seed 0
```
