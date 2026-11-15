# IEEE Final Project Report (`report/`)

- **Trạng thái:** Đã hoàn thiện toàn diện báo cáo chuẩn IEEE conference 2 cột, sẵn sàng nộp bài.
- **File PDF chính thức:** [`report/report.pdf`](report.pdf) (đã xuất sẵn, 3 trang $\le$ tối đa 5 trang theo yêu cầu).
- **Mã nguồn LaTeX Overleaf:**
  - [`report/main.tex`](main.tex): Source LaTeX chuẩn `IEEEtran` 2 cột.
  - [`report/references.bib`](references.bib): Tài liệu trích dẫn chuẩn IEEE.
  - [`report/figures/`](figures/): Toàn bộ biểu đồ độ phân giải cao trích xuất từ dữ liệu benchmark thực tế:
    - `figures/task1/sat_scaling.png` & `min_conflicts_comparison.png`
    - `figures/task2/search_nodes_comparison.png`
    - `figures/task3/kakuro_presets_nodes.png`
- **Tác giả:**
  - Thành viên A (MSSV: 52100001)
  - Thành viên B (MSSV: 52100002)
  - Giảng viên hướng dẫn: ThS. Nguyễn Thanh An (`nguyenthanhan@tdtu.edu.vn`) là tác giả cuối cùng.
- **Tái tạo báo cáo bằng Python:**
  ```bash
  python scripts/generate_report_assets.py
  python scripts/build_report_pdf.py
  ```
