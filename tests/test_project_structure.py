from pathlib import Path


def test_project_structure_exists():
    project_root = Path(__file__).resolve().parents[1]

    expected_paths = [
        ".github/workflows",
        "app/api",
        "app/ui",
        "data",
        "docs",
        "notebooks",
        "src/datasets",
        "src/evaluation",
        "src/features",
        "src/models",
        "src/serving",
        "src/trainers",
        "src/transforms",
        "src/utils",
        "tests",
    ]

    missing_paths = [
        path for path in expected_paths if not (project_root / path).exists()
    ]

    assert missing_paths == []
