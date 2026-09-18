# Results

## Frozen development result

Analytical sample: 503 projects.

Development/test split:
- Development: 402
- Locked test: 101

5-fold development-set cross-validation selected `k = 100`.

| Model | Development CV MAE |
|---|---:|
| Global median outside view | $5.86m/MW |
| ML-selected reference class | $5.88m/MW |

Relative MAE change vs global: **-0.3%**.

A negative value means the kNN reference-class method had higher MAE than the global baseline.

## Locked out-of-sample test

| Model | MAE | RMSE |
|---|---:|---:|
| Global median outside view | $6.59m/MW | $17.60m/MW |
| ML-selected reference class | $6.62m/MW | $17.50m/MW |

Primary result:

**MAE change vs global = -0.56%.**

The frozen kNN reference-class method therefore did not improve the primary locked-test MAE relative to the global median baseline. Its RMSE was slightly lower, but RMSE was secondary and does not overturn the pre-specified primary result.

## What the result supports

Under the frozen v1.0.0 experiment, similarity defined only by reported MW and gross floor area did not demonstrate incremental predictive value on the primary metric.

## What the result does not support

The experiment does not show that:

- all reference-class methods fail
- all machine-learning methods fail
- MW and area have no relationship with project cost
- the result generalises to other assets, datasets, targets or time periods
- the source data represent verified actual outturn CAPEX

## Measurement warning

The source target is highly right-skewed and contains observations with very high reported investment per MW. The source documentation itself warns that announced investment can include multi-phase totals and that capacity may represent planned maximum capacity. These limitations are material to interpretation.
