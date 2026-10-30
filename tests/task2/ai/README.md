# Tests – Task 2: Adversarial Search AI (`tests/task2/ai/`)

- **Owner:** `Người A`
- **TODO cần tự viết:**
  - `test_game_tree.py`: Kiểm tra `TurnSequencedGame` chuyển 1 chu kỳ đồng thời thành 2 tầng MAX/MIN.
  - `test_evaluator.py`: Kiểm tra tính đối xứng tổng bằng 0 (`evaluate(s, 0) == -evaluate(s, 1)`) của `TerminalOnlyEvaluator` và `HeuristicEvaluator`.
  - `test_minimax.py` & `test_alphabeta.py`: Kiểm tra `MinimaxSearch` và `AlphaBetaSearch` trả về cùng giá trị gốc trên cùng thế cờ, và Alpha-Beta duyệt ít trạng thái hơn.
  - `test_iterative_deepening.py` & `test_transposition.py`: Kiểm tra giới hạn thời gian và bảng băm trạng thái.
  - `test_search_agent.py`: Kiểm tra `SearchAgent` và factory `create_agent()`.
