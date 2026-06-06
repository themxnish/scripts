# Multi-Threaded Port Scanner

## Overview

A Python-based multi-threaded port scanner that identifies open TCP ports on a target host, performs basic service detection, attempts banner grabbing, and provides a simple operating system guess based on discovered services and banners.

The scanner supports predefined port sets, custom ranges, and custom port lists while displaying real-time scan progress.

---

## Features

* Multi-threaded TCP port scanning with Hostname to IP resolution
* Open port detection and Service identification for common ports
* Banner grabbing for version information as well as basic operating system fingerprinting
* Risky port identification
* Customizable port ranges and lists

---

## Requirements

* Python 3.x
* Standard Python libraries only:

  * `socket`
  * `threading`
  * `concurrent.futures`
  * `datetime`

No other external dependencies are required.

---

## Scan Modes

### 1. Common Ports

Scans frequently used services such as:

FTP (21), SSH (22), HTTP (80), HTTPS (443), MySQL (3306), RDP (3389), MongoDB (27017)

### 2. Standard Range

Scans ports:

```text
1 - 1024
```

### 3. Custom Range

Specify a start and end port.

Example:

```text
1000 - 5000
```

### 4. Custom Specific Port List

Specify individual ports.

Example:

```text
22,80,443,3306
```

---

## Usage

Run the scanner:

```bash
python port_scanner.py
```

Or provide a target directly:

```bash
python port_scanner.py 192.168.1.10
```

---

## Output Information

For each open port, the scanner displays:

| Field          | Description                           |
| -------------- | ------------------------------------- |
| Port           | Open TCP port                         |
| Service        | Common service name                   |
| Banner         | Service banner or version information |
| Risk Indicator | Marks potentially exposed services    |

Example:

```text
PORT       SERVICE        BANNER/VERSION
22/tcp     SSH            OpenSSH_8.9
80/tcp     HTTP           Apache/2.4.57
3306/tcp   MySQL          MySQL Server
```

---

## Risk Detection

The scanner highlights commonly exposed or high-risk services, including:

FTP, Telnet, SMB, MSSQL, RDP, Redis, Elasticsearch, MongoDB, Docker API

This helps identify services that may require additional security review.

---

## Operating System Detection

The scanner performs basic OS fingerprinting using:

* Service banners
* Open port combinations

Possible results:

* Windows
* Linux
* Unknown

---

## Example Workflow

1. Resolve target hostname.
2. Scan selected ports using multiple threads.
3. Identify open ports.
4. Collect service banners.
5. Perform OS detection.
6. Display scan results and statistics.

---

## Disclaimer

This tool is intended for educational purposes, network administration, and authorized security assessments only.

Always obtain proper authorization before scanning systems or networks that you do not own or manage.
