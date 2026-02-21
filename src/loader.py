import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
LABELS_PATH = ROOT / "data" / "datacube_labels.json"
WAREHOUSE_PATH = ROOT / "data" / "warehouse"
RAW_PATH = ROOT / "data" / "raw"

with open(LABELS_PATH, "r", encoding="utf-8") as f:
    ALL_LABELS = json.load(f)


def load_from_csv(filepath: Path) -> pd.DataFrame:
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cube_code = lines[1].split(";")[0].strip()
    cube_name = lines[1].split(";")[1].strip().strip('"')
    last_updated = lines[2].split(";")[1].strip()
    dimensions = [d.strip() for d in lines[5].strip().split(";")]

    df = pd.read_csv(
        filepath, sep=";", skiprows=8,
        names=dimensions + ["value"],
        dtype={d: str for d in dimensions},
    )
    df.loc[:, "value"] = pd.to_numeric(df["value"], errors="coerce")
    df.loc[:, "cube_code"] = cube_code
    df.loc[:, "cube_name"] = cube_name

    cube_labels = ALL_LABELS.get(cube_code, {})
    for dim in dimensions:
        elem_labels = cube_labels.get(dim, {}).get("elements", {})
        if elem_labels:
            df.loc[:, dim + "_label"] = df[dim].map(elem_labels).fillna(df[dim])

    df.attrs = {
        "cube_code": cube_code,
        "cube_name": cube_name,
        "last_updated": last_updated,
        "dimensions": dimensions,
    }
    return df


def load(cube_code: str) -> pd.DataFrame:
    parquet = WAREHOUSE_PATH / f"{cube_code}.parquet"
    if parquet.exists():
        return pd.read_parquet(parquet)
    csv = RAW_PATH / f"{cube_code}.csv"
    if csv.exists():
        return load_from_csv(csv)
    raise FileNotFoundError(f"Cube '{cube_code}' not found in warehouse or raw.")


def load_all() -> dict[str, pd.DataFrame]:
    return {
        p.stem: pd.read_parquet(p)
        for p in sorted(WAREHOUSE_PATH.glob("*.parquet"))
    }


def get_label(cube_code: str, dim: str, code: str) -> str:
    return (
        ALL_LABELS.get(cube_code, {})
        .get(dim, {})
        .get("elements", {})
        .get(code, code)
    )


def catalog() -> pd.DataFrame:
    rows = []
    for p in sorted(WAREHOUSE_PATH.glob("*.parquet")):
        df = pd.read_parquet(p)
        cube = p.stem
        rok_dim = next((c for c in df.columns if "rok" in c or "year" in c), None)
        years = sorted(df[rok_dim].unique()) if rok_dim else []
        rows.append({
            "cube_code": cube,
            "cube_name": df["cube_name"].iloc[0] if "cube_name" in df.columns else "",
            "rows": len(df),
            "columns": df.shape[1],
            "nan_pct": round(df["value"].isna().mean() * 100, 1),
            "year_min": years[0] if years else None,
            "year_max": years[-1] if years else None,
            "n_years": len(years),
        })
    return pd.DataFrame(rows)
