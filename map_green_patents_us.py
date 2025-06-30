import pandas as pd
import duckdb
import plotly.express as px

def generate_us_green_patent_map(con):
    # Load green IPC code list
    green_ipc_df = pd.read_excel("combined_ipc_codes.xlsx", header=None)
    green_ipc_list = green_ipc_df[0].dropna().astype(str).str.strip().tolist()
    if 'IPC_Codes' in green_ipc_list:
        green_ipc_list.remove('IPC_Codes')

    # Initialize empty DataFrame to store chunks
    panel_data_partial = pd.DataFrame(columns=["raw_state", "year", "is_green", "patent_count"])
    chunk_size = 1_000_000
    total_rows = con.execute("SELECT COUNT(*) FROM patent_joined WHERE raw_country = 'US'").fetchone()[0]

    for start in range(0, total_rows, chunk_size):
        print(f"Processing rows {start} to {start + chunk_size}...")

        query = f"""
        SELECT raw_state, action_date, section, ipc_class, subclass, main_group, subgroup
        FROM patent_joined
        WHERE raw_country = 'US'
        LIMIT {chunk_size} OFFSET {start}
        """
        chunk_df = con.execute(query).df()
        chunk_df = chunk_df.dropna(subset=['raw_state', 'action_date'])
        chunk_df['action_date'] = pd.to_datetime(chunk_df['action_date'], errors='coerce')
        chunk_df = chunk_df.dropna(subset=['action_date'])
        chunk_df['year'] = chunk_df['action_date'].dt.year

        chunk_df['ipc_code_full'] = (
            chunk_df['section'].fillna('') +
            chunk_df['ipc_class'].fillna('') +
            chunk_df['subclass'].fillna('') +
            chunk_df['main_group'].fillna('') + '/' +
            chunk_df['subgroup'].fillna('')
        )

        chunk_df['is_green'] = chunk_df['ipc_code_full'].isin(green_ipc_list)

        grouped = (
            chunk_df
            .groupby(['raw_state', 'year', 'is_green'])
            .size()
            .reset_index(name='patent_count')
        )

        panel_data_partial = pd.concat([panel_data_partial, grouped], ignore_index=True)

    # Aggregate green patents from 2006–2022
    panel_final = (
        panel_data_partial
        .groupby(['raw_state', 'year', 'is_green'], as_index=False)['patent_count'].sum()
    )
    green_us = panel_final[(panel_final["is_green"]) & (panel_final["year"].between(2006, 2022))]
    state_green_counts = green_us.groupby("raw_state")["patent_count"].sum().reset_index()

    # State abbreviation mapping
    state_abbreviation_to_name = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
        "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
        "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
        "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
        "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
        "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
        "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
        "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
        "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
        "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
    }
    state_green_counts["state_name"] = state_green_counts["raw_state"].map(state_abbreviation_to_name)

    # Create bins
    bins = [0, 100, 300, 600, 900, 1200, 1500, 3000, 6000, 10000, 18000]
    labels = [f"{bins[i]}–{bins[i+1]}" for i in range(len(bins) - 1)]
    state_green_counts["patent_bin"] = pd.cut(
        state_green_counts["patent_count"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    # Plot using Plotly
    fig = px.choropleth(
        state_green_counts,
        locations="raw_state",
        locationmode="USA-states",
        color="patent_bin",
        hover_name="state_name",
        color_discrete_sequence=px.colors.sequential.Blues,
        scope="usa",
        title="Green Patents by U.S. State (2006–2022)"
    )

    fig.update_layout(
        legend_title_text="Patent Count Range",
        legend=dict(
            title_font=dict(size=14),
            font=dict(size=12),
            yanchor="middle",
            y=0.5
        ),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    fig.show()