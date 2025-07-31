import os
import platformdirs

# Basic Setup
USER_DATA_DIR = platformdirs.user_data_dir('zaturn', 'zaturn')
QUERIES_DIR = os.path.join(USER_DATA_DIR, 'queries')
VISUALS_DIR = os.path.join(USER_DATA_DIR, 'visuals')
SOURCES_FILE = os.path.join(USER_DATA_DIR, 'sources.txt')

os.makedirs(QUERIES_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)

