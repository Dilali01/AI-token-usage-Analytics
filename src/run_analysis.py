"""Clean community.csv with SQLite and produce reproducible EDA outputs."""
from __future__ import annotations

import csv
import html
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "community.csv"
CLEAN = ROOT / "data" / "community_clean.csv"
SQL = ROOT / "sql" / "cleaning.sql"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
FIELDS = ["date", "dimension", "dimension_value", "events", "tokens", "cost",
          "contributors", "success", "quality_avg", "latency_avg_ms"]


def load_and_clean() -> list[dict]:
    if not RAW.exists():
        raise FileNotFoundError(f"Source CSV not found: {RAW}")
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE raw_community (" + ", ".join(f'"{f}" TEXT' for f in FIELDS) + ")")
    with RAW.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing expected columns: {sorted(missing)}")
        db.executemany(
            "INSERT INTO raw_community VALUES (" + ",".join("?" for _ in FIELDS) + ")",
            ([row.get(field, "") for field in FIELDS] for row in reader),
        )
    db.executescript(SQL.read_text(encoding="utf-8"))
    rows = [dict(zip(FIELDS, row)) for row in db.execute(
        "SELECT " + ",".join(FIELDS) + " FROM clean_community ORDER BY date, dimension, dimension_value"
    )]
    db.close()
    with CLEAN.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_svg(path: Path, title: str, labels: list[str], values: list[float], *, kind="line", color="#3867d6", suffix="") -> None:
    """Write a compact, dependency-free SVG bar or line chart."""
    w, h = 960, 460
    left, right, top, bottom = 82, 30, 62, 82
    pw, ph = w - left - right, h - top - bottom
    maxv = max(values, default=1) or 1
    maxv *= 1.12
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
             '<rect width="100%" height="100%" fill="#ffffff"/>',
             f'<text x="{left}" y="34" font-family="Arial,sans-serif" font-size="21" font-weight="bold" fill="#172033">{html.escape(title)}</text>']
    for i in range(5):
        y = top + ph * i / 4
        tick = maxv * (1 - i / 4)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w-right}" y2="{y:.1f}" stroke="#e4e8ef"/>')
        parts.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="11" fill="#596579">{tick:,.0f}{suffix}</text>')
    if kind == "line":
        coords = []
        n = max(1, len(values)-1)
        for i, value in enumerate(values):
            x = left + pw * i / n
            y = top + ph * (1 - value / maxv)
            coords.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
        for i in sorted(set([0, len(labels)//2, max(0, len(labels)-1)])):
            if labels:
                x = left + pw * i / max(1, len(labels)-1)
                parts.append(f'<text x="{x:.1f}" y="{h-49}" text-anchor="middle" font-family="Arial" font-size="11" fill="#596579">{html.escape(labels[i])}</text>')
    else:
        n = max(1, len(values))
        slot = pw / n
        bw = min(52, slot * .66)
        for i, (label, value) in enumerate(zip(labels, values)):
            x = left + slot * i + (slot - bw) / 2
            bh = ph * value / maxv
            y = top + ph - bh
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{color}"/>')
            parts.append(f'<text x="{x+bw/2:.1f}" y="{h-51}" text-anchor="middle" font-family="Arial" font-size="10" fill="#596579">{html.escape(label)}</text>')
    parts += ['<text x="18" y="220" transform="rotate(-90 18 220)" font-family="Arial" font-size="12" fill="#596579">Value</text>', '</svg>']
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows = load_and_clean()
    total = sorted((r for r in rows if r["dimension"] == "total"), key=lambda r: r["date"])
    models = defaultdict(lambda: {"events": 0, "tokens": 0, "cost": 0.0, "days": 0})
    for r in rows:
        if r["dimension"] == "model":
            m = models[r["dimension_value"]]
            m["events"] += r["events"]
            m["tokens"] += r["tokens"]
            m["cost"] += r["cost"]
            m["days"] += 1
    dates = [r["date"] for r in total]
    daily_cost = [r["cost"] for r in total]
    daily_events = [r["events"] for r in total]
    daily_tokens = [r["tokens"] for r in total]
    write_svg(FIGURES / "daily_cost.svg", "Daily aggregate cost", dates, daily_cost, color="#3867d6", suffix="")
    write_svg(FIGURES / "daily_events.svg", "Daily aggregate events", dates, daily_events, color="#20a486")
    ranked = sorted(models.items(), key=lambda item: item[1]["cost"], reverse=True)
    write_svg(FIGURES / "model_cost.svg", "Cumulative cost by model", [m for m, _ in ranked], [v["cost"] for _, v in ranked], kind="bar", color="#7655c9")
    first, last = dates[0], dates[-1]
    days = len(total)
    all_events = sum(daily_events)
    all_tokens = sum(daily_tokens)
    all_cost = sum(daily_cost)
    report = [
        "# EDA summary", "", 
        "> This report describes the supplied aggregate dataset. It does not identify users or infer individual behavior.", "",
        "## Data profile", "",
        f"- Source rows: {len(rows):,} cleaned records across {len(set(r['date'] for r in rows))} observed dates.",
        f"- Date span: {first} through {last} ({days} daily total observations; dates may be missing).",
        f"- Dimensions: {', '.join(sorted(set(r['dimension'] for r in rows)))}.",
        "- All `success` observations are 0; `quality_avg` and `latency_avg_ms` are entirely null in the source.",
        "- Platform/provider/use_case each have only one observed category in this extract, so they do not support comparative analysis.", "",
        "## Descriptive totals", "",
        f"- Aggregate events across `dimension=total`: {all_events:,}.",
        f"- Aggregate tokens across `dimension=total`: {all_tokens:,}.",
        f"- Aggregate cost across `dimension=total`: {all_cost:,.6f} (source currency/unit is unspecified).",
        f"- Mean cost per observed date: {all_cost / days:,.6f}.",
        f"- Mean cost per event: {all_cost / all_events:,.6f} (descriptive only; unit unspecified).", "",
        "## Model breakdown", "",
        "| Model | Observed days | Events | Tokens | Cost (source units) |", "|---|---:|---:|---:|---:|"
    ]
    for model, val in ranked:
        report.append(f"| {model} | {val['days']} | {val['events']:,} | {val['tokens']:,} | {val['cost']:,.6f} |")
    report += ["", "## Figures", "", "![Daily aggregate cost](figures/daily_cost.svg)", "", "![Daily aggregate events](figures/daily_events.svg)", "", "![Cumulative cost by model](figures/model_cost.svg)", "",
               "## Interpretation limits", "",
               "The rows are overlapping daily rollups, not a transaction-level event ledger. Totals in this report use only `dimension=total`; model breakdowns use only `dimension=model`. Values across dimensions must not be added together. Missing calendar dates are not filled or treated as zero. Cost currency, token definition, event definition, success encoding, and collection methodology are not documented in the file, so no unit conversion, causal claim, or success-rate estimate is made.", ""]
    (REPORTS / "eda_summary.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Cleaned {len(rows)} rows -> {CLEAN}")
    print(f"Generated EDA summary and figures in {REPORTS}")


if __name__ == "__main__":
    main()
