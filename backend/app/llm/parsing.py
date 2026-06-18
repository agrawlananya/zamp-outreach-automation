import json
import re

_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def parse_json_response(text: str):
    cleaned = text.strip()
    match = _CODE_FENCE_RE.search(cleaned)
    if match:
        cleaned = match.group(1).strip()
    return json.loads(cleaned)
