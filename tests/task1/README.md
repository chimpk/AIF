# Tests – Task 1: N-Queens (`tests/task1/`)

- **Owner:** `Người A`
- **TODO cần tự viết:**
  - `test_board.py`: Kiểm tra `Placement` và `SolutionValidator.is_valid` trên các bàn cờ đúng và các bàn cờ có cặp hậu ăn nhau (ngang, dọc, chéo).
  - `test_variable_mapper.py`: Kiểm tra ánh xạ 2 chiều `var(row, col)` <-> `cell(var)` với `1..N*N`.
  - `test_attack_lines.py`: Kiểm tra `AttackLineGenerator.all_lines()` sinh đủ hàng, cột, đường chéo độ dài >= 2.
  - `test_cnf_builder.py`: Kiểm tra `NQueensCNFBuilder(n).build()` sinh đúng số mệnh đề CNF ($N=4 \to 80$, $N=8 \to 736$).
  - `test_sat_solver.py`: Kiểm tra `SatNQueensSolver` với `Glucose3` ($N=2, 3$ vô nghiệm; $N \ge 4$ trả nghiệm hợp lệ).
  - `test_conflict_tracker.py`: Kiểm tra `conflicts_of`, `conflicts_if`, `move` khớp với đếm vét cạn.
  - `test_selection_strategies.py` & `test_min_conflicts.py`: Kiểm tra `RandomConflictedSelection`, `MaxConflictSelection` và `MinConflictsSolver`.
