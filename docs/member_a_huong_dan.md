# Tài liệu phần Người A (Task 1 + AI của Task 2)

## 1. Phạm vi
| Phần | Thư mục |
|---|---|
| Task 1 – N-Queens | `src/task1_nqueens/`, `tests/task1/`, `experiments/task1_nqueens.ipynb` |
| Task 2 – AI tìm kiếm | `src/task2_tank_battle/ai/`, `src/task2_tank_battle/benchmark/`, `tests/task2/ai/`, `tests/task2/doubles/stub_forward_model.py`, `experiments/task2_search.ipynb` |
| Kết quả thực nghiệm | `experiments/results/task1_*.csv`, `task2_*.csv`, `task2_benchmark_meta.json` |

Không sửa `contracts/`, `engine/`, `plugins/`, `ui/` và test của B. Chỉ thêm các khoá tuỳ chọn
(`positions_per_scenario`, `match_depth_ply`, `match_max_cycles`) vào `experiments/configs/task2.json`.

## 2. Thiết kế tóm tắt
**Task 1** – `VariableMapper` (`var = r*N+c+1`) → `AttackLineGenerator` (hàng, cột, 2 loại đường chéo, ≥2 ô) →
`NQueensCNFBuilder` (at-least-one mỗi hàng + at-most-one từng cặp trên mỗi đường; N=4 → 80, N=8 → 736 mệnh đề) →
`SatNQueensSolver` (Glucose3, giải mã rồi kiểm tra lại bằng `SolutionValidator`).
`ConflictTracker` (3 mảng đếm, O(1)) → `MinConflictsSolver` với 2 chiến lược chọn cột:
`RandomConflictedSelection` (chuẩn) và `MaxConflictSelection` (cột nhiều xung đột nhất + tabu 3 bước).

**Task 2** – `TurnSequencedGame` (tách chu kỳ đồng thời thành 2 ply MAX/MIN) → `MinimaxSearch`, `AlphaBetaSearch`
(tuỳ chọn `MoveOrderer`, `TranspositionTable`) → `TerminalOnlyEvaluator`/`HeuristicEvaluator` →
`IterativeDeepeningDriver` (độ sâu 2,4,6…, giữ nước đi của độ sâu hoàn tất cuối) → `SearchAgent` (không ném exception, luôn trả hành động hợp lệ).
Tên agent: `A-MINIMAX`, `A-ALPHABETA`, `A-H_MINIMAX`, `A-H_ALPHABETA`; `create_agent()` trả về `A-H_ALPHABETA`.

## 3. Giả định cần Người B xác nhận
1. Toạ độ là `(hàng, cột)`, hàng 0 ở trên, `UP` làm giảm hàng (`ai/geometry.py::DIRECTION_DELTA`).
2. Đạn được tính như trong `StubForwardModel` (mỗi chu kỳ bay 3 ô, kiểm tra va chạm từng ô). AI chỉ dùng `ForwardModel`, nên sai khác ở engine không làm hỏng code AI, chỉ đổi số liệu benchmark.
3. `engine.MapLoader().load(path)` và `engine.GameRules` triển khai đúng `ForwardModel`.

## 4. Chạy trên Windows (PowerShell, tại thư mục gốc repo)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
$env:PYTHONPATH = "src"

# Task 1
python -m task1_nqueens solve --method sat --n 8 --show
python -m task1_nqueens solve --method mc-max --n 100 --seed 0
python -m task1_nqueens benchmark

# Task 2 AI: benchmark trên stub (khi engine của B xong, đổi --model stub thành --model engine)
python -m task2_tank_battle.benchmark --model stub

# Test
python -m pytest tests/task1 tests/task2/ai -q
python -m pytest -q

# Notebook
jupyter nbconvert --to notebook --execute --inplace experiments/task1_nqueens.ipynb
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 experiments/task2_search.ipynb
```
