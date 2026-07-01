FIELDNAMES = [
    "source_file", "line_number", "detected_format", "confidence",
    "timestamp", "ip", "hostname", "user", "method", "path",
    "status_code", "size", "process", "message", "raw_line",
]

def empty_row():
    return {field: "" for field in FIELDNAMES}