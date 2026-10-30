# Tests – Task 3: Kakuro CSP (`tests/task3/`)

- **Owner:** `Người B`
- **TODO cần tự viết:**
  - `test_puzzle_model.py`: Kiểm tra `KakuroPuzzle.from_json` trên `small_5x5.json` (12 ô trắng) và `large_9x9.json` (48 ô trắng, 28 run).
  - `test_combinations.py`: Kiểm tra `SumCombinationTable.combos(total, length)`.
  - `test_constraint.py` & `test_domains.py`: Kiểm tra `SumAllDifferentConstraint.supported_values` và `DomainStore` (`checkpoint` / `restore`).
  - `test_propagation.py`: Kiểm tra `ForwardChecking` và `GeneralizedArcConsistency` cắt tỉa miền giá trị và phát hiện wipeout.
  - `test_heuristics.py` & `test_backtracking.py`: Kiểm tra `MRV`, `MRVDegree`, `LeastConstrainingValue` và `BacktrackingSolver` giải đúng cả 2 bảng 5x5 và 9x9.
  - `test_verify.py`: Kiểm tra `SolutionVerifier.verify`.
  - `test_trace_player.py`: Kiểm tra `TraceRecorder` và `TracePlayer` (`step_forward` / `step_backward`).
