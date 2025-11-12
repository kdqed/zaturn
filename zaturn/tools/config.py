import os
from pathlib import Path
import platformdirs

# Basic Setup
USER_DATA_DIR = Path(platformdirs.user_data_dir('zaturn', 'zaturn'))
QUERIES_DIR = USER_DATA_DIR / 'queries'
VISUALS_DIR = USER_DATA_DIR / 'visuals'
SOURCES_FILE = USER_DATA_DIR / 'sources.txt'

BIGQUERY_SERVICE_ACCOUNT_FILE = USER_DATA_DIR / 'bigquery-service-account.json'
if not os.path.exists(BIGQUERY_SERVICE_ACCOUNT_FILE):
    BIGQUERY_SERVICE_ACCOUNT_FILE = None

os.makedirs(QUERIES_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)

