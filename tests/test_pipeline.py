from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import ensure_demo_assets, run_pipeline


class JudicialSettlementPipelineTest(unittest.TestCase):
    def test_pipeline_runs_end_to_end(self):
        _, sample_pdfs = ensure_demo_assets()
        artifacts = run_pipeline(sample_pdfs[0])

        self.assertGreaterEqual(artifacts.summary["similar_cases_found"], 3)
        self.assertGreater(artifacts.summary["acceptance_probability"], 0)
        self.assertGreater(artifacts.summary["graph_nodes"], 4)
        self.assertTrue(artifacts.graph_html_path.exists())


if __name__ == "__main__":
    unittest.main()

