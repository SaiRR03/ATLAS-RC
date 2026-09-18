# ATLAS-RC v1.0.0

**Optimising Reference-Class Selection for Capital Cost Estimation: A Machine-Learning Experiment Using Public Data**

ATLAS-RC is a bounded empirical experiment asking whether a machine-selected reference class, based on project similarity, improves out-of-sample estimation of reported capital intensity relative to a broad outside-view baseline.

## Research question

> Can machine-learning methods identify reference classes that improve out-of-sample capital cost estimation relative to a universal reference class?

This release tests a deliberately narrow version of that question using two similarity features:

- reported project power capacity (MW)
- reported gross floor area (ft²)

The target is:

`reported investment / reported project power capacity`

It should **not** be interpreted as actual outturn construction CAPEX, cost overrun, contingency, or a causal estimate.

## Data

The experiment uses the public U.S. data-centre project database published by Server Country.

Source:
- https://servercountry.org/data/downloads/
- https://servercountry.org/data/methodology/

Server Country describes `investmentUSD` as total announced investment and `powerCapacityMW` as peak power capacity. Its documentation warns that announced investment may cover multi-phase programmes and that power capacity may represent planned maximum capacity.

The source dataset is licensed CC BY 4.0. Please cite the original data creators as specified by Server Country.

### Reproducing the analysis

1. Download the current CSV dataset from Server Country.
2. Save it as `dataset.csv` in the repository root.
3. Install the Python dependencies:
   `pip install -r requirements.txt`
4. Run:
   `python atlas_rc.py`

The original executed research record used for this release is included as `Code_atlas_v1.0.pdf`.

## Frozen experiment

Analytical sample with both modelling features available: **503 projects**

Split:
- Development: **402**
- Locked test: **101**
- Random seed: **42**

Model:
- StandardScaler fitted on development/training data only
- Euclidean distance
- k-nearest-neighbour reference-class selection
- median reference-class capital intensity
- k selected by 5-fold cross-validation on development data only
- primary metric: MAE

Cross-validation selected:

`k = 100`

Development CV:
- Global median baseline MAE: **$5.86m/MW**
- kNN reference-class MAE: **$5.88m/MW**
- Change vs global: **-0.3%**

Locked test:
- Global median baseline MAE: **$6.59m/MW**
- kNN reference-class MAE: **$6.62m/MW**
- Global RMSE: **$17.60m/MW**
- kNN reference-class RMSE: **$17.50m/MW**
- MAE change vs global: **-0.56%**

## Main result

In this experiment, the frozen machine-selected reference class did **not** improve the primary out-of-sample MAE relative to the global-median outside-view baseline.

This is a narrow empirical result. It does not establish that reference-class forecasting or machine learning is generally ineffective. It shows that, under this dataset, target definition, two-feature similarity representation, validation protocol, and estimator, local similarity did not earn its added complexity on the primary metric.

## Important limitations

- Reported investment is announced investment, not verified outturn CAPEX.
- Investment and MW scopes may not always align.
- The target distribution is strongly right-skewed.
- The experiment uses only MW and gross floor area as similarity features.
- A random 80/20 split was used; temporal, sponsor, campus and geography-grouped validation were not part of this bounded experiment.
- The test set was opened once after the kNN specification was frozen.
- The source database is periodically updated, so a fresh download may not reproduce the exact numerical results of this release unless the same source snapshot is used.

## Repository contents

- `atlas_rc.py` - compact reproducible implementation
- `Code_atlas_v1.0.pdf` - executed research/code record
- `METHODOLOGY.md` - experimental design and definitions
- `RESULTS.md` - frozen results
- `DATA.md` - source, licence and data limitations
- `requirements.txt` - Python dependencies
- `CITATION.cff` - citation metadata
- `LICENSE` - MIT licence for original code/documentation
- `figures/atlas_final_test.png` - final locked-test figure

## Licence

Original ATLAS-RC code and documentation in this repository are released under the MIT License.

The Server Country source dataset is separate third-party material licensed by its creators under CC BY 4.0. The MIT licence does not replace or alter the dataset's licence or attribution requirements.
