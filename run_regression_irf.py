# run_regression_irf.py

import os
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
import statsmodels.api as sm
import matplotlib.pyplot as plt


def preprocess_and_construct_features(merged_panel):
    merged_panel = merged_panel.sort_values(by=["country", "year"]).copy()
    merged_panel["log_gdp_pc"] = np.log(merged_panel["gdp_per_capita"])
    merged_panel["gdp_growth"] = merged_panel.groupby("country")["log_gdp_pc"].diff()

    merged_panel = merged_panel[merged_panel["is_green"].notna()].copy()
    green = merged_panel[merged_panel["is_green"] == True].copy()
    non_green = merged_panel[merged_panel["is_green"] == False].copy()

    green_sum = green.groupby(["country", "year"])["patent_count"].sum().reset_index(name="green_patents")
    total_sum = merged_panel.groupby(["country", "year"])["patent_count"].sum().reset_index(name="total_patents")

    merged_summary = pd.merge(total_sum, green_sum, on=["country", "year"], how="left")
    merged_summary["green_share"] = merged_summary["green_patents"] / merged_summary["total_patents"]
    merged_summary["green_share"] = merged_summary["green_share"].fillna(0)

    final_df = merged_panel.merge(merged_summary, on=["country", "year"], how="left")
    final_df = final_df[(final_df["year"] >= 2006) & (final_df["year"] <= 2022)].copy()

    return final_df


def construct_log_vars(df):
    df = df.set_index(['country', 'year']).copy()

    df["green_patents"] = pd.to_numeric(df["green_patents"], errors="coerce").fillna(0)
    df["green_pc"] = df["green_patents"] / df["gdp_per_capita"]
    df["log_green"] = np.log1p(df["green_pc"])

    df["non_green_patents"] = df["total_patents"] - df["green_patents"]
    df["non_green_patents"] = df["non_green_patents"].clip(lower=0).fillna(0)
    df["non_green_pc"] = df["non_green_patents"] / df["gdp_per_capita"]
    df["log_non_green"] = np.log1p(df["non_green_pc"])

    for k in range(1, 4):
        df[f"log_green_l{k}"] = df.groupby("country")["log_green"].shift(k)
        df[f"log_non_green_l{k}"] = df.groupby("country")["log_non_green"].shift(k)
    for k in range(2, 4):
        df[f"log_gdp_l{k}"] = df.groupby("country")["log_gdp_pc"].shift(k)
    df["log_gdp_lag1"] = df.groupby("country")["log_gdp_pc"].shift(1)

    return df


def run_irf(df, patent_type):
    results = []
    var_prefix = "log_green" if patent_type == "green" else "log_non_green"

    for h in range(6):
        df[f"log_gdp_h{h}"] = df.groupby("country")["log_gdp_pc"].shift(-h)
        df[f"delta_gdp_h{h}"] = df[f"log_gdp_h{h}"] - df["log_gdp_lag1"]

        exog_vars = [
            f"{var_prefix}",
            f"{var_prefix}_l1",
            f"{var_prefix}_l2",
            f"{var_prefix}_l3",
            "log_gdp_l2", "log_gdp_l3"
        ]
        X = sm.add_constant(df[exog_vars])
        y = df[f"delta_gdp_h{h}"]

        reg_data = pd.concat([y, X], axis=1).dropna()
        y_clean = reg_data[f"delta_gdp_h{h}"]
        X_clean = reg_data[exog_vars + ['const']]

        model = PanelOLS(y_clean, X_clean, entity_effects=True, time_effects=True)
        result = model.fit(cov_type="robust")

        results.append({
            "horizon": h,
            "coef": result.params[var_prefix],
            "stderr": result.std_errors[var_prefix]
        })

    return pd.DataFrame(results)


def plot_irfs(df_green, df_non_green, save_path="fig/irf_plot.png"):
    df_green["lower"] = df_green["coef"] - 1.96 * df_green["stderr"]
    df_green["upper"] = df_green["coef"] + 1.96 * df_green["stderr"]

    df_non_green["lower"] = df_non_green["coef"] - 1.96 * df_non_green["stderr"]
    df_non_green["upper"] = df_non_green["coef"] + 1.96 * df_non_green["stderr"]

    plt.figure(figsize=(10, 6))
    plt.plot(df_green["horizon"], df_green["coef"], label="Green Patents", color="blue")
    plt.fill_between(df_green["horizon"], df_green["lower"], df_green["upper"], alpha=0.2, color="blue")

    plt.plot(df_non_green["horizon"], df_non_green["coef"], label="Non-Green Patents", color="orange")
    plt.fill_between(df_non_green["horizon"], df_non_green["lower"], df_non_green["upper"], alpha=0.2, color="orange")

    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.xlabel("Horizon (years)")
    plt.ylabel("Δ log GDP per capita")
    plt.title("Impulse Response of GDP to Green vs. Non-Green Innovation")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Create output folder if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    print("Saving to:", os.path.abspath(save_path))

    # Save figure
    plt.savefig(save_path, dpi=300)
    print(f"IRF plot saved to {save_path}")
    plt.show()
    plt.close()


# Main callable
def run_regression_irf_pipeline(merged_panel):
    final_df = preprocess_and_construct_features(merged_panel)
    df = construct_log_vars(final_df)

    df_green = run_irf(df, "green")
    df_non_green = run_irf(df, "non_green")

    plot_irfs(df_green, df_non_green, save_path="fig/irf_plot.png")

    return df_green, df_non_green