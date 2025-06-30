# load_patent_data.py

from zipfile import ZipFile
from urllib.request import urlretrieve
import tempfile
import os
import duckdb

# ------------------------------
# 1. Download & Extract Zip File
# ------------------------------

def extract_from_url(zipfile_url: str, filename: str, dir: str = ".", overwrite: bool = False):
    """
    Download and extract a single file from a zipped URL.
    
    Args:
        zipfile_url: URL to download the zip archive.
        filename: Name of the file inside the zip archive to extract.
        dir: Target directory for the extracted file.
        overwrite: Whether to overwrite existing file.
    
    Returns:
        Path to the extracted file.
    """
    filepath = os.path.join(dir, filename)
    if overwrite or not os.path.exists(filepath):
        with tempfile.NamedTemporaryFile() as zipped:
            urlretrieve(zipfile_url, zipped.name)
            with ZipFile(zipped) as zipfile:
                zipfile.extract(filename, path=dir)

    return filepath

# List of PatentsView tables to download
tables = [
    "g_patent",
    "g_location_not_disambiguated",
    "g_assignee_not_disambiguated",
    "g_ipc_at_issue"
]

def download_tables(tables):
    """
    Download and extract specified TSV tables from PatentsView.
    """
    base_url = "https://s3.amazonaws.com/data.patentsview.org/download"
    for table in tables:
        download_url = f"{base_url}/{table}.tsv.zip"
        filename = f"{table}.tsv"
        extract_from_url(download_url, filename)

# Download the required tables
download_tables(tables)

# ------------------------------
# 2. Load into DuckDB
# ------------------------------

# Connect to DuckDB and suppress progress bars
con = duckdb.connect("patentsview.ddb")
con.execute("SET enable_progress_bar = false;")

def list_tables(con: duckdb.DuckDBPyConnection):
    """
    Return a list of existing DuckDB table names.
    """
    return [row[0] for row in con.execute("SHOW TABLES").fetchall()]

def create_tables_if_not_exist(con, tables):
    """
    Create DuckDB tables from local TSV files if they do not already exist.
    """
    for table in tables:
        if table not in list_tables(con):
            con.read_csv(
                f"{table}.tsv",
                delimiter="\t",
                quotechar='"',
                escapechar='"',
                all_varchar=True
            ).create(table)

# Create tables if needed
create_tables_if_not_exist(con, tables)

# ------------------------------
# 3. Join and Preview Tables
# ------------------------------

# Load each DuckDB table
g_patent = con.table("g_patent")
g_location_not_disambiguated = con.table("g_location_not_disambiguated")
g_assignee_not_disambiguated = con.table("g_assignee_not_disambiguated")
g_ipc_at_issue = con.table("g_ipc_at_issue")

# Join patent-assignee-location-ipc tables
patent_joined = (
    g_patent
    .join(g_assignee_not_disambiguated, "patent_id", how="left")
    .join(g_location_not_disambiguated, "rawlocation_id", how="left")
    .join(g_ipc_at_issue, "patent_id", how="left")
)
con.execute("""
CREATE OR REPLACE VIEW patent_joined AS
SELECT *
FROM g_patent AS p
LEFT JOIN g_assignee_not_disambiguated AS a ON p.patent_id = a.patent_id
LEFT JOIN g_location_not_disambiguated AS l ON a.rawlocation_id = l.rawlocation_id
LEFT JOIN g_ipc_at_issue AS i ON p.patent_id = i.patent_id
""")

# Optional: print column names for inspection
print(patent_joined.limit(1).df().columns)