# Tests – Task 2: Game Engine (`tests/task2/engine/`)

- **Owner:** `Người B`
- **TODO cần tự viết:**
  - `test_map_loader.py`: Kiểm tra `MapLoader.load` đọc đúng vị trí và máu khởi tạo (`TANK_HP=6`, `BASE_HP=9`, `WALL_HP=3`).
  - `test_movement.py`: Kiểm tra `MovementResolver.resolve` (di chuyển 1 ô, xoay hướng khi bị chặn, 2 xe cùng nhảy vào 1 ô hoặc đổi chỗ).
  - `test_bullet_physics.py`: Kiểm tra `BulletPhysics` (đạn bay 3 ô/chu kỳ từng ô một, kiểm tra va chạm sau mỗi ô, trừ 1 HP và dừng ngay lập tức khi trúng Wall/Tank/Base).
  - `test_rules.py`: Kiểm tra `GameRules` thỏa mãn `ForwardModel` và điều kiện kết thúc trận đấu.
