# Data source and attribution

ATLAS-RC uses the public U.S. data-centre project database published by Server Country.

Data pages:
- https://servercountry.org/data/
- https://servercountry.org/data/downloads/
- https://servercountry.org/data/methodology/

Server Country's requested citation is:

Bommarito, Jillian and Bommarito, Michael James, *Data Center Policy across the 50 States: A Survey of Incentives, Land Use, and Energy Regulation* (June 18, 2026). Available at SSRN: https://ssrn.com/abstract=6964278 ; DOI: 10.2139/ssrn.6964278.

Server Country states that its project database and state policy/power research are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).

## Important source limitations

Server Country states that:

- announced does not mean built
- investment figures can include multi-phase totals spanning long periods
- power capacity can refer to planned maximum rather than current operational capacity
- fields can be missing
- the database is periodically updated

For those reasons, ATLAS-RC uses the phrase **reported investment** rather than verified actual CAPEX.

## Dataset redistribution

The v1.0.0 package does not bundle `dataset.csv`. This avoids ambiguity over the exact snapshot and encourages users to retrieve the canonical source and its current attribution information directly.

To reproduce, download the CSV and save it as `dataset.csv` in the repository root.
