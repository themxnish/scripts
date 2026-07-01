import json
from .common import empty_row

IMPORTANT_FIELDS = ["timestamp", "message"]

def parse_line(line):
    try:
        data = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None

    row = empty_row()
    
    row["timestamp"] = str(data.get("timestamp") or data.get("time") or "")
    row["ip"] = str(data.get("ip") or data.get("src_ip") or "")
    row["path"] = str(data.get("path") or data.get("url") or "")
    row["status_code"] = str(data.get("status") or data.get("status_code") or "")
    row["message"] = str(data.get("message") or data.get("msg") or "")
    return row