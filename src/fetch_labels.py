import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
OUT_PATH = ROOT / "data" / "datacube_labels.json"


def get_cube_labels(cube_code: str, n_dims: int, lang: str = "sk") -> dict | None:
    all_path = "/".join(["all"] * n_dims)
    url = f"https://data.statistics.sk/api/v2/dataset/{cube_code}/{all_path}?lang={lang}&type=json"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  ✗ {cube_code}: {e}")
        return None

    labels = {}
    for dim_id, dim_data in data.get("dimension", {}).items():
        if dim_id.endswith("_data"):
            continue
        labels[dim_id] = {
            "label": dim_data.get("note", dim_id),
            "elements": dim_data.get("category", {}).get("label", {}),
        }
    return labels


def load_csv_meta(filepath: Path) -> tuple[str, int]:
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    cube_code = lines[1].split(";")[0].strip()
    dimensions = [d.strip() for d in lines[5].strip().split(";")]
    return cube_code, len(dimensions)


def fetch_all(raw_dir: Path, delay: float = 0.3) -> dict:
    all_labels: dict = {}
    csv_files = sorted(raw_dir.glob("*.csv"))
    print(f"Fetching labels for {len(csv_files)} cubes...")

    for fpath in csv_files:
        cube_code, n_dims = load_csv_meta(fpath)
        labels = get_cube_labels(cube_code, n_dims)
        if labels is not None:
            all_labels[cube_code] = labels
            print(f"  ✓ {cube_code}")
        time.sleep(delay)

    return all_labels


if __name__ == "__main__":
    raw_dir = ROOT / "data" / "raw"
    labels = fetch_all(raw_dir)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Labels saved to {OUT_PATH} ({len(labels)} cubes)")
