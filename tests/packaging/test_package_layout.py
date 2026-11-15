"""Tests for repository structure and Task 3 notebook output retention (Owner: B)."""

import json
import unittest
from pathlib import Path


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

    def test_notebooks_maintain_outputs_for_all_code_cells(self) -> None:
        root = Path(__file__).resolve().parents[2]
        notebook_names = [
            "task1_nqueens.ipynb",
            "task2_search.ipynb",
            "task3_kakuro.ipynb",
        ]
        for nb_name in notebook_names:
            nb_path = root / "experiments" / nb_name
            self.assertTrue(nb_path.is_file(), f"experiments/{nb_name} must exist")

            nb = json.loads(nb_path.read_text(encoding="utf-8"))
            code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
            self.assertGreaterEqual(len(code_cells), 1)
            for idx, cell in enumerate(code_cells, start=1):
                source_text = "".join(cell.get("source", [])).strip()
                if not source_text:
                    continue
                self.assertIsNotNone(
                    cell.get("execution_count"),
                    f"[{nb_name}] Code cell #{idx} has not been executed",
                )
                self.assertGreater(
                    len(cell.get("outputs", [])),
                    0,
                    f"[{nb_name}] Code cell #{idx} is missing saved outputs",
                )


if __name__ == "__main__":
    unittest.main()
