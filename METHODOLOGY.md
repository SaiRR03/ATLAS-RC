# Methodology

## 1. Objective

ATLAS-RC tests whether a data-driven reference-class selector improves out-of-sample estimation of reported investment intensity relative to a universal outside-view baseline.

## 2. Target

For project i:

`Y_i = investmentUSD_i / powerCapacityMW_i`

Interpretation: reported project investment per MW of reported project power capacity.

The target is not labelled actual CAPEX because the source field is announced investment.

## 3. Eligibility

Initial numerical eligibility requires:

- `investmentUSD` present and > 0
- `powerCapacityMW` present and > 0

The modelling experiment additionally requires:

- `totalSquareFeet` present and > 0

The executed experiment produced 503 modelling observations.

No observation was removed merely because its capital intensity was statistically extreme.

## 4. Baseline

The global outside-view estimator is the median target value in the relevant training sample.

## 5. Machine-selected reference class

Features:

- `powerCapacityMW`
- `totalSquareFeet`

For every training fold:

1. Fit `StandardScaler` on training features only.
2. Transform training and validation/test features using that scaler.
3. Calculate Euclidean distances.
4. Select the k nearest training projects.
5. Predict the target as the median target value of those k projects.

## 6. Model selection

The full analytical sample was split once using an 80/20 random split with `random_state=42`.

Development set: 402 projects.
Locked test set: 101 projects.

Candidate k values:

`3, 5, 10, 15, 20, 30, 50, 75, 100`

k was selected using 5-fold shuffled cross-validation on the development set only, also using random state 42.

Primary metric: MAE.
Secondary metric: RMSE.

The selected value was k=100.

## 7. Locked test

After model selection, the development data were used to fit preprocessing and the kNN selector. The locked test set was then evaluated once.

No post-test tuning is part of v1.0.0.

## 8. Exploratory diagnostics

The executed research record also examined:

- missingness and feature availability
- capital-intensity distribution
- error by capacity band
- Spearman associations
- log investment vs log power scaling
- the relationship between reference-class size and CV error

The fitted exploratory scaling model was:

`log(investmentUSD) = alpha + beta * log(powerCapacityMW) + error`

with beta approximately 0.9208 and in-sample R² approximately 0.7628.

These exploratory statistics are descriptive and are not causal estimates.

## 9. Interpretation boundary

The experiment tests one operationalisation of similarity. It does not establish a universal conclusion about Reference Class Forecasting, data-centre cost functions, or machine learning.
