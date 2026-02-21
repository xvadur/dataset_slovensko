"""
Vrstva 3 + 5: Vzdelanie & Digitalizácia
  - Vzdelanostná štruktúra muži vs. ženy (ISCED 0-2 / 3-4 / 5-8)
  - Trend terciárneho vzdelania podľa pohlavia (2020-2024)
  - VŠ študenti na 1000 obyvateľov podľa miest
  - Digitálna priepasť – seniori a internet (45-75+)
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


def filter_years(df, rok_col):
    return df[df[rok_col].astype(int).isin(YEARS)].copy()


# ── GRAF 1: Vzdelanostná štruktúra – muži vs ženy (2024) ─────────────────────

VZD_LABELS = {
    "VZD01": ("Základné\n(ISCED 0–2)", RED),
    "VZD02": ("Stredné\n(ISCED 3–4)", BLUE[2]),
    "VZD03": ("Terciárne\n(ISCED 5–8)", GREEN[3]),
}

def plot_edu_structure(ax, df):
    sub = df[
        (df["kz1030rs_rok"] == "2024") &
        (df["kz1030rs_pohl"].isin(["POHL1", "POHL2", "POHL3"]))
    ].copy()

    pohl_map = {"POHL1": "Spolu", "POHL2": "Muži", "POHL3": "Ženy"}
    pohl_order = ["Muži", "Ženy", "Spolu"]
    sub["pohl"] = sub["kz1030rs_pohl"].map(pohl_map)

    x = np.arange(len(pohl_order))
    width = 0.55
    bottom = np.zeros(len(pohl_order))

    for vzd, (label, color) in VZD_LABELS.items():
        vals = [
            sub[(sub["kz1030rs_vzd"] == vzd) & (sub["pohl"] == p)]["value"].values
            for p in pohl_order
        ]
        vals = np.array([v[0] if len(v) > 0 else 0 for v in vals])
        bars = ax.bar(x, vals, width, bottom=bottom, color=color,
                      label=label, edgecolor=STYLE["bg"], linewidth=0.5)
        for bar, val, bot in zip(bars, vals, bottom):
            if val > 3:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bot + val / 2, f"{val:.1f}%",
                        ha="center", va="center", fontsize=8.5,
                        color="white", fontweight="bold")
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(pohl_order, color=STYLE["text"], fontsize=9)
    ax.set_title("Vzdelanostná štruktúra  (SR, 2024)", pad=8)
    ax.set_ylabel("%")
    ax.set_ylim(0, 108)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8,
              loc="upper right", ncol=3)
    apply_dark(ax)


# ── GRAF 2: Trend VŠ vzdelaných podľa pohlavia (2020-2024) ───────────────────

def plot_edu_trend(ax, df):
    sub = filter_years(df, "kz1030rs_rok")
    sub["rok"] = sub["kz1030rs_rok"].astype(int)
    sub = sub[sub["kz1030rs_vzd"] == "VZD03"]

    pohl_cfg = {
        "POHL1": ("Spolu",  ORANGE,  "-",  "o"),
        "POHL2": ("Muži",   BLUE[2], "--", "s"),
        "POHL3": ("Ženy",   PURPLE,  ":",  "^"),
    }

    for pohl, (label, color, ls, marker) in pohl_cfg.items():
        row = sub[sub["kz1030rs_pohl"] == pohl].sort_values("rok")
        ax.plot(row["rok"], row["value"], color=color, linewidth=2.2,
                linestyle=ls, marker=marker, markersize=5, label=label)
        if not row.empty:
            last = row.iloc[-1]
            ax.annotate(f"{label}  {last['value']:.1f}%",
                        xy=(last["rok"], last["value"]),
                        xytext=(6, 0), textcoords="offset points",
                        color=color, fontsize=7.5, va="center")

    ax.set_title("Podiel ľudí s terciárnym vzdelaním (ISCED 5–8)  (SR, 2020–2024)", pad=8)
    ax.set_ylabel("% z 15–64 ročných")
    ax.set_xticks(YEARS)
    ax.set_xlim(YEARS[0] - 0.3, YEARS[-1] + 1.8)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8)
    apply_dark(ax, yformat=lambda x, _: f"{x:.0f}%")


# ── GRAF 3: VŠ študenti na 1000 obyv. podľa miest ────────────────────────────

MESTA = {
    "SK_CAP":         "Bratislava",
    "SK0321508438":   "Banská Bystrica",
    "SK0422_0425":    "Košice",
    "SK031B517402":   "Žilina",
    "SK0417524140":   "Prešov",
    "SK0229505820":   "Trenčín",
    "SK0233500011":   "Nitra",
    "SK0217506745":   "Trnava",
}
MESTA_COLORS = [GREEN[3], GREEN[2], BLUE[3], BLUE[2], ORANGE, PURPLE, RED, "#f0883e"]

def plot_vs_mesta(ax, df2):
    sub = df2[
        (df2["sv3701rr_uzemieua"].isin(MESTA)) &
        (df2["sv3701rr_vzdel"] == "VZDEL_VS_1000") &
        (df2["sv3701rr_poh"] == "TOTAL")
    ].copy()
    sub = filter_years(sub, "sv3701rr_rok")
    sub["rok"] = sub["sv3701rr_rok"].astype(int)
    sub["mesto"] = sub["sv3701rr_uzemieua"].map(MESTA)

    for i, (kod, mesto) in enumerate(MESTA.items()):
        row = sub[sub["sv3701rr_uzemieua"] == kod].sort_values("rok")
        if row.empty or row["value"].isna().all():
            continue
        color = MESTA_COLORS[i]
        ax.plot(row["rok"], row["value"], color=color, linewidth=2,
                marker="o", markersize=4, label=mesto)
        last = row.dropna(subset=["value"])
        if not last.empty:
            last = last.iloc[-1]
            ax.annotate(f"{mesto}  {last['value']:.0f}",
                        xy=(last["rok"], last["value"]),
                        xytext=(6, 0), textcoords="offset points",
                        color=color, fontsize=7, va="center")

    ax.set_title("Študenti VŠ na 1 000 obyvateľov  (mestá, 2020–2024)", pad=8)
    ax.set_ylabel("Študenti / 1 000 obyv.")
    ax.set_xticks(YEARS)
    ax.set_xlim(YEARS[0] - 0.3, YEARS[-1] + 2.2)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=7.5, ncol=2)
    apply_dark(ax)


# ── GRAF 4: Digitálna priepasť – internet nikdy nepoužili podľa veku ─────────

AGE_INTERNET = {
    "AGE_Y45-54": ("45–54", GREEN[3]),
    "AGE_Y55-64": ("55–64", BLUE[2]),
    "AGE_Y65-74": ("65–74", ORANGE),
    "AGE_Y_GE75": ("75+",   RED),
}

def plot_digital_gap(ax, df3):
    # UKAZ16 = internet nikdy nepoužili (%, celkovo)
    sub = df3[
        (df3["as1012rs_ukaz"] == "UKAZ16") &
        (df3["as1012rs_vek"].isin(AGE_INTERNET))
    ].copy()
    sub = filter_years(sub, "as1012rs_rok")
    sub["rok"] = sub["as1012rs_rok"].astype(int)

    for vek_kod, (label, color) in AGE_INTERNET.items():
        row = sub[sub["as1012rs_vek"] == vek_kod].sort_values("rok")
        if row.empty or row["value"].isna().all():
            continue
        ax.plot(row["rok"], row["value"], color=color, linewidth=2.2,
                marker="o", markersize=5, label=f"{label} rokov")
        last = row.dropna(subset=["value"])
        if not last.empty:
            last = last.iloc[-1]
            ax.annotate(f"{label} r.  {last['value']:.0f}%",
                        xy=(last["rok"], last["value"]),
                        xytext=(6, 0), textcoords="offset points",
                        color=color, fontsize=7.5, va="center")

    ax.set_title("Digitálna priepasť – nikdy nepoužili internet  (SR, 2020–2024)", pad=8)
    ax.set_ylabel("% respondentov")
    ax.set_xticks(YEARS)
    ax.set_xlim(YEARS[0] - 0.3, YEARS[-1] + 1.8)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8)
    apply_dark(ax, yformat=lambda x, _: f"{x:.0f}%")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    df_edu    = load("kz1030rs")
    df_mesta  = load("sv3701rr")
    df_inet   = load("as1012rs")

    fig, axes = plt.subplots(2, 2, figsize=(20, 13))
    fig.patch.set_facecolor(STYLE["bg"])
    fig.suptitle("Vzdelanie & Digitalizácia  |  ŠÚ SR DATAcube",
                 color=STYLE["text"], fontsize=15, fontweight="bold", y=0.98)

    plot_edu_structure(axes[0, 0], df_edu)
    plot_edu_trend(axes[0, 1], df_edu)
    plot_vs_mesta(axes[1, 0], df_mesta)
    plot_digital_gap(axes[1, 1], df_inet)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = OUT / "education_digital_analysis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✓ Uložené: {out}")


if __name__ == "__main__":
    main()
