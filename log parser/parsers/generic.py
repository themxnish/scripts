import re
from .common import empty_row

IP_PATTERN = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
TIME_PATTERNS = [
    re.compile(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}'),       # 2026-05-21 10:00:01
    re.compile(r'\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}'),     # 21/May/2026:08:12:03
    re.compile(r'[A-Z][a-z]{2}\s+\d{1,2}\s\d{2}:\d{2}:\d{2}'),    # May 21 08:45:12
]
GENERAL_PATTERN = re.compile(r'^(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+\[(?P<timestamp>[^\]]+)\]\s+(?P<message>.+)$')

IMPORTANT_FIELDS = ["ip", "timestamp", "message"]

def parse_line(line):
    row = empty_row()

    ip_found = IP_PATTERN.search(line)
    if ip_found:
        row["ip"] = ip_found.group()

    for pattern in TIME_PATTERNS:
        time_found = pattern.search(line)
        if time_found:
            row["timestamp"] = time_found.group()
            break

    general_match = GENERAL_PATTERN.match(line)
    if general_match:
        row.update(general_match.groupdict())

    return row