# Tests – Shared Contracts (`tests/contracts/`)

- **Owner:** `A+B` (chốt ở đầu Tuần 1 trước khi tách code).
- **TODO cần tự viết:**
  - `test_contract_constants.py`: Kiểm tra giá trị `TANK_HP=6`, `BASE_HP=9`, `WALL_HP=3`, `DAMAGE_PER_HIT=1`, `BULLET_SPEED=3`, `Direction` và 6 giá trị `Action`.
  - `test_state_immutability.py`: Kiểm tra `TankState`, `BaseState`, `WallState`, `BulletState`, `GameState` là `frozen` và `hash()` được.
  - `forward_model_contract.py`: Bộ kiểm tra bất biến dùng chung cho cả `StubForwardModel` (A) và `GameRules` (B).
