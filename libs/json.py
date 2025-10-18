import json
import os

def get_json(filepath) -> dict:
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf8") as f:
                dictionary = json.load(f)
        else:
            dictionary = {}
    except json.JSONDecodeError as e:
        print('[JSON] ' + e)
        dictionary = {}
    
    return dictionary

def dump_json(filepath:str, dictionary:dict):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf8") as f:
        json.dump(dictionary, f, sort_keys=True, indent=4, ensure_ascii=False)