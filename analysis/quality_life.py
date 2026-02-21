"""
Vrstva 7: Kvalita života
  - Spokojnosť so životom podľa veku a pohlaví (kz1028rs)
  - Medián čistého príjmu podľa vekových skupín (kz1001rs)
  - Schopnosť výjsť s peniazmi podľa typu domácnosti (kz1008rs)
  - Miera ekonomickej aktivity muži vs. ženy 2020-2024 (kz1018rs)
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from loader import load

OUT   = Path(__file__).parent
YEARS = list(range(2020, 2025))

STYLE = {
    "bg": "#0d1117", "panel": "#161b22", "border": "#30363d",
    "text": "#e6edf3", "sub": "#8b949e", "grid": "#21262d",
}
GREEN  = ["#0e4429", "#006d32", "#26a641", "#39d353", "#56d364"]
BLUE   = ["#0d419d", "#1f6feb", "#388bfd", "#58a6ff", "#79c0ff"]
RED    = "#f78166"
ORANGE = "#e3b341"
PURPLE = "#bc8cff"


def apply_dark(ax, yformat=None):
    ax.set_facecolor(STYLE["panel"])
    ax.tick_params(colors=STYLE["sub"], labelsize=8)
    ax.xaxis.label.set_color(STYLE["sub"])
    ax.yaxis.label.set_color(STYLE["sub"])
    ax.title.set_color(STYLE["text"])
    for sp in ax.spines.values():
        sp.set_edgecolor(STYLE["border"])
    ax.grid(axis="y", color=STYLE["grid"], linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)
    if yformat:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(yformat))


# ── GRAF 1: Spokojnosť so životom – podľa veku (škála 0-10) ──────────────────

# kz1028rs má roky: 2013, 2018, 2021, 2023, 2024 – použijeme všetky dostupné
SPOKOJNOST_VEKOVE = {
    "UKAZ04": ("16–24",  GREEN[3]),
    "UKAZ05": ("25–34",  GREEN[2]),
    "UKAZ06": ("35–49",  BLUE[2]),
    "UKAZ07": ("50–64",  ORANGE),
    "UKAZ08": ("65–74",  RED),
    "UKAZ09": ("75+",    PURPLE),
}

def plot_life_satisfaction(ax, df):
    sub = df[df["kz1028rs_ukaz"].isin(SPOKOJNOST_VEKOVE)].copy()
    sub["rok"] = sub["kz1028rs_rok"].astype(int)
    rok_vals = sorted(sub["rok"].unique())

    for ukaz, (label, color) in SPOKOJNOST_VEKOVE.items():
        row = sub[sub["kz1028rs_ukaz"] == ukaz].sort_values("rok")
        ax.plot(row["rok"], row["value"], color=color, linewidth=2,
                marker="o", markersize=5, label=label)
        if not row.empty:
            last = row.iloc[-1]
            ax.annotate(f"{label}  {last['value']:.1f}",
                        xy=(last["rok"], last["value"]),
                        xytext=(6, 0), textcoords="offset points",
                        color=color, fontsize=7.5, va="center")

    ax.set_title("Celková spokojnosť so životom  (SR, škála 0–10)", pad=8)
    ax.set_ylabel("Priemerná hodnota (0–10)")
    ax.set_xticks(rok_vals)
    ax.set_xlim(rok_vals[0] - 0.5, rok_vals[-1] + 2)
    ax.set_ylim(5.5, 9)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8,
              title="Veková skupina", title_fontsize=7.5)
    ax.legend_.get_title().set_color(STYLE["sub"])
    apply_dark(ax)


# ── GRAF 2: Medián čistého príjmu podľa veku ──────────────────────────────────

VEKS_ORDER = {
    "VEKS01": ("Spolu",  ORANGE,  "-",  "o"),
    "VEKS02": ("0–17",   BLUE[1], ":",  "s"),
    "VEKS03": ("18–24",  BLUE[2], "--", "^"),
    "VEKS04": ("25–49",  GREEN[3],"-",  "D"),
    "VEKS05": ("50–64",  GREEN[2],"--", "v"),
    "VEKS06": ("65+",    RED,     ":",  "P"),
}

def plot_median_income(ax, df):
    sub = df.copy()
    sub["rok"] = sub["kz1001rs_rok"].astype(int)
    rok_vals = sorted(sub["rok"].unique())

    for veks, (label, color, ls, marker) in VEKS_ORDER.items():
        row = sub[sub["kz1001rs_veks"] == veks].sort_values("rok")
        lw = 2.5 if veks == "VEKS01" else 1.8
        ax.plot(row["rok"], row["value"], color=color, linewidth=lw,
                linestyle=ls, marker=marker, markersize=5 if veks == "VEKS01" else 4,
                label=label)
        if not row.empty:
            last = row.iloc[-1]
            ax.annotate(f"{label}  {last['value']:,.0f} €",
                        xy=(last["rok"], last["value"]),
                        xytext=(6, 0), textcoords="offset points",
                        color=color, fontsize=7.5, va="center")

    ax.set_title("Medián ekvivalentného čistého príjmu podľa veku  (SR)", pad=8)
    ax.set_ylabel("EUR / rok")
    ax.set_xticks(rok_vals)
    ax.set_xlim(rok_vals[0] - 0.3, rok_vals[-1] + 2)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8,
              title="Veková skupina", title_fontsize=7.5)
    ax.legend_.get_title().set_color(STYLE["sub"])
    apply_dark(ax, yformat=lambda x, _: f"{x:,.0f} €")


# ── GRAF 3: Schopnosť výjsť s peniazmi ───────────────────────────────────────

def plot_money_ability(ax, df):
    sub = df.copy()
    sub["rok"] = sub["kz1008rs_rok"].astype(int)

    labels = df[["kz1008rs_typd", "kz1008rs_typd_label"]].drop_duplicates()
    label_map = dict(zip(labels["kz1008rs_typd"], labels["kz1008rs_typd_label"]))

    # 2024 snapshot – bar chart podľa typu domácnosti
    sub24 = sub[sub["rok"] == 2024].copy()
    sub24["label"] = sub24["kz1008rs_typd"].map(label_map)
    # Skrátime dlhé labely
    sub24["label_short"] = sub24["label"].str.slice(0, 38)
    sub24 = sub24.sort_values("value", ascending=True)

    colors = plt.cm.RdYlGn(np.linspace(0.15, 0.85, len(sub24)))
    bars = ax.barh(range(len(sub24)), sub24["value"], color=colors, height=0.65)

    ax.set_yticks(range(len(sub24)))
    ax.set_yticklabels(sub24["label_short"], fontsize=7.5, color=STYLE["text"])

    for bar, val in zip(bars, sub24["value"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=8, color=STYLE["text"])

    ax.set_title("Schopnosť výjsť s peniazmi – ľahko/celkom ľahko  (SR, 2024)", pad=8)
    ax.set_xlabel("% domácností")
    ax.set_xlim(0, sub24["value"].max() * 1.22)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    apply_dark(ax)
    ax.yaxis.set_major_formatter(mticker.NullFormatter())
    ax.grid(axis="x", color=STYLE["grid"], linewidth=0.6, linestyle="--")
    ax.grid(axis="y", visible=False)


# ── GRAF 4: Ekonomická aktivita – muži vs. ženy ───────────────────────────────

VEK_EA = {
    "VEK01": ("15–64 (Spolu)", ORANGE,  "-",  "o"),
    "VEK02": ("15–24",         BLUE[2], "--", "s"),
    "VEK03": ("25–54",         GREEN[3],"-",  "^"),
    "VEK04": ("55–64",         RED,     ":",  "D"),
}

def plot_activity_rate(ax, df):
    sub = df[df["kz1018rs_pohl"].isin(["POHL2", "POHL3"])].copy()
    sub = sub[sub["kz1018rs_rok"].astype(int).isin(YEARS)]
    sub["rok"] = sub["kz1018rs_rok"].astype(int)

    pohl_cfg = {
        "POHL2": ("Muži",  BLUE[2],  "-"),
        "POHL3": ("Ženy",  PURPLE, "--"),
    }

    for vek, (vek_label, _color, _ls, _m) in VEK_EA.items():
        for pohl, (pohl_label, color, ls) in pohl_cfg.items():
            row = sub[(sub["kz1018rs_vek"] == vek) &
                      (sub["kz1018rs_pohl"] == pohl)].sort_values("rok")
            alpha = 1.0 if vek == "VEK01" else 0.5
            lw = 2.2 if vek == "VEK01" else 1.4
            label = f"{pohl_label} {vek_label}" if vek == "VEK01" else f"  {pohl_label} {vek_label}"
            ax.plot(row["rok"], row["value"], color=color, linewidth=lw,
                    linestyle=ls, alpha=alpha, marker="o" if vek == "VEK01" else None,
                    markersize=4, label=label)

        if vek == "VEK01":
            ax.axhline(0, alpha=0)  # spacer

    ax.set_title("Miera ekonomickej aktivity – muži vs. ženy  (SR, 2020–2024)", pad=8)
    ax.set_ylabel("%")
    ax.set_xticks(YEARS)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=7.5, ncol=2)
    apply_dark(ax, yformat=lambda x, _: f"{x:.0f}%")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    df_spokojnost = load("kz1028rs")
    df_prijem     = load("kz1001rs")
    df_peniaze    = load("kz1008rs")
    df_aktivita   = load("kz1018rs")

    fig, axes = plt.subplots(2, 2, figsize=(20, 13))
    fig.patch.set_facecolor(STYLE["bg"])
    fig.suptitle("Kvalita života  |  ŠÚ SR DATAcube",
                 color=STYLE["text"], fontsize=15, fontweight="bold", y=0.98)

    plot_life_satisfaction(axes[0, 0], df_spokojnost)
    plot_median_income(axes[0, 1], df_prijem)
    plot_money_ability(axes[1, 0], df_peniaze)
    plot_activity_rate(axes[1, 1], df_aktivita)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = OUT / "quality_life_analysis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✓ Uložené: {out}")


if __name__ == "__main__":
    main()
