# 02 – HƯỚNG DẪN LÀM TỪNG BÀI & GIAO DIỆN CODE

> Tài liệu này giải thích **cách giải từng bài bằng lời dễ hiểu** và **danh sách các file/hàm cần viết** để mỗi người nhìn vào là tự code được ngay.

---

## PHẦN 1: HƯỚNG DẪN CHO NGƯỜI A (`Task 1` + `AI của Task 2`)

### 1. Bài 1 – N-Queens (`src/task1_nqueens/`)

#### A. Ý tưởng dễ hiểu
Bàn cờ có $N \times N$ ô. Ta đánh số thứ tự các ô từ `1` đến $N^2$ theo công thức:
$$\text{var}(r, c) = r \times N + c + 1 \quad (0 \le r, c < N)$$
- Nếu biến mang giá trị **Dương** (`+k`): ô đó **có** đặt quân hậu.
- Nếu biến mang giá trị **Âm** (`-k`): ô đó **không** có quân hậu.

**Cách tạo mệnh đề CNF (Yêu cầu 1.1):**
1. **Mỗi hàng phải có ít nhất 1 quân hậu (At-Least-One):**
   Với mỗi hàng $r$, nối tất cả các ô trong hàng bằng phép HOẶC ($\lor$):
   `[var(r, 0), var(r, 1), ..., var(r, N-1)]` (có $N$ mệnh đề như vậy).
2. **Không có 2 quân hậu nào ăn nhau (At-Most-One trên mỗi hàng, cột, đường chéo):**
   Quét mọi đường thẳng theo 4 hướng (ngang, dọc, chéo chính $\searrow$, chéo phụ $\swarrow$). Trên mỗi đường thẳng, với **mọi cặp 2 ô khác nhau** $(u, v)$, không được cùng có hậu $\Rightarrow$ thêm mệnh đề:
   `[-u, -v]` (nghĩa là $\neg u \lor \neg v$).

**Cách giải bằng Glucose3 (Yêu cầu 1.2):**
Đưa danh sách các mệnh đề trên vào `Glucose3` của thư viện `pysat.solvers`. Gọi `solver.solve()`, sau đó lấy nghiệm `solver.get_model()`, lọc ra các số `> 0` rồi đổi ngược về tọa độ `(r, c)`.

**Cách giải bằng Min-Conflicts + Heuristic (Yêu cầu 1.3):**
- Ta biểu diễn bàn cờ bằng 1 mảng `rows_by_col` độ dài $N$: mỗi cột đã có sẵn đúng 1 quân hậu ở hàng `rows_by_col[col]`.
- Để đếm số xung đột cực nhanh $O(1)$, dùng 3 mảng đếm số hậu trên từng hàng (`row_count`), từng đường chéo chính (`diag_count[r - c + N - 1]`), và từng đường chéo phụ (`anti_count[r + c]`).
- **Vòng lặp Min-Conflicts:**
  1. Nếu tổng xung đột bằng 0 $\Rightarrow$ trả về nghiệm.
  2. **Chọn cột đang bị xung đột:**
     - *Cách chuẩn (Standard):* Chọn ngẫu nhiên 1 cột trong các cột có xung đột `> 0`.
     - *Heuristic đề xuất (Max-Conflict / Tabu):* Chọn cột có **số xung đột lớn nhất** (và không nằm trong danh sách vừa mới di chuyển ở vài bước gần nhất) để tháo gỡ "điểm nóng" nhanh nhất.
  3. Di chuyển quân hậu ở cột đó sang hàng nào làm phát sinh **ít xung đột nhất** (nếu có nhiều hàng bằng nhau thì bốc ngẫu nhiên).

#### B. Các file Người A cần viết trong `src/task1_nqueens/`
| File | Class / Hàm cần viết | Công dụng |
|---|---|---|
| `board.py` | `Placement(n, rows_by_col)`<br>`SolutionValidator.is_valid(placement)` | Lưu vị trí $N$ quân hậu và hàm kiểm tra nghiệm có hợp lệ không. |
| `encoding/variable_mapper.py` | `VariableMapper(n)`<br>- `var(row, col) -> int`<br>- `cell(var) -> (row, col)` | Đổi qua lại giữa tọa độ `(row, col)` và số nguyên `1..N^2`. |
| `encoding/attack_lines.py` | `AttackLineGenerator(n).all_lines()` | Tự động tìm tất cả các hàng, cột, đường chéo có từ 2 ô trở lên. |
| `encoding/cnf_builder.py` | `NQueensCNFBuilder(n).build()` | Sinh toàn bộ danh sách mệnh đề CNF (kiểm tra: $N=4$ ra `80` mệnh đề, $N=8$ ra `736` mệnh đề). |
| `solvers/sat_solver.py` | `SatNQueensSolver.solve(n)` | Giải bằng `Glucose3`, trả về nghiệm + số mệnh đề + thời gian chạy. |
| `solvers/conflict_tracker.py` | `ConflictTracker(n, rows_by_col)`<br>- `conflicts_of(col)`<br>- `conflicts_if(col, row)`<br>- `move(col, new_row)` | Đếm và cập nhật xung đột trong thời gian $O(1)$. |
| `solvers/selection_strategies.py` | `RandomConflictedSelection`<br>`MaxConflictSelection` | 2 chiến lược chọn biến để đem đi so sánh thực nghiệm. |
| `solvers/min_conflicts.py` | `MinConflictsSolver(strategy).solve(n)` | Thuật toán tìm kiếm cục bộ Min-Conflicts. |

---

### 2. Bài 2 (Phần AI) – Tìm kiếm đối kháng (`src/task2_tank_battle/ai/`)

#### A. Ý tưởng dễ hiểu
- **Mô hình cây tìm kiếm:** Trong 1 chu kỳ (cycle), xe của mình (`MAX`) chọn 1 trong 6 hành động, xe địch (`MIN`) chọn 1 trong 6 hành động, rồi gọi `model.step(state, {max_id: a_max, min_id: a_min})` để sang trạng thái mới.
- **4 cấu hình cần so sánh (Yêu cầu 2.2):**
  1. `Minimax Search`: Duyệt cây tới độ sâu giới hạn $d$, chỉ chấm điểm thắng/thua (`+10000` / `-10000`, chưa kết thúc thì `0`).
  2. `Alpha-Beta Search`: Giống cấu hình 1 nhưng có cắt tỉa nhánh thừa bằng $(\alpha, \beta)$.
  3. `Heuristic Minimax Search`: Duyệt bằng Minimax, nhưng khi chạm độ sâu giới hạn $d$ thì dùng hàm `HeuristicEvaluator` để ước lượng thế trận.
  4. `Heuristic Minimax + Alpha-Beta`: Kết hợp cả hàm lượng giá `HeuristicEvaluator` và cắt tỉa `Alpha-Beta`.
- **Công thức hàm lượng giá (`HeuristicEvaluator`) gợi ý:**
  $$\text{Score} = w_1(\text{HP}_{\text{xe mình}} - \text{HP}_{\text{xe địch}}) + w_2(\text{HP}_{\text{nhà mình}} - \text{HP}_{\text{nhà địch}}) + w_3(\text{Khoảng cách địch tới nhà mình} - \text{Khoảng cách mình tới nhà địch}) + w_4(\text{Đường ngắm bắn & Né đạn})$$

#### B. Các file Người A cần viết trong `src/task2_tank_battle/ai/`
| File | Class / Hàm cần viết | Công dụng |
|---|---|---|
| `game_tree.py` | `TurnSequencedGame(model, max_player)` | Biến 1 chu kỳ đồng thời thành 2 tầng (ply) trên cây: tầng MAX và tầng MIN. |
| `evaluator.py` | `TerminalOnlyEvaluator`<br>`HeuristicEvaluator` | 2 bộ chấm điểm bàn cờ (chỉ chấm thắng/thua vs. chấm điểm thế trận). |
| `search.py` | `MinimaxSearch`<br>`AlphaBetaSearch` | Cài đặt thuật toán tìm kiếm và đếm số trạng thái đã duyệt (`nodes_expanded`), số lần cắt tỉa (`cutoffs`). |
| `iterative_deepening.py` | `IterativeDeepeningDriver` | Tìm kiếm lặp sâu dần ($d = 2, 4, 6\dots$) và ngắt đúng giờ để giao diện không bị giật. |
| `search_agent.py` | `SearchAgent(TankAgent)`<br>`create_agent() -> TankAgent` | Đóng gói AI thành agent chuẩn để lắp vào giao diện PyGame của B. |

---

## PHẦN 2: HƯỚNG DẪN CHO NGƯỜI B (`Task 3` + `Engine/UI của Task 2`)

### 1. Bài 2 (Phần Engine, Plugin & UI) – Tank Battle (`src/task2_tank_battle/`)

#### A. Luật vật lý cần cài chính xác (Trang 2 đề bài)
Trong hàm `GameRules.step(state, actions)`, xử lý lần lượt 4 bước nhỏ:
1. **Di chuyển xe (`movement.py`):**
   - Nếu hành động là `MOVE_UP/DOWN/LEFT/RIGHT`: Đầu tiên xoay hướng nhìn (`facing`) của xe theo hướng đó. Nếu ô trước mặt trống (không ra ngoài biên, không có tường, căn cứ, hay xe kia) thì tiến lên 1 ô.
   - Nếu 2 xe cùng bước vào 1 ô trống hoặc đổi chỗ cho nhau $\Rightarrow$ cả hai đứng yên.
2. **Sinh đạn mới (`bullet_physics.py`):**
   - Nếu hành động là `FIRE` (và xe đó chưa có đạn đang bay trên sân): Tạo 1 viên đạn tại vị trí xe, hướng bay trùng với `facing` của xe.
3. **Cho đạn bay 3 ô từng bước một (`bullet_physics.py` – Rất quan trọng):**
   - Chạy vòng lặp `substep` từ `1` đến `3`:
     - Nhích mỗi viên đạn đi **1 ô** theo hướng bay của nó.
     - Kiểm tra ngay lập tức:
       - Nếu ra ngoài bản đồ $\Rightarrow$ xóa viên đạn.
       - Nếu chạm **Tường (`Wall`)**, **Xe (`Tank`)**, hoặc **Căn cứ (`Base`)** $\Rightarrow$ trừ `1 HP` của vật thể đó, và **xóa viên đạn ngay lập tức** (đạn không được bay tiếp bước thứ 2, 3).
4. **Kiểm tra thắng thua (`rules.py`):**
   - Xóa các bức tường có `HP == 0`.
   - Nếu `Tank` hoặc `Base` của bên nào có `HP == 0` $\Rightarrow$ trận đấu kết thúc, bên còn lại thắng.

#### B. Các file Người B cần viết trong `src/task2_tank_battle/`
| File | Class / Hàm cần viết | Công dụng |
|---|---|---|
| `engine/map_loader.py` | `MapLoader.load(path) -> GameState` | Đọc file `.map` thành `GameState` ban đầu (`Tank HP=6`, `Base HP=9`, `Wall HP=3`). |
| `engine/movement.py` | `MovementResolver.resolve(...)` | Xử lý xoay hướng và di chuyển 1 ô/lượt. |
| `engine/bullet_physics.py` | `BulletPhysics.spawn(...)`<br>`BulletPhysics.advance(...)` | Xử lý bắn đạn và cho đạn bay từng ô một (tối đa 3 ô/lượt). |
| `engine/rules.py` | `GameRules(ForwardModel)` | Ghép di chuyển + đạn + kiểm tra thắng thua (cài đặt đúng `ForwardModel` trong `contracts/`). |
| `plugins/loader.py` & `guard.py` | `PluginLoader.load_file(path)`<br>`GuardedAgent` | Nạp file `.py` của nhóm khác thông qua hàm `create_agent()`; bọc timeout để nếu code nhóm bạn bị treo thì tự trả về `STAY`. |
| `ui/app.py` & `renderer.py` | `TankBattleApp` | Giao diện PyGame: chọn AI cho 2 xe, vẽ bản đồ, thanh máu, đường đạn và bảng thông số AI. |

---

### 2. Bài 3 – Trò chơi Kakuro (`src/task3_kakuro/`)

#### A. Ý tưởng dễ hiểu
- **Biến (Variables):** Mỗi ô trắng `.` trên bảng là một biến, ký hiệu bằng tọa độ `(row, col)`.
  - Bảng nhỏ `small_5x5.json` có **12 ô trắng**.
  - Bảng lớn `large_9x9.json` có **48 ô trắng**.
- **Miền giá trị (Domains):** Ban đầu mỗi ô trắng chỉ có thể nhận các số từ `{1, 2, ..., 9}`.
  - *Thu hẹp ngay từ đầu:* Nếu một dãy ngang gồm $k=2$ ô có tổng gợi ý là `3`, thì chỉ có bộ `{1, 2}` cộng lại bằng 3 $\Rightarrow$ miền giá trị của 2 ô đó giảm ngay xuống `{1, 2}`.
- **Ràng buộc (Constraints):** Mỗi dãy ô trắng liên tiếp theo hàng ngang hoặc cột dọc (`Run`) phải thỏa mãn đồng thời:
  1. Các chữ số trong dãy **khác nhau đôi một** (`AllDifferent`).
  2. Tổng các chữ số trong dãy bằng đúng số gợi ý (`clue`).
- **Giải bằng Constraint Propagation + Backtracking + Heuristic:**
  1. **Chọn biến chưa điền (`MRV` + `Degree`):** Luôn chọn ô trắng nào đang có **ít số khả dĩ nhất** trong miền giá trị (nếu bằng nhau thì chọn ô giao với nhiều ô chưa điền hơn).
  2. **Sắp xếp giá trị thử (`LCV`):** Thử con số nào làm **ít ảnh hưởng nhất** tới miền giá trị của các ô cùng hàng/cùng cột.
  3. **Lan truyền ràng buộc (`Forward Checking` / `GAC`):** Mỗi khi điền thử một số vào ô, lập tức gạch bỏ số đó khỏi các ô cùng dãy và loại các số không còn tổ hợp nào cộng đủ tổng `clue`. Nếu có ô nào bị rỗng miền giá trị (`Wipeout`) $\Rightarrow$ quay lui (`Backtrack`) ngay lập tức!
- **Giao diện trực quan hóa (Yêu cầu 3.3):**
  - Mỗi khi Solver thu hẹp miền giá trị, gán thử hoặc quay lui, nó đẩy một bản ghi `SolverEvent` vào danh sách `TraceRecorder`.
  - Giao diện PyGame chỉ việc đọc danh sách sự kiện này để vẽ: trong mỗi ô trắng vẽ 9 số nhỏ `1..9` (như ghi nháp bằng bút chì), số nào bị cắt tỉa thì tô đỏ/mờ đi, ô đang gán thử tô xanh, ô quay lui tô vàng; có nút `Play / Pause / Step Next / Step Back`.

#### B. Các file Người B cần viết trong `src/task3_kakuro/`
| File | Class / Hàm cần viết | Công dụng |
|---|---|---|
| `model/puzzle.py` | `KakuroPuzzle.from_json(path)` | Đọc file JSON bảng câu đố, tách tự động các dãy ngang (`ACROSS`) và dãy dọc (`DOWN`). |
| `csp/combinations.py` | `SumCombinationTable.combos(total, length)` | Tìm tất cả các bộ $k$ chữ số khác nhau từ `1..9` có tổng bằng `total`. |
| `csp/constraint.py` | `SumAllDifferentConstraint` | Kiểm tra ràng buộc của 1 dãy và tính các chữ số còn hợp lệ (`supported_values`) cho từng ô. |
| `csp/domains.py` | `DomainStore` (`checkpoint`, `restore`) | Lưu miền giá trị hiện tại của mọi ô trắng và khôi phục nhanh khi quay lui. |
| `propagation/forward_checking.py`<br>`propagation/gac.py` | `ForwardChecking`<br>`GeneralizedArcConsistency` | Hai thuật toán lan truyền ràng buộc cắt tỉa miền giá trị. |
| `search/heuristics.py`<br>`search/backtracking.py` | `MRV`, `MRVDegree`, `LeastConstrainingValue`<br>`BacktrackingSolver` | Bộ giải tìm kiếm quay lui kết hợp heuristic và phát sự kiện cho UI. |
| `verify.py` | `SolutionVerifier.verify(puzzle, solution)` | Hàm độc lập kiểm tra lại kết quả điền số đã đúng 100% luật Kakuro chưa. |
| `ui/app.py` & `trace_player.py` | `KakuroApp`, `TracePlayer` | Giao diện PyGame tua từng bước quá trình cắt tỉa miền giá trị và quay lui. |

---

## PHẦN 3: HỢP ĐỒNG CHUNG `contracts/` (Cả A và B cùng chốt đầu Tuần 1)

Chỉ có **3 file ngắn** trong `src/task2_tank_battle/contracts/` mà hai bạn làm chung trước khi chia nhánh:

1. **`contracts/types.py`:**
   - `Direction`: `UP`, `DOWN`, `LEFT`, `RIGHT`.
   - `Action`: `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `FIRE`, `STAY`.
   - Hằng số đề bài & luật chốt: `TANK_HP = 6`, `BASE_HP = 9`, `WALL_HP = 3`, `DAMAGE_PER_HIT = 1`, `BULLET_SPEED = 3`, `MAX_BULLETS_PER_TANK = 1`, `DEFAULT_MAX_CYCLES = 300`.
2. **`contracts/state.py`:**
   - Các `@dataclass(frozen=True, slots=True)`: `TankState`, `BaseState`, `WallState`, `BulletState`, `GameState` (có `max_cycles: int = DEFAULT_MAX_CYCLES`) và `GameOutcome` (`ONGOING`, `WIN_P0`, `WIN_P1`, `DRAW`).
3. **`contracts/interfaces.py`:**
   - Giao diện `ForwardModel`: có hàm `legal_actions(state, player)`, `step(state, actions) -> GameState`, `outcome(state)`, `is_terminal(state)`. (Không dùng `step_with_events`; cả AI và UI chỉ gọi `step` thuần trả về `GameState`).
   - Lớp trừu tượng `TankAgent`: có hàm `reset(player, model)` và `choose_action(state, time_budget_s) -> Action`.
