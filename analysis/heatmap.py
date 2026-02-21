"""
Dataset coverage heatmap – ktoré kocky majú dáta pre ktoré roky.
Sekundárna vrstva: dostupnosť hodnôt (% non-NaN) ako intenzita farby.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from loader import load_all

THEME_GROUPS = {
    "Mzdy":          ["np3101rr", "np3102rr", "np3106rr", "od0008ms", "kz1001rs", "kz1008rs"],
    "Demografia":    ["as1001rs", "nu1024rs", "om3707rr"],
    "Vzdelanie":     ["kz1030rs", "sv3701rr"],
    "Ekonomika":     ["kz1018rs", "og1007rs", "og2019qs", "og2021qs", "og3803rr"],
    "Digitalizacia": ["as1012rs", "is1001rs"],
    "Inovacie & VaV":["vt0003rs","vt1002rs","vt1003rs","vt1008rs","vt1009rs","vt1011rs"],
    "Kvalita zivota":["kz1028rs", "kz1024rs", "kz1029rs"],
}


def build_coverage_matrix(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
        has_data  – bool matrix  [cube × rok]
        fill_rate – float matrix [cube × rok]  (% non-NaN values pre daný rok)
    """
    all_years = set()
    rok_dims: dict[str, str] = {}

    for cube, df in data.items():
        rok_dim = next((c for c in df.columns if "rok" in c or "year" in c), None)
        if rok_dim:
            rok_dims[cube] = rok_dim
            all_years.update(df[rok_dim].unique())

    years = sorted(all_years)
    ordered_cubes = [c for g in THEME_GROUPS.values() for c in g if c in data]

    has_data  = pd.DataFrame(False, index=ordered_cubes, columns=years)
    fill_rate = pd.DataFrame(0.0,   index=ordered_cubes, columns=years)

    for cube in ordered_cubes:
        df = data[cube]
        rok = rok_dims.get(cube)
        if not rok:
            continue
        for yr, grp in df.groupby(rok):
            has_data.at[cube, yr] = True
            non_nan = grp["value"].notna().mean()
            fill_rate.at[cube, yr] = non_nan

    return has_data, fill_rate


def cube_label(cube_code: str, data: dict) -> str:
    df = data.get(cube_code)
    if df is None or "cube_name" not in df.columns:
        return cube_code
    name = df["cube_name"].iloc[0]
    # Skráť dlhé názvy
    return f"{cube_code}  {name[:42]}{'…' if len(name)>42 else ''}"


def plot_heatmap(output: Path | None = None):
    data = load_all()
    has_data, fill_rate = build_coverage_matrix(data)

    cubes = list(has_data.index)
    years = list(has_data.columns)

    matrix = fill_rate.values.copy()
    matrix[~has_data.values] = np.nan

    # Skupinové delimitery (hrubé čiary)
    group_boundaries = []
    pos = 0
    for group_cubes in THEME_GROUPS.values():
        pos += sum(1 for c in group_cubes if c in data)
        group_boundaries.append(pos)

    fig, ax = plt.subplots(figsize=(max(20, len(years) * 0.55), max(10, len(cubes) * 0.42)))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "gh", ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    )
    cmap.set_bad(color="#161b22")

    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1,
                   interpolation="nearest")

    # Os X – roky
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, rotation=45, ha="right", fontsize=8, color="#8b949e")

    # Os Y – cube labely
    ax.set_yticks(range(len(cubes)))
    ax.set_yticklabels([cube_label(c, data) for c in cubes],
                       fontsize=7.5, color="#e6edf3", family="monospace")

    # Skupinové oddeľovacie čiary
    for b in group_boundaries[:-1]:
        ax.axhline(b - 0.5, color="#30363d", linewidth=2)

    # Skupinové labely (napravo)
    pos = 0
    for grp_name, grp_cubes in THEME_GROUPS.items():
        n = sum(1 for c in grp_cubes if c in data)
        if n:
            mid = pos + n / 2 - 0.5
            ax.text(len(years) + 0.3, mid, grp_name,
                    va="center", fontsize=8, color="#8b949e",
                    transform=ax.get_yaxis_transform())
        pos += n

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.015, pad=0.01)
    cbar.set_label("Dostupnosť hodnôt (% non-NaN)", color="#8b949e", fontsize=8)
    cbar.ax.yaxis.set_tick_params(color="#8b949e")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#8b949e", fontsize=7)

    ax.set_title("Pokrytie datasetov ŠÚ SR – dostupnosť dát podľa roku",
                 color="#e6edf3", fontsize=13, pad=14, fontweight="bold")

    ax.spines[:].set_visible(False)
    ax.tick_params(colors="#8b949e", length=0)

    plt.tight_layout()

    if output:
        plt.savefig(output, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"✓ Heatmapa uložená: {output}")
    else:
        plt.show()


if __name__ == "__main__":
    out = Path(__file__).parent.parent / "analysis" / "coverage_heatmap.png"
    plot_heatmap(output=out)
