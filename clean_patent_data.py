# clean_patent_data.py

import pandas as pd
import duckdb

def load_green_ipc_list(excel_path="combined_ipc_codes.xlsx"):
    """
    Load and clean the list of green IPC codes from an Excel file.
    """
    green_ipc_df = pd.read_excel(excel_path, header=None)
    ipc_list = (
        green_ipc_df[0]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )
    if "IPC_Codes" in ipc_list:
        ipc_list.remove("IPC_Codes")
    return ipc_list


def generate_patent_panel(con, green_ipc_list, chunk_size=1_000_000):
    """
    Process the patent_joined table in chunks to generate a panel dataset:
    [country, year, is_green, patent_count]
    """
    total_rows = con.execute("SELECT COUNT(*) FROM patent_joined").fetchone()[0]
    panel_data = pd.DataFrame(columns=["raw_country", "year", "is_green", "patent_count"])

    for start in range(0, total_rows, chunk_size):
        print(f"Processing rows {start} to {min(start + chunk_size, total_rows)}...")

        query = f"""
        SELECT raw_country, action_date, section, ipc_class, subclass, main_group, subgroup
        FROM patent_joined
        LIMIT {chunk_size} OFFSET {start}
        """
        chunk_df = con.execute(query).df()

        # Drop rows with missing country or action_date
        chunk_df = chunk_df.dropna(subset=['raw_country', 'action_date'])

        # Convert date and extract year
        chunk_df['action_date'] = pd.to_datetime(chunk_df['action_date'], errors='coerce')
        chunk_df = chunk_df.dropna(subset=['action_date'])
        chunk_df['year'] = chunk_df['action_date'].dt.year

        # Construct full IPC code
        chunk_df['ipc_code_full'] = (
            chunk_df['section'].fillna('') +
            chunk_df['ipc_class'].fillna('') +
            chunk_df['subclass'].fillna('') +
            chunk_df['main_group'].fillna('') + '/' +
            chunk_df['subgroup'].fillna('')
        )

        # Identify green patents
        chunk_df['is_green'] = chunk_df['ipc_code_full'].isin(green_ipc_list)

        # Aggregate by country, year, and green status
        grouped = (
            chunk_df
            .groupby(['raw_country', 'year', 'is_green'])
            .size()
            .reset_index(name='patent_count')
        )

        panel_data = pd.concat([panel_data, grouped], ignore_index=True)

    # Final aggregation
    panel_final = panel_data.groupby(['raw_country', 'year', 'is_green'], as_index=False)['patent_count'].sum()
    return panel_final


# Optional direct run
if __name__ == "__main__":
    con = duckdb.connect("patentsview.ddb")
    con.execute("SET enable_progress_bar = false;")
    green_ipc_list = load_green_ipc_list()
    panel_df = generate_patent_panel(con, green_ipc_list)
    print(panel_df.head())