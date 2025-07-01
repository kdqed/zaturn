from datetime import datetime
import json
import os
from pathlib import Path
import urllib.parse


import platformdirs
from slugify import slugify


USER_DATA_DIR = Path(platformdirs.user_data_dir('zaturn', 'zaturn'))
STATE_FILE = USER_DATA_DIR / 'studio.json'
CHATS_DIR = USER_DATA_DIR / 'chats'
os.makedirs(CHATS_DIR, exist_ok=True)


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.loads(f.read())
            state['sources'] = state.get('sources', {})
            return state
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


def remove_datafile(filepath):
    if filepath.startswith("sqlite:///"):
        filepath = filepath.replace("sqlite:///", "")
    os.remove(filepath)


def create_chat(question: str):
    slug = slugify(question[:20]).strip("-")
    slug += '-' + str(hex(int(datetime.now().timestamp() * 1000000)))[2:]
    
    chat = {
        'slug': slug,
        'messages': [{
            'role': 'user',
            'content': question,
        }]
    }
    
    filename = CHATS_DIR / f'{slug}.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(chat, indent=2))
        
    return slug


def load_chat(slug: str):
    try:
        with open(CHATS_DIR / f'{slug}.json') as f:
            return json.loads(f.read())
    except:
        return None


def save_chat(slug: str, chat: dict):
    filename = CHATS_DIR / f'{slug}.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(chat, indent=2))


def list_chats():
    return sorted(
        [Path(f).stem for f in os.listdir(CHATS_DIR)],
        key = lambda stem: os.path.getctime(CHATS_DIR / f'{stem}.json'),
    )[::-1]
