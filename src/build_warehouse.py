from pathlib import Path
from loader import load_from_csv

ROOT = Path(__file__).parent.parent
RAW = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "data" / "warehouse"


def build(force: bool = False):
    WAREHOUSE.mkdir(exist_ok=True)
    csv_files = sorted(RAW.glob("*.csv"))
    print(f"Building warehouse from {len(csv_files)} CSV files...\n")

    ok, fail = 0, 0
    for fpath in csv_files:
        out = WAREHOUSE / f"{fpath.stem}.parquet"
        if out.exists() and not force:
            print(f"  – {fpath.stem}.parquet (skip, exists)")
            continue
        try:
            df = load_from_csv(fpath)
            df.to_parquet(out, index=False)
            print(f"  ✓ {fpath.stem}.parquet  ({len(df)} rows, {df.shape[1]} cols)")
            ok += 1
        except Exception as e:
            print(f"  ✗ {fpath.stem}: {e}")
            fail += 1

    total_kb = sum(f.stat().st_size for f in WAREHOUSE.glob("*.parquet")) / 1024
    print(f"\n✓ Done: {ok} built, {fail} failed")
    print(f"✓ Warehouse size: {total_kb:.1f} KB")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="Rebuild even if parquet exists")
    args = p.parse_args()
    build(force=args.force)
