### **Impulse Response Analysis: Green vs. Non-Green Innovation**

This analysis estimates the dynamic impact of green and non-green patenting on future GDP per capita using panel data regressions with fixed effects.

#### Methodology
## Data Sources

This project integrates data from the following three sources:

1. [PatentsView - Patents and Assignees (via pastat)](https://github.com/PatentsView/PatentsView-Code-Examples/tree/ce759fccc9f1f43e8fce333369fab7149b9480a4):  
   Contains cleaned and structured patent data including assignees, locations, and IPC classifications.

2. [IMF - GDP per Capita Data](https://www.imf.org/en/Data):  
   Provides macroeconomic indicators such as GDP per capita for each country and year.

3. [Green Patent IPC Codes](https://github.com/shuangchenfinance/greenpatent/tree/main):  
   A manually compiled Excel file listing International Patent Classification (IPC) codes associated with green technologies.
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
