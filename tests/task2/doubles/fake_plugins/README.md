# Tests – Task 2: Fake Plugins (`tests/task2/doubles/fake_plugins/`)

- **Owner:** `Người B`
- **Trạng thái:** Đã tạo đầy đủ các plugin mẫu để test `PluginLoader` và `GuardedAgent`:
  - `good_agent.py`: plugin hợp lệ tuân thủ `create_agent() -> TankAgent`.
  - `bad_no_factory.py`: plugin thiếu hàm `create_agent()`.
  - `wrong_return_type.py`: plugin có factory trả về sai kiểu đối tượng.
  - `slow_agent.py`: plugin chạy quá thời gian `time_budget_s` (kiểm tra timeout).
  - `crashing_agent.py`: plugin ném ngoại lệ (kiểm tra khả năng cô lập lỗi).
