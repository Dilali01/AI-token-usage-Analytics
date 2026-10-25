# EDA summary

> This report describes the supplied aggregate dataset. It does not identify users or infer individual behavior.

## Data profile

- Source rows: 518 cleaned records across 114 observed dates.
- Date span: 2026-05-22 through 2026-10-19 (114 daily total observations; dates may be missing).
- Dimensions: model, platform, provider, total, use_case.
- All `success` observations are 0; `quality_avg` and `latency_avg_ms` are entirely null in the source.
- Platform/provider/use_case each have only one observed category in this extract, so they do not support comparative analysis.

## Descriptive totals

- Aggregate events across `dimension=total`: 3,665.
- Aggregate tokens across `dimension=total`: 194,648,481,236.
- Aggregate cost across `dimension=total`: 9,843.659769 (source currency/unit is unspecified).
- Mean cost per observed date: 86.347893.
- Mean cost per event: 2.685855 (descriptive only; unit unspecified).

## Model breakdown

| Model | Observed days | Events | Tokens | Cost (source units) |
|---|---:|---:|---:|---:|
| claude-opus-4-8 | 5 | 96 | 11,217,976,995 | 155.662048 |
| claude-opus-5-5 | 11 | 128 | 16,614,409,711 | 154.993203 |
| claude-opus-5 | 18 | 209 | 20,052,884,627 | 140.087871 |
| claude-sonnet-5 | 19 | 402 | 4,811,048,213 | 82.198016 |
| claude-sonnet-4-6 | 5 | 70 | 790,744,188 | 17.890115 |
| claude-sonnet-5-5 | 3 | 145 | 520,737,961 | 10.495904 |
| claude-opus-4-7 | 1 | 21 | 50,896,561 | 3.091808 |
| unknown | 2 | 8 | 0 | 0.000000 |

## Figures

![Daily aggregate cost](figures/daily_cost.svg)

![Daily aggregate events](figures/daily_events.svg)

![Cumulative cost by model](figures/model_cost.svg)

## Interpretation limits

The rows are overlapping daily rollups, not a transaction-level event ledger. Totals in this report use only `dimension=total`; model breakdowns use only `dimension=model`. Values across dimensions must not be added together. Missing calendar dates are not filled or treated as zero. Cost currency, token definition, event definition, success encoding, and collection methodology are not documented in the file, so no unit conversion, causal claim, or success-rate estimate is made.
