import json


def render_json_report(result):
    return json.dumps(result, indent=2)
