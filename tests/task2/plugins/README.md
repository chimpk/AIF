# Tests – Task 2: Plugin System (`tests/task2/plugins/`)

- **Owner:** `Người B`
- **Trạng thái:** Đã hoàn thành 100% trong `test_plugins.py`.
- **Nội dung kiểm thử:**
  - `PluginLoader.load_file`: nạp agent từ file `.py` bên ngoài và xác thực phương thức `create_agent()`.
  - `GuardedAgent`: cô lập lỗi và timeout bằng luồng riêng, tự động trả về `Action.STAY` khi plugin gặp sự cố.
  - `AgentRegistry`: đăng ký và khởi tạo agent theo tên, hỗ trợ agent có sẵn lẫn agent từ file bên ngoài.
