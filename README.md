# Agentic Analytics Dashboard

A reproducible analytics project built around the supplied `community.csv` export. It uses SQL to validate and clean the daily rollups, then Python to profile the data, calculate descriptive metrics, and generate SVG charts for a GitHub portfolio.

## Project questions

- How did aggregate activity, token volume, and reported cost vary by observed date?
- How do those measures differ across the model dimension?
- What can this extract support, and which quality or metadata gaps limit interpretation?

## Findings in this extract

- 518 cleaned records across 114 observed dates, from May 22 through October 19, 2026.
- The `total` dimension reports 3,665 events, 194,648,481,236 tokens, and 9,843.659769 cost units in aggregate.
- Model rows provide a separate breakdown. Opus 4.8 has the largest accumulated model cost in this export (155.662048); this is descriptive and is not a normalized efficiency comparison.
- `success` is zero in every source row, while `quality_avg` and `latency_avg_ms` are blank throughout. Platform, provider, and use case each have only one observed category.

Cost units, token definitions, event definitions, and the meaning/encoding of `success` are not documented in the source. For that reason, this project reports the raw cost field without assigning a currency, and it does not estimate a success rate, performance quality, or latency.

## Data and outputs

- `data/community.csv`: unchanged source export provided for this analysis.
- `data/community_clean.csv`: deduplicated, typed, filtered output from the SQL cleaning view.
- `sql/cleaning.sql`: SQLite cleaning logic.
- `src/run_analysis.py`: loads the source CSV into SQLite, applies the SQL view, exports clean data, calculates summaries, and creates charts.
- `reports/eda_summary.md`: generated profile, descriptive totals, model table, figures, and interpretation limits.
- `reports/figures/`: generated SVG charts.

## Reproduce the workflow

Requires Python 3.10 or newer. The analysis uses only the Python standard library and SQLite, so there are no third-party package dependencies.

From this project directory, run:

```bash
python src/run_analysis.py
```

The script reads `data/community.csv` and regenerates `data/community_clean.csv`, `reports/eda_summary.md`, and all SVG figures. To use another export, replace `data/community.csv` while retaining the expected headers.

## Workflow

1. **Inspect source structure:** check headers, row count, date range, dimension categories, nulls, and repeated records.
2. **Clean with SQL:** trim and normalize dimension labels, parse valid dates, cast numeric fields, convert blank quality/latency measures to `NULL`, reject invalid or negative count/cost records, and remove exact duplicate records.
3. **Respect the data grain:** treat each row as a daily aggregate for one dimension/category. Use only `dimension = 'total'` for overall trends and only `dimension = 'model'` for model comparisons. Never sum across dimensions.
4. **Explore with Python:** calculate observed-date totals and per-model totals; retain missing calendar dates as missing rather than assuming zero.
5. **Visualize:** generate daily cost, daily events, and cumulative model cost charts as portable SVG files.
6. **Document limits:** call out absent metric definitions and unavailable quality/latency data before drawing conclusions.

## Data dictionary

| Field | Meaning in source | Cleaning / use |
|---|---|---|
| `date` | Aggregation date | Parsed as ISO date |
| `dimension` | Rollup type (`total`, `model`, etc.) | Trimmed and lowercased |
| `dimension_value` | Category for that rollup | Trimmed and lowercased |
| `events` | Reported event count | Non-negative integer |
| `tokens` | Reported token count | Non-negative integer |
| `cost` | Reported cost value | Non-negative decimal; unit unspecified |
| `contributors` | Reported contributor count | Non-negative integer |
| `success` | Source success field | Integer retained as provided; all observed values are 0 |
| `quality_avg` | Average quality metric | Blank values become `NULL`; all source rows are blank |
| `latency_avg_ms` | Average latency in milliseconds | Blank values become `NULL`; all source rows are blank |

## Method and limitations

This is an exploratory analysis of an aggregate export, not a causal study or user-level analysis. Dates with no row in a dimension are not interpolated. Model observations cover different numbers of dates, and cumulative cost is not normalized by activity, so raw totals should not be read as model efficiency. The SQL view keeps only recognized dimensions and valid non-negative counts/cost values. It does not impute missing measurements or reinterpret the `success` field.

## Portfolio presentation

Suggested dashboard cards: **Total events**, **Total tokens**, **Reported cost**, and **Observed dates**. Suggested charts: **daily reported cost**, **daily events**, and **cumulative reported cost by model**. Keep a visible note that cost units and success semantics are unspecified, and expose the date/dimension filters in any interactive dashboard built from `community_clean.csv`.
