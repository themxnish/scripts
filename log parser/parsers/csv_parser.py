import csv
from .common import empty_row

def looks_like_csv(sample_lines):
    if len(sample_lines) < 2:
        return False
    try:
        dialect = csv.Sniffer().sniff("\n".join(sample_lines[:5]), delimiters=",;")
    except csv.Error:
        return False

    rows = list(csv.reader(sample_lines, dialect))
    if not rows or len(rows[0]) < 2:
        return False
    return all(len(r) == len(rows[0]) for r in rows[1:])

def parse_file(path, filename):
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for line_number, csv_row in enumerate(reader, start=2):
            row = empty_row()
            row["source_file"] = filename
            row["line_number"] = line_number
            row["detected_format"] = "csv"
            row["raw_line"] = ",".join(str(v) for v in csv_row.values())

            lower_keys = {k.lower().strip(): v for k, v in csv_row.items() if k}
            for field in ["timestamp", "ip", "user", "status_code", "message"]:
                if field in lower_keys:
                    row[field] = lower_keys[field]
            if not row["status_code"] and "status" in lower_keys:
                row["status_code"] = lower_keys["status"]

            filled = sum(1 for f in ["timestamp", "ip", "message"] if row[f])
            row["confidence"] = round(filled / 3 * 100, 1) if filled else 40.0
            rows.append(row)
    return rows