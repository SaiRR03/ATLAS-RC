# ATLAS-RC2 public demonstrator model card

The app estimates publicly reported or announced US data-centre investment, not verified construction outturn.

The capacity-only specification uses ridge regression on log capacity. The experimental expanded specification adds log floor area, US state and announcement year. Both predict log reported investment and use absolute grouped out-of-fold log residuals to form an approximately 80% marginal conformal interval.

The public demonstrator uses 346 rows and five-fold grouped validation by US state. Grouped OOF log-MAE is approximately 0.740 for capacity-only and 0.752 for the expanded specification. The expanded specification therefore does not demonstrate improved predictive accuracy on this metric.

The original Jupyter RC2 experiment is separate: 263 screened observations split 151 development / 60 calibration / 52 test. Do not present the public app as the frozen original experiment.

Public announcements can contain inconsistent scopes, phases and maturity levels. Power capacity may not represent delivered IT load. The app does not provide investment, lending, engineering or construction-cost advice.
