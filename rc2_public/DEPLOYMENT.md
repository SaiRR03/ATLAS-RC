# Deployment for public trials

The canonical public trial runs from:

https://github.com/SaiRR03/ATLAS-RC

## One-click Render deployment

Open:

https://render.com/deploy?repo=https://github.com/SaiRR03/ATLAS-RC

Render reads the root `render.yaml`, uses `rc2_public/` as the application root, installs the Python dependencies and starts Streamlit on `0.0.0.0:$PORT`. After the deployment completes, Render provides a public `onrender.com` URL suitable for LinkedIn trials.

## Public description

Describe the application as an **ATLAS-RC2 public research demonstrator for probabilistic benchmarking of publicly reported US data-centre investment**.

Do not describe it as a construction-cost estimator, an investment-grade estimate or a reproduction of the frozen original Jupyter experiment. The public app uses a separately reconstructed 346-row modelling population and grouped validation, while the original Jupyter RC2 experiment used 263 screened observations split 151 development / 60 calibration / 52 test.

Treat every output as a research benchmark, not a detailed cost estimate, lending decision or investment recommendation.
