import json
import os
from pathlib import Path

import platformdirs


USER_DATA_DIR = platformdirs.user_data_dir('zaturn', 'zaturn')
STATE_FILE = Path(USER_DATA_DIR) / 'studio.json'


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.loads(f.read())
    else:
        return {}


def save_state(state: dict):
    with open(STATE_FILE, 'w') as f:
        f.write(json.dumps(state, indent=2))


def save_datafile(datafile, filename: str) -> Path:
    target_dir = Path(USER_DATA_DIR) / 'studio_data'
    os.makedirs(target_dir, exist_ok=True)

    target_path = target_dir / filename
    datafile.save(target_path)
    return target_path
    
