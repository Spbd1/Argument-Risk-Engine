import json

def safe_dump(data, sort_keys=False):
    return json.dumps(data, indent=2)

def safe_load(text):
    try:
        return json.loads(text)
    except Exception:
        return None
