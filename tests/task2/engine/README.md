# Tests – Task 2: Game Engine (`tests/task2/engine/`)

- **Owner:** `Người B`
- **Trạng thái:** Đã hoàn thành 100% trong `test_engine.py`.
- **Nội dung kiểm thử:**
  - `MapLoader.load`: đọc đúng vị trí và máu khởi tạo (`TANK_HP=6`, `BASE_HP=9`, `WALL_HP=3`), phát hiện lỗi cú pháp bản đồ.
  - `MovementResolver.resolve`: di chuyển 1 ô, xoay hướng khi bị cản, 2 xe cùng nhảy vào 1 ô hoặc đổi chỗ.
  - `BulletPhysics`: đạn bay 3 ô/chu kỳ từng ô một, kiểm tra va chạm sau mỗi ô, trừ 1 HP và dừng ngay lập tức khi trúng Wall/Tank/Base.
  - `GameRules`: thỏa mãn hợp đồng `ForwardModel`, phát hiện kết thúc trận đấu và xác định đúng người thắng / hòa.
