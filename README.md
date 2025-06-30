### **Impulse Response Analysis: Green vs. Non-Green Innovation**

This analysis estimates the dynamic impact of green and non-green patenting on future GDP per capita using panel data regressions with fixed effects.

#### Methodology
- **Data**: Panel dataset of countries over time with patent and GDP information.
- **Approach**: For each horizon (0–5 years), we estimate how changes in green and non-green patents per capita predict GDP growth.
- **Model**: `PanelOLS` from the `linearmodels` package, controlling for:
  - Lagged innovation variables (up to 3 years)
  - Lagged GDP per capita (2 lags)
  - Country and year fixed effects
  - Robust standard errors

#### Variables
- **Green Innovation**: log of per capita green patents (`log_green`)
- **Non-Green Innovation**: log of per capita non-green patents (`log_non_green`)
- **Outcome**: Change in log GDP per capita at horizon h (`Δ log GDP_h`)

#### Output
- The impulse response functions (IRFs) for both green and non-green innovation are plotted together for comparison.
- Confidence intervals (95%) are shown as shaded regions.

This figure highlights how different types of innovation contribute to economic growth over time.
