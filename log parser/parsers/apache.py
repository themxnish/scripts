import re
from .common import empty_row

PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]+" (?P<status>\d{3}) (?P<size>\S+)'
)

IMPORTANT_FIELDS = ["ip", "timestamp", "method", "path", "status_code"]

def parse_line(line):
    """Returns a filled-in row, or None if this line isn't an Apache/Nginx line."""
    match = PATTERN.match(line)
    if not match:
        return None

    d = match.groupdict()
    row = empty_row()
    row["ip"] = d["ip"]
    row["user"] = "" if d["user"] == "-" else d["user"]
    row["timestamp"] = d["timestamp"]
    row["method"] = d["method"]
    row["path"] = d["path"]
    row["status_code"] = d["status"]
    row["size"] = "" if d["size"] == "-" else d["size"]
    return row