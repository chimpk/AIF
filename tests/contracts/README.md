# Tests – Shared Contracts (`tests/contracts/`)

- **Owner:** `A+B` (chốt ở đầu Tuần 1 trước khi tách code).
- `test_contracts.py` kiểm tra các hằng số HP/damage/speed, `Direction`, 6 giá trị `Action`, `GameOutcome`, và tính immutable/hashable của toàn bộ state.
- Các test engine và integration áp dụng cùng contract cho `StubForwardModel` và `GameRules`.
