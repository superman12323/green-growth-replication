# merge_country_gdp.py

import pandas as pd
import pycountry

def map_country_codes(df, raw_country_col="raw_country"):
    """
    Maps raw country codes to IMF-compatible alpha-3 codes using pycountry and manual fixes.
    Returns a DataFrame with two new columns: 'clean_country' and 'imf_country'.
    """

    # Manual overrides for raw codes
    manual_fix_map = {
        'AN': 'AN', 'CS': 'RS', 'YU': 'RS', 'SU': 'RU', 'DD': 'DE', 'DDR': 'DE',
        'UK': 'GB', 'USA': 'US',
        'JPX': 'JP', 'JPx': 'JP', 'JPS': 'JP', 'JPC': 'JP', 'JPK': 'JP',
        'FRx': 'FR', 'FRX': 'FR',
        'GB1': 'GB', 'GB2': 'GB', 'GB3': 'GB', 'GB4': 'GB',
        'DE1': 'DE', 'DE2': 'DE',
        'HKX': 'HK', 'KRX': 'KR', 'CNX': 'CN', 'TWX': 'TW',
        'ITX': 'IT', 'PLX': 'PL', 'SEx': 'SE', 'SEX': 'SE',
        'INX': 'IN', 'CHX': 'CH', 'NLX': 'NL', 'MAX': 'MX', 'MXX': 'MX', 'MXC': 'MX',
        'BRX': 'BR', 'BGX': 'BG', 'ARX': 'AR', 'ATX': 'AT', 'AUX': 'AU',
        'ZAX': 'ZA', 'NZK': 'NZ', 'NZX': 'NZ', 'ISX': 'IS', 'NOX': 'NO', 'DKX': 'DK',
        'SUX': 'RU', 'RUX': 'RU',
        'unknown': None, 's': None, 'XH': None, 'OE': None, 'CT': None
    }

    alpha2_to_alpha3 = {c.alpha_2: c.alpha_3 for c in pycountry.countries}
    alpha2_to_alpha3.update({
        'XK': 'XKX', 'AN': 'ANT', 'SU': 'SUN', 'YU': 'YUG', 'DD': 'DDR', 'CS': 'SCG'
    })

    df["clean_country"] = df[raw_country_col].replace(manual_fix_map)
    df["imf_country"] = df["clean_country"].map(alpha2_to_alpha3)

    # Print mapping status
    mapped = df[df["imf_country"].notna()]["clean_country"].unique()
    unmapped = df[df["imf_country"].isna()]["clean_country"].unique()
    print(f"Mapped countries: {len(mapped)}")
    print(f"Unmapped countries: {len(unmapped)}")

    return df


def merge_with_gdp(panel_df, gdp_df):
    """
    Merges panel patent data (with 'imf_country' and 'year') with GDP per capita data.
    Drops rows with missing GDP values.
    """
    panel_df["year"] = panel_df["year"].astype(int)
    gdp_df["year"] = gdp_df["year"].astype(int)

    merged = pd.merge(
        panel_df,
        gdp_df,
        left_on=["imf_country", "year"],
        right_on=["country", "year"],
        how="left"
    )

    merged = merged.dropna(subset=["gdp_per_capita"])
    return merged


# Optional preview
if __name__ == "__main__":
    # Replace with your real data paths or variables
    panel_final = pd.read_csv("panel_final.csv")  # cleaned patent data
    panel_df = pd.read_csv("gdp_per_capita.csv")  # GDP data

    panel_mapped = map_country_codes(panel_final)
    merged = merge_with_gdp(panel_mapped, panel_df)
    print(merged.head())