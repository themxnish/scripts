# Log Parser Tool

## Overview

A Python-based log parsing utility that scans a folder of log files, detects common log formats, extracts useful fields, and combines all parsed records into one structured CSV file. The tool also creates a manifest file with file hashes, detected formats, and parsed line counts for simple audit tracking.

---

## Features

* Automatic log format detection from sample lines
* Supports Apache/Nginx access logs, syslog, JSON lines, CSV exports, and generic text logs
* Combines multiple input files into one normalized CSV output
* Preserves source filename, line number, raw log line, and detected format
* Calculates parse confidence for each parsed row
* Generates a JSON manifest with SHA-256 hashes for input files

---

## Requirements

* Python 3.x
* Standard Python libraries only:

  * `argparse`
  * `csv`
  * `hashlib`
  * `json`
  * `os`
  * `re`
  * `datetime`

No external dependencies are required.

---

## Supported Log Formats

### 1. Apache/Nginx Access Logs

Parses common web access log fields such as:

* IP address
* User
* Timestamp
* HTTP method
* Request path
* Status code
* Response size

### 2. Syslog

Parses Linux-style syslog entries with:

* Timestamp
* Hostname
* Process name
* Message
* IP address from message text when available

### 3. JSON Lines

Parses one JSON object per line and extracts known fields such as:

* `timestamp` or `time`
* `ip` or `src_ip`
* `path` or `url`
* `status` or `status_code`
* `message` or `msg`

### 4. CSV Logs

Parses CSV files with headers and maps known columns into the normalized output schema.

Recognized columns include:

```text
timestamp, ip, user, status, status_code, message
```

### 5. Generic Logs

Falls back to a generic parser when a file does not match a known format.

The generic parser attempts to extract:

* IP addresses
* Common timestamp formats
* Message text when the line follows a recognizable pattern

---

## Folder Structure

```text
log parser/
|-- logs/
|   |-- apache_access.log
|   |-- app_events.json
|   |-- auth.syslog
|   `-- firewall_export.csv
|-- output/
|   |-- manifest.json
|   `-- parsed_logs.csv
|-- parsers/
|   |-- apache.py
|   |-- common.py
|   |-- csv_parser.py
|   |-- generic.py
|   |-- json.py
|   `-- syslog.py
`-- main.py
```

---

## Usage

Run the parser with default folders:

```bash
python main.py
```

By default, this reads from:

```text
logs
```

And writes to:

```text
output/parsed_logs.csv
output/manifest.json
```

---

## Custom Input and Output

Specify a custom input folder:

```bash
python main.py --input logs
```

Specify a custom output CSV:

```bash
python main.py --output output/parsed_logs.csv
```

Specify a custom manifest path:

```bash
python main.py --manifest output/manifest.json
```

Example with all options:

```bash
python main.py --input logs --output output/parsed_logs.csv --manifest output/manifest.json
```

---

## Output CSV Fields

The combined CSV uses a normalized schema:

| Field           | Description                                  |
| --------------- | -------------------------------------------- |
| source_file     | Original log file name                       |
| line_number     | Line number from the source file             |
| detected_format | Parser used for the row                      |
| confidence      | Parse confidence percentage                  |
| timestamp       | Extracted event timestamp                    |
| ip              | Extracted IP address                         |
| hostname        | Hostname from syslog-style entries           |
| user            | User value when available                    |
| method          | HTTP method for web logs                     |
| path            | Request path or URL                          |
| status_code     | HTTP or event status code                    |
| size            | Response size from web access logs           |
| process         | Process name from syslog entries             |
| message         | Extracted log message                        |
| raw_line        | Original unmodified log line                 |

---

## Manifest File

The manifest is written as JSON and includes:

* Generation timestamp
* Input file name
* SHA-256 hash for each file
* Detected log format
* Number of parsed lines
* Total files processed
* Total lines parsed

Example:

```json
{
  "generated_at": "2026-07-01T20:56:00",
  "files": [
    {
      "file": "apache_access.log",
      "sha256": "file_hash_here",
      "detected_format": "apache",
      "lines_parsed": 10
    }
  ],
  "total_files": 1,
  "total_lines": 10
}
```

---

## Example Output

When the parser runs successfully, it prints a summary similar to:

```text
Found 4 file(s) in logs

  apache_access.log         format: apache     lines parsed: 10
  app_events.json           format: json       lines parsed: 8
  auth.syslog               format: syslog     lines parsed: 7
  firewall_export.csv       format: csv        lines parsed: 5

Done! Wrote 30 rows to output/parsed_logs.csv
Manifest (file hashes) saved to output/manifest.json
Average parse confidence: 83.4%
```

---

## Workflow

1. Read all files from the input folder.
2. Generate a SHA-256 hash for each source file.
3. Sample the first non-empty lines from each file.
4. Detect the most likely log format.
5. Parse each line using the matching parser.
6. Fall back to the generic parser when needed.
7. Write all parsed rows to one CSV file.
8. Save a manifest with file metadata and parse totals.
9. Display a final summary with average parse confidence.

---

## Use Case

Ideal for:

* Combining logs from different systems
* Converting raw logs into spreadsheet-friendly CSV data
* Security event review and investigation
* Basic log normalization before analysis
* Building parser examples for Apache, syslog, JSON, CSV, and generic logs
