import re
from .common import empty_row

PATTERN = re.compile(
    r'^(?P<timestamp>[A-Z][a-z]{2}\s+\d{1,2}\s\d{2}:\d{2}:\d{2}) '
    r'(?P<hostname>\S+) (?P<process>[\w./-]+)(?:\[\d+\])?:\s*(?P<message>.*)$'
)
IP_PATTERN = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

IMPORTANT_FIELDS = ["timestamp", "hostname", "process", "message"]

def parse_line(line):
    match = PATTERN.match(line)
    if not match:
        return None

    d = match.groupdict()
    row = empty_row()
    row["timestamp"] = d["timestamp"]
    row["hostname"] = d["hostname"]
    row["process"] = d["process"]
    row["message"] = d["message"]

    ip_found = IP_PATTERN.search(d["message"])
    if ip_found:
        row["ip"] = ip_found.group()
    return row