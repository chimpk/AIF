# Tests – Task 3: Kakuro CSP (`tests/task3/`)

- **Owner:** `Người B`
- **Trạng thái:** Đã hoàn thành 100% trong `test_kakuro.py`.
- **Nội dung kiểm thử:**
  - `KakuroPuzzle.from_json`: kiểm tra trên `small_5x5.json` (12 ô trắng, 8 run) và `large_9x9.json` (48 ô trắng, 28 run).
  - `SumCombinationTable.combos(total, length)`: kiểm tra bảng tổ hợp chữ số không lặp.
  - `SumAllDifferentConstraint.supported_values` & `DomainStore`: kiểm tra cắt tỉa và hoàn tác `checkpoint`/`restore`.
  - `ForwardChecking` & `GeneralizedArcConsistency`: kiểm tra cắt tỉa miền giá trị và phát hiện wipeout.
  - `BacktrackingSolver`: giải đúng cả 5 preset (`bt`, `fc`, `fc-mrv`, `mac-mrv`, `mac-mrvdeg-lcv`) trên cả 2 bảng câu đố.
  - `SolutionVerifier.verify`: kiểm chứng nghiệm độc lập và từ chối các nghiệm sai luật.
  - `TracePlayer` & `KakuroApp`: kiểm tra tua sự kiện từng bước và giao diện trực quan hóa.
