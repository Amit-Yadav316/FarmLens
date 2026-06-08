from __future__ import annotations

import sys


def main(dataset_path: str) -> None:
    """Prepare the KCC dataset for fine-tuning. (Phase 2)"""
    raise NotImplementedError


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "./data/kcc_dataset.csv"
    main(path)
