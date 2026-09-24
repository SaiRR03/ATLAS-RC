# ATLAS-RC2 public trial app

This folder contains the deployable Streamlit demonstrator for Project Atlas RC2.

It estimates a central benchmark and an approximately 80% marginal prediction interval for publicly reported US data-centre investment. It does not estimate verified construction outturn and does not provide investment, lending or engineering advice.

The original Jupyter RC2 experiment used 263 screened observations split 151 development / 60 calibration / 52 test. This web app is a separately reconstructed public demonstrator trained under a different 346-row eligibility rule and five-fold state-grouped validation.

The expanded specification is experimental. Its grouped-validation log-MAE is slightly worse than the capacity-only specification, so additional inputs do not currently demonstrate better predictive accuracy.
