"""Tests for repository structure and Task 3 notebook output retention (Owner: B)."""

import json
from pathlib import Path
import unittest


class TestPackagingAndNotebookOutputs(unittest.TestCase):
    """Verify required submission files and that Task 3 notebook keeps cell outputs."""

    def test_required_project_files_exist(self) -> None:
        root = Path(__file__).resolve().parents[2]
        self.assertTrue((root / "README.md").is_file())
        self.assertTrue((root / "requirements.txt").is_file())
        self.assertTrue((root / "demo.txt").is_file())
        self.assertTrue(
            (
                root
                / "experiments"
                / "results"
                / "task3"
                / "task3_kakuro_benchmark.csv"
            ).is_file()
        )

    def test_task3_notebook_maintains_outputs_for_all_code_cells(self) -> None:
        root = Path(__file__).resolve().parents[2]
        nb_path = root / "experiments" / "task3_kakuro.ipynb"
        self.assertTrue(nb_path.is_file(), "experiments/task3_kakuro.ipynb must exist")

        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
        self.assertGreaterEqual(len(code_cells), 3)
        for idx, cell in enumerate(code_cells, start=1):
            source_text = "".join(cell.get("source", [])).strip()
            if not source_text:
                continue
            self.assertIsNotNone(
                cell.get("execution_count"),
                f"Code cell #{idx} has not been executed",
            )
            self.assertGreater(
                len(cell.get("outputs", [])),
                0,
                f"Code cell #{idx} is missing saved outputs",
            )


if __name__ == "__main__":
    unittest.main()
