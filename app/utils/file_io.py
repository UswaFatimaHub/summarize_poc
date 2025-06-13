import os
import pandas as pd
import json

def read_csv_file(path: str):
    return pd.read_csv(path)

def save_json_file(filename: str, data: dict):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json_file(filename: str):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def delete_existing_file(filename: str):
    filepath = os.path.join("uploads", filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
