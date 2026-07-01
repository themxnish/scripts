import os, re, csv, json, hashlib, argparse
from datetime import datetime
from parsers import LINE_PARSERS, csv_parser, generic
from parsers.common import FIELDNAMES

def sha256_of_file(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if chunk == b"":
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def read_sample_lines(path, count=20):
    lines = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                lines.append(line.rstrip("\n"))
            if len(lines) >= count:
                break
    return lines

def detect_format(sample_lines):
    # Try each known parser against a sample of lines and see which one matches the most. Falls back to 'generic' if nothing fits well.
    if csv_parser.looks_like_csv(sample_lines):
        return "csv"
    if not sample_lines:
        return "generic"

    best_name, best_score = "generic", 0.0
    for name, module in LINE_PARSERS.items():
        hits = sum(1 for line in sample_lines if module.parse_line(line) is not None)
        score = hits / len(sample_lines)
        if score > best_score:
            best_name, best_score = name, score

    return best_name if best_score >= 0.5 else "generic"

def parse_line_based_file(path, filename, detected_format, all_rows):
    module = LINE_PARSERS.get(detected_format)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line_number, raw in enumerate(f, start=1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue

            row = module.parse_line(line) if module else None
            used_format = detected_format
            important_fields = module.IMPORTANT_FIELDS if module else generic_parser.IMPORTANT_FIELDS

            if row is None:
                row = generic_parser.parse_line(line)
                used_format = "generic"
                important_fields = generic_parser.IMPORTANT_FIELDS

            row["source_file"] = filename
            row["line_number"] = line_number
            row["raw_line"] = line
            row["detected_format"] = used_format

            filled = sum(1 for f in important_fields if row.get(f))
            row["confidence"] = round(filled / len(important_fields) * 100, 1)
            all_rows.append(row)

def main():
    parser = argparse.ArgumentParser(description="Parse every log file in a folder into one combined CSV.")
    parser.add_argument("--input", default="logs", help="Folder containing the log files (default: logs)")
    parser.add_argument("--output", default="output/parsed_logs.csv", help="Output CSV file path")
    parser.add_argument("--manifest", default="output/manifest.json", help="Output manifest file path")
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"Error: '{args.input}' is not a folder.")
        return

    files = sorted(
        f for f in os.listdir(args.input)
        if os.path.isfile(os.path.join(args.input, f))
    )
    if not files:
        print(f"No files found in {args.input}")
        return

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    print(f"Found {len(files)} file(s) in {args.input}\n")

    all_rows = []
    manifest = {"generated_at": datetime.now().isoformat(), "files": []}

    for filename in files:
        full_path = os.path.join(args.input, filename)
        file_hash = sha256_of_file(full_path)
        sample = read_sample_lines(full_path)
        detected_format = detect_format(sample)

        rows_before = len(all_rows)
        if detected_format == "csv":
            all_rows.extend(csv_parser.parse_file(full_path, filename))
        else:
            parse_line_based_file(full_path, filename, detected_format, all_rows)
        lines_parsed = len(all_rows) - rows_before

        print(f"  {filename:<25} format: {detected_format:<10} lines parsed: {lines_parsed}")

        manifest["files"].append({
            "file": filename,
            "sha256": file_hash,
            "detected_format": detected_format,
            "lines_parsed": lines_parsed,
        })

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    manifest["total_files"] = len(files)
    manifest["total_lines"] = len(all_rows)
    with open(args.manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    avg_confidence = (
        sum(float(r["confidence"]) for r in all_rows) / len(all_rows)
        if all_rows else 0
    )

    print(f"\nDone! Wrote {len(all_rows)} rows to {args.output}")
    print(f"Manifest (file hashes) saved to {args.manifest}")
    print(f"Average parse confidence: {avg_confidence:.1f}%")

if __name__ == "__main__":
    main()