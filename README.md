# **Green Innovation and Economic Growth: Replication Study**

## **1. What I Did**

I replicated the main results of the IMF Working Paper:  
[**The Drivers and Macroeconomic Impacts of Low-Carbon Innovation: A Cross-Country Exploration**](https://www.imf.org/en/Publications/WP/Issues/2025/06/27/The-Drivers-and-Macroeconomic-Impacts-of-Low-Carbon-Innovation-A-Cross-Country-Exploration-568142)  
by Zeina Hasna, Henry Hatton, Florence Jaumotte, Jaden Kim, Kamiar Mohaddes, and Samuel Pienknagura.

This project reconstructs their core empirical analysis using global patent data and GDP per capita from 2006 to 2022, with a specific focus on comparing the effects of green vs. non-green technological innovation on economic growth.

---

## **2. Data Sources**

This project integrates data from the following three sources:

- [**PatentsView - Patents and Assignees (via pastat)**](https://github.com/PatentsView/PatentsView-Code-Examples/tree/ce759fccc9f1f43e8fce333369fab7149b9480a4):  
  Contains cleaned and structured patent-level data including assignees, locations, and IPC classifications.

- [**IMF - GDP per Capita Data**](https://www.imf.org/en/Data):  
  Provides macroeconomic indicators such as GDP per capita by country and year.

- [**Green Patent IPC Codes**](https://github.com/shuangchenfinance/greenpatent/tree/main):  
  A manually compiled Excel file listing IPC codes associated with green technologies.

---

## **3. Python Scripts and Their Roles**

- [**main.ipynb**](./main.ipynb): Runs the entire analysis pipeline and produces the main regression outputs.  
- [**load_patent_data.py**](./load_patent_data.py): Loads and joins raw PatentsView data using DuckDB.  
- [**clean_patent_data.py**](./clean_patent_data.py): Identifies green patents and constructs a panel dataset by country and year.  
- [**map_green_patents_us.py**](./map_green_patents_us.py): Visualizes the geographic distribution of green patents across U.S. states.  
- [**merge_country_gdp.py**](./merge_country_gdp.py): Harmonizes country names and merges patent data with IMF GDP per capita data.  
- [**run_regression_irf.py**](./run_regression_irf.py): Builds features and runs panel regressions to estimate impulse response functions (IRFs) of GDP growth.

---

## **4. Output Figures**

- **`map.png`**  
  A **static PNG snapshot** of the interactive Plotly map showing the number of green patents by U.S. state.  
  **To view the interactive version**, please run [`main.ipynb`](./main.ipynb) locally — the map includes zoom and hover capabilities.

- **`irf_plot.png`**  
  Displays impulse response functions of GDP per capita to green and non-green innovation (0–5 year horizons), replicating the main finding of the IMF paper.

---

To reproduce this analysis, ensure your environment includes required dependencies such as `pandas`, `duckdb`, `linearmodels`, `plotly`, and `matplotlib`, and that you have access to the `patentsview.ddb` local DuckDB file.
