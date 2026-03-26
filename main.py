from __future__ import annotations

from pathlib import Path

from src.pipeline import ensure_demo_assets, run_pipeline


def main() -> None:
    _, sample_pdfs = ensure_demo_assets()
    artifacts = run_pipeline(Path(sample_pdfs[0]))

    print("Judicial Settlement MVP")
    print("-" * 52)
    for key, value in artifacts.summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

