# 01 – TỔNG QUAN DỰ ÁN & PHÂN CÔNG 2 NGƯỜI

> Tài liệu này giúp 2 thành viên nắm rõ **ai làm file nào**, **làm theo thứ tự nào trong 6 tuần**, và **quy trình Git** để không bao giờ đụng code của nhau.

---

## 1. Bảng chia việc nhanh (Ai làm phần nào?)

Dự án có 3 bài toán độc lập (mỗi bài 3 điểm) và 1 bài báo cáo IEEE (1 điểm). Hai người chia nhau như sau:

| Thành viên | Phụ trách chính | Thư mục sở hữu độc quyền (Người kia KHÔNG sửa) |
|---|---|---|
| **Cả hai (A + B)** | **Chốt hợp đồng giao tiếp (Contract)** cho Game Xe Tăng ở đầu Tuần 1 | `src/task2_tank_battle/contracts/`<br>`tests/contracts/` |
| **Người A** | 1. **Task 1 (N-Queens):** Mã hóa CNF + Giải bằng Glucose3 + Giải bằng Min-Conflicts.<br>2. **Task 2 (Phần AI):** Thuật toán Minimax, Alpha-Beta, Heuristic Minimax điều khiển xe tăng + Chạy thống kê 4 cấu hình. | `src/task1_nqueens/`<br>`src/task2_tank_battle/ai/`<br>`src/task2_tank_battle/benchmark/`<br>`tests/task1/`, `tests/task2/ai/`<br>`experiments/task1_nqueens.ipynb`<br>`experiments/task2_search.ipynb` |
| **Người B** | 1. **Task 3 (Kakuro):** Mô hình CSP + Cắt tỉa miền giá trị (FC/GAC) + Backtracking + Giao diện xem từng bước.<br>2. **Task 2 (Phần Game Engine & UI):** Luật di chuyển/bắn đạn, Giao diện PyGame, Cơ chế nạp file AI của nhóm khác. | `src/task3_kakuro/`<br>`src/task2_tank_battle/engine/`<br>`src/task2_tank_battle/plugins/`<br>`src/task2_tank_battle/ui/`<br>`tests/task3/`, `tests/task2/engine/`, `tests/task2/plugins/`<br>`experiments/task3_kakuro.ipynb` |

---

## 2. Làm sao để A và B không phải chờ nhau ở Bài 2 (Tank Battle)?

Bài 2 có **AI (do A viết)** và **Luật Game/Giao diện (do B viết)**. Nếu làm kiểu thông thường, A phải đợi B viết xong Luật Game mới có cái để chạy thử AI, và B phải đợi A viết xong AI mới có cái cho xe chạy trên màn hình.

Để **không ai phải chờ ai**, nhóm làm theo 3 bước:
1. **Đầu Tuần 1:** Hai người cùng viết 3 file ngắn trong `src/task2_tank_battle/contracts/` (chỉ định nghĩa tên nút bấm `MOVE_UP`, `FIRE`..., cấu trúc dữ liệu `GameState`, và khung hàm `step`, `choose_action`). Xong bước này thì khóa lại.
2. **Tuần 2–3 (Làm độc lập):**
   - **Người A** tự viết một luật giả lập siêu ngắn (`StubForwardModel` trong thư mục test) để test thuật toán Minimax / Alpha-Beta ngay lập tức.
   - **Người B** tự viết một con bot đi ngẫu nhiên (`RandomAgent`) để test Luật Game và Giao diện PyGame ngay lập tức.
3. **Tuần 4 (Ghép nối):** Khi cả hai đã chạy ngon lành, chỉ cần cắm `SearchAgent` của A vào `GameRules` của B là chạy khớp 100% vì cả hai đều dùng chung `contracts/`.

---

## 3. Lộ trình 6 tuần (Checklist công việc)

### Tuần 1: Chốt Contract & Khởi động
- [ ] **A + B:** Cùng viết xong `src/task2_tank_battle/contracts/` (`types.py`, `state.py`, `interfaces.py`) và commit lên nhánh `main`.
- [ ] **A + B:** Từ `main`, A tạo nhánh `dev/person-a`, B tạo nhánh `dev/person-b`.
- [ ] **A:** Viết `board.py` và `variable_mapper.py` của Task 1 (N-Queens).
- [ ] **B:** Viết `cell.py`, `run.py`, `puzzle.py` của Task 3 (Kakuro) để đọc 2 file JSON đề bài (`small_5x5.json` và `large_9x9.json`).

### Tuần 2: Xây phần lõi (Core 1)
- [ ] **A (Task 1):** Hoàn thành bộ sinh mệnh đề CNF (`attack_lines.py`, `cnf_builder.py`) và giải bằng `Glucose3` (`sat_solver.py`).
- [ ] **A (Task 2):** Viết luật giả lập `stub_forward_model.py`, hàm chấm điểm trạng thái (`evaluator.py`) và khung chuyển lượt (`game_tree.py`).
- [ ] **B (Task 3):** Hoàn thành bảng tổ hợp tổng (`combinations.py`), ràng buộc Kakuro (`constraint.py`, `domains.py`, `csp.py`) và lan truyền `ForwardChecking`.
- [ ] **B (Task 2):** Viết bộ đọc bản đồ (`map_loader.py`) và xử lý di chuyển xe tăng (`movement.py`).

### Tuần 3: Hoàn thiện thuật toán (Core 2)
- [ ] **A (Task 1):** Hoàn thành `Min-Conflicts` chuẩn + Heuristic chọn biến nhiều xung đột nhất (`conflict_tracker.py`, `selection_strategies.py`, `min_conflicts.py`). **Xong code Task 1.**
- [ ] **A (Task 2):** Hoàn thành `MinimaxSearch` và `AlphaBetaSearch` (`search.py`).
- [ ] **B (Task 2 – Ưu tiên số 1):** Hoàn thành vật lý đạn bay 3 ô/lượt (`bullet_physics.py`) và luật tổng hợp (`rules.py`), merge vào `main` cuối tuần 3.
- [ ] **B (Task 3):** Hoàn thành lan truyền `GAC` (`gac.py`), các heuristic `MRV`/`LCV` (`heuristics.py`), bộ giải `BacktrackingSolver` (`backtracking.py`) và bộ kiểm tra nghiệm (`verify.py`). **Giải ra nghiệm bảng 9×9.**

### Tuần 4: Ghép nối & Giao diện (UI)
- [ ] **A (Task 2):** Tối ưu tìm kiếm thời gian thực (`move_ordering.py`, `transposition.py`, `iterative_deepening.py`), đóng gói `SearchAgent` (`search_agent.py`) và ghép thử với `GameRules` thật của B.
- [ ] **A (Task 1):** Chạy xong toàn bộ thực nghiệm trên notebook `experiments/task1_nqueens.ipynb` (giữ nguyên output).
- [ ] **B (Task 2):** Hoàn thành cơ chế nạp plugin nhóm khác (`loader.py`, `guard.py`, `registry.py`) và giao diện `PyGame` (`ui/`).
- [ ] **B (Task 3):** Hoàn thành giao diện `PyGame` hiển thị miền giá trị `{1..9}`, quá trình cắt tỉa và quay lui (`events.py`, `ui/`).

### Tuần 5: Chạy thực nghiệm & Viết báo cáo IEEE
- [ ] **A:** Chạy thực nghiệm so sánh 4 cấu hình tìm kiếm trên `experiments/task2_search.ipynb`; viết phần Task 1 và Task 2 (AI) trong báo cáo LaTeX (`report/`).
- [ ] **B:** Chạy thực nghiệm Kakuro trên `experiments/task3_kakuro.ipynb`; viết phần Task 3, phần giao diện/plugin Task 2, bảng phân công đóng góp (`Contributions`) và tự chấm điểm (`Self-evaluation`).

### Tuần 6: Quay video Demo, Ôn vấn đáp & Nộp bài
- [ ] **A + B:** Quay video demo 3 bài, dán link vào `demo.txt`, xuất `report/report.pdf` (tối đa 5 trang).
- [ ] **A + B:** Dò chéo code của nhau để cả 2 đều hiểu và trả lời được khi giảng viên vấn đáp.
- [ ] **A + B:** Đóng gói thư mục `AI_final_<GroupID>_<StudentID>.zip` và **mỗi người tự nộp bài trên hệ thống**.

---

## 4. Quy tắc Git đơn giản cho 2 người

1. **Làm ở nhánh riêng:**
   - Người A luôn làm việc trên nhánh `dev/person-a`.
   - Người B luôn làm việc trên nhánh `dev/person-b`.
2. **Không sửa file của người kia:** Trước khi `git commit`, chạy `git status` kiểm tra xem có vô tình sửa nhầm file của bạn cùng nhóm không.
3. **Đồng bộ cuối mỗi tuần:**
   - Cuối tuần, người A và người B lần lượt tạo Pull Request (hoặc merge khi test đã xanh) vào `main`.
   - Sau khi `main` có code mới, cả hai chạy `git merge main` vào nhánh riêng của mình để lấy code mới nhất của nhau.

---

## 5. Nhắc nhở quan trọng từ đề bài (Tránh bị 0 điểm)

- **Tuyệt đối không dùng AI sinh code nộp bài:** Mọi hàm và comment trong thư mục `src/` và `tests/` phải do hai bạn tự tay gõ và hiểu rõ từng dòng.
- **Giữ nguyên kết quả chạy trong file `.ipynb`:** Khi nộp bài, các ô code trong `experiments/*.ipynb` phải còn nguyên bảng số liệu và biểu đồ bên dưới.
- **Tạo cả 2 file `requirements.txt` và `requirement.txt`** khi nén nộp (đề bài ghi thiếu chữ `s` ở trang cuối nên để cả 2 file cho an toàn tuyệt đối).
