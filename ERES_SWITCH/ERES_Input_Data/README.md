# ERES input data

`global-input-bundle-v2` contains the complete SWITCH input bundle for
the CN, EU, and IN simulations reported in the article.

The bundle provides 27 scenario profiles:

- regions: `CN`, `EU`, and `IN`;
- ERES cases: `BR`, `HR`, and `NR`;
- technology cases: `A`, `C`, and `M`.

Each profile is combined with its registered carbon cases through
`scenario_manifest.csv`, giving 315 materializable simulations.

There are nine `storage_energy_limits.csv` files, one for each region
and ERES-case combination. Profile-specific generation data are stored
under `regions/<region>/profiles/<scenario-profile>`.

Do not edit this folder. Select inputs through `run_eres.py` in the
sibling `ERES_SWITCH_Model` folder.
