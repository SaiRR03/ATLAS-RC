from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.predictor import estimate_investment, load_bundle


ROOT = Path(__file__).resolve().parent
METADATA_PATH = ROOT / "artefacts" / "model_metadata.json"

st.set_page_config(page_title="ATLAS Data Centre Investment Benchmark", page_icon=None, layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1100px; padding-top: 2rem;}
    .atlas-kicker {color:#2563eb; font-weight:700; letter-spacing:.08em; font-size:.78rem;}
    .atlas-note {background:#f8fafc; border-left:4px solid #2563eb; padding:1rem 1.1rem;}
    div[data-testid="stMetric"] {background:#f8fafc; border:1px solid #e2e8f0; padding:1rem; border-radius:.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

bundle = load_bundle()
domain = bundle["domain"]
metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

st.markdown('<div class="atlas-kicker">PROJECT ATLAS · RC2</div>', unsafe_allow_html=True)
st.title("Data Centre Investment Benchmark")
st.write(
    "Explore a probability range for publicly reported US data-centre investment "
    "using early project characteristics and historical reference evidence."
)
st.markdown(
    '<div class="atlas-note"><strong>Public research demonstrator.</strong> The model predicts '
    "reported or announced investment, not verified construction outturn. It does not "
    "replace a detailed cost estimate, engineering estimate, lending decision or investment appraisal.</div>",
    unsafe_allow_html=True,
)

st.subheader("Project inputs")
left, right = st.columns(2)
with left:
    capacity = st.number_input(
        "Power capacity (MW)", min_value=0.1, value=100.0, step=10.0,
        help=f"Central training range: {domain['capacity_min']:.1f} to {domain['capacity_max']:.0f} MW."
    )
    use_details = st.checkbox(
        "Try the experimental expanded specification", value=False,
        help=(
            "Uses capacity, floor area, state and announcement year. In this public demonstrator, "
            "it did not improve grouped-validation log-MAE versus the capacity-only specification."
        ),
    )

with right:
    if use_details:
        area = st.number_input("Gross floor area (sq ft)", min_value=1_000.0, value=500_000.0, step=50_000.0)
        state = st.selectbox("US state", options=domain["states"])
        year = st.number_input(
            "Announcement year", min_value=domain["year_min"],
            max_value=max(domain["year_max"], date.today().year),
            value=min(date.today().year, domain["year_max"]), step=1,
        )
    else:
        area, state, year = None, None, None
        st.info("The capacity-only specification will be used.")

run = st.button("Estimate reported investment", type="primary", use_container_width=True)

if run:
    try:
        result = estimate_investment(capacity, area, state, int(year) if year else None)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.divider()
    st.subheader("Benchmark result")
    c1, c2, c3 = st.columns(3)
    c1.metric("Lower bound · ~80% interval", result["formatted"]["lower_80"])
    c2.metric("Central benchmark", result["formatted"]["central"])
    c3.metric("Upper bound · ~80% interval", result["formatted"]["upper_80"])

    chart_data = pd.DataFrame({
        "Estimate": ["Lower", "Central", "Upper"],
        "USD billions": [
            result["interval_lower_80_usd"] / 1e9,
            result["central_usd"] / 1e9,
            result["interval_upper_80_usd"] / 1e9,
        ],
    })
    chart = (
        alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Estimate:N", sort=["Lower", "Central", "Upper"], title=None),
            y=alt.Y("USD billions:Q", title="Reported investment, USD bn"),
            tooltip=["Estimate:N", alt.Tooltip("USD billions:Q", format=",.2f")],
        ).properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    a, b, c = st.columns(3)
    a.metric("Central intensity", result["formatted"]["central_per_mw"])
    b.metric("Applicability", result["applicability"])
    c.metric("Specification", result["model_used"].replace("_", " ").title())

    st.write(
        f"For a **{capacity:,.0f} MW** project, the model estimates a central reported-investment "
        f"benchmark of **{result['formatted']['central']}**, with an approximately 80% marginal "
        f"prediction interval of **{result['formatted']['lower_80']} to {result['formatted']['upper_80']}**."
    )
    for warning in result["warnings"]:
        st.warning(warning)

    export = pd.DataFrame([{
        "capacity_mw": capacity,
        "floor_area_sqft": area,
        "state": state,
        "announcement_year": year,
        "interval_lower_80_usd": result["interval_lower_80_usd"],
        "central_usd": result["central_usd"],
        "interval_upper_80_usd": result["interval_upper_80_usd"],
        "central_usd_per_mw": result["central_usd_per_mw"],
        "applicability": result["applicability"],
        "model_used": result["model_used"],
        "model_version": result["model_version"],
    }])
    st.download_button(
        "Download result as CSV", export.to_csv(index=False),
        file_name="atlas_rc2_estimate.csv", mime="text/csv"
    )

st.divider()
with st.expander("How the demonstrator works"):
    st.write(
        "The central specification predicts log reported investment using ridge regression. "
        "Absolute grouped out-of-fold log residuals calibrate an approximately 80% marginal "
        "conformal interval. Validation groups projects by US state."
    )
    st.write(
        "The original Jupyter RC2 experiment used a separate 151/60/52 development, calibration "
        "and test structure. This public app is a separately reconstructed demonstrator and must "
        "not be presented as the frozen original experiment."
    )
with st.expander("Validation snapshot"):
    rows = []
    for name, values in metadata["models"].items():
        rows.append({
            "Specification": name.replace("_", " ").title(),
            "Grouped OOF log-MAE": values["grouped_oof_log_mae"],
            "Observed interval coverage": values["grouped_oof_coverage"],
            "Training rows": values["n"],
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption(
        "The expanded specification's grouped-validation log-MAE is slightly worse than the "
        "capacity-only specification, so additional inputs do not currently demonstrate better accuracy."
    )
with st.expander("Important limitations"):
    st.markdown(
        """
        - Source values represent public reported or announced investment.
        - Investment, capacity and floor-area scopes may not align across projects.
        - Prediction intervals express historical dispersion, not construction contingency.
        - Marginal interval coverage does not guarantee 80% coverage for every individual project type.
        - The demonstrator's conformal calibration reuses grouped out-of-fold residuals after model selection; treat coverage as exploratory rather than confirmatory.
        - The tool does not provide investment, lending or engineering advice.
        """
    )
st.caption(f"Model version: {bundle['version']} · Target: {bundle['target']}")
