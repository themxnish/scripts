import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

COMMON_SERVICES = {
    21: "FTP",       22: "SSH",       23: "Telnet",    25: "SMTP",
    53: "DNS",       67: "DHCP",      69: "TFTP",      80: "HTTP",
    110: "POP3",     111: "RPC",      135: "MSRPC",    139: "NetBIOS",
    143: "IMAP",     161: "SNMP",     389: "LDAP",     443: "HTTPS",
    445: "SMB",      465: "SMTPS",    587: "SMTP",     636: "LDAPS",
    993: "IMAPS",    995: "POP3S",    1433: "MSSQL",   1521: "Oracle",
    2375: "Docker",  3000: "Dev",     3306: "MySQL",   3389: "RDP",
    5432: "Postgres",5900: "VNC",     6379: "Redis",   8000: "HTTP-Alt",
    8080: "HTTP-Alt",8443: "HTTPS-Alt",9200: "Elastic",27017: "MongoDB",
}

RISKY_PORTS = {
    21:    "FTP sends passwords in plaintext",
    23:    "Telnet is completely unencrypted",
    135:   "MSRPC - common Windows attack surface",
    139:   "NetBIOS - legacy, often exploited",
    445:   "SMB - EternalBlue / WannaCry target",
    1433:  "MSSQL exposed to network",
    2375:  "Docker API with NO authentication",
    3306:  "MySQL exposed to network",
    3389:  "RDP - brute force target",
    4444:  "Common backdoor/Metasploit port",
    5432:  "PostgreSQL exposed to network",
    5900:  "VNC - often has weak/no password",
    6379:  "Redis - no auth by default",
    9200:  "Elasticsearch - data exposed",
    27017: "MongoDB - no auth by default",
}

def resolve_host(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Could not resolve hostname: {host}")
        return None

def scan_port(ip, port, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))

        if result == 0:
            return "open"
        else:
            return "closed"

    except socket.timeout:
        return "filtered"
    except Exception as e:
        print(f"Error scanning port {port}: {e}")
        return "filtered"

def grad_banner(ip, port, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))

        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        return banner
    except Exception as e:
        print(f"Error grabbing banner from {ip}:{port} - {e}")
        return "No banner"

def detect_os(open_ports, banners):
    banners = " ".join(banners.values()).lower()

    if "windows" in banners:
        return "Windows"
    elif "linux" in banners or "ubuntu" in banners or "debian" in banners or "centos" in banners or "red hat" in banners:
        return "Linux (Ubuntu/Debian/CentOS/Red Hat)"
    return "Unknown"
    
    ports = set(open_ports)
    if 22 in ports and (80 in ports or 443 in ports):
        return "Linux"
    elif 135 in ports and 445 in ports:
        return "Windows"
    return "Unknown"

def scan(target, ports, timeout=1, threads=200):
    print("\n" + "=" * 55)
    print("         Starting - Port Scanner")
    print("=" * 55)

    ip = resolve_host(target)
    if not ip:
        return

    print(f" Target: {target}")
    if ip != target:
        print(f" Resolved IP: {ip}")
    print(f"  Ports   : {len(ports)} ports to scan")
    print(f"  Threads : {threads}")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 55)

    open_ports = []
    start_time = datetime.now()
    lock = threading.Lock()
    scanned_ports = [0]

    def progress_bar():
        done =  scanned_ports[0]
        total = len(ports)
        percent = int((done / total) * 100) if total else 100
        bar = "#" * (percent // 2) + "-" * (50 - percent // 2)
        print(f"\r  [{bar}] {percent}% ({done}/{total})", end="", flush=True)

    def check_port(port):
        status = scan_port(ip, port, timeout)
        with lock:
            scanned_ports[0] += 1

            if scanned_ports[0] % max(1, len(ports) // 100) == 0 or scanned_ports[0] == len(ports):
                progress_bar()
        if status == "open":
            return port
        return None
    
    print("\n  Scanning ports...\n")
    progress_bar()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_port = {executor.submit(check_port, port): port for port in ports}
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            result = future.result()
            if result:
                open_ports.append(result)
    
    print()
    open_ports.sort()

    print("\n Grabbing banners from open ports...")
    banners = {}
    for port in open_ports:
        banner = grad_banner(ip, port, timeout)
        banners[port] = banner
    
    scan_time = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 55)
    print(f"  RESULTS - {len(open_ports)} open port(s) found")
    print("=" * 55)

    if not open_ports:
        print(" No open ports found.")
    else:
        print(f"  {'PORT':<10} {'SERVICE':<14} {'BANNER / VERSION'}")
        print("  " + "-" * 52)
        for port in open_ports:
            service = COMMON_SERVICES.get(port, "Unknown")
            banner = banners.get(port, "No banner")
            banner_short = banner.split("\n")[0][:45] if banner else "-"
            risk = " !" if port in RISKY_PORTS else ""

            print(f"  {str(port) + '/tcp':<10} {service:<14} {banner_short}{risk}")

    if open_ports:
        os_guess = detect_os(open_ports, banners)
        print(f"\n  OS Guess: {os_guess}")

    print(f"  Scanned  : {len(ports)} ports in {scan_time:.2f}s")
    print("=" * 55 + "\n")

if __name__ == "__main__":
    import sys

    print("\nPort Scanner")
    print("-" * 30)

    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Enter target hostname or IP: ").strip()

    print("\nSelect port range to scan:")

    print("  1. Top common ports (fast)")
    print("  2. Ports 1-1024 (standard)")
    print("  3. Custom range")
    print("  4. Custom list (e.g. 22,80,443)")

    choice = input("\nChoice [1-4]: ").strip()

    if choice == "1":
        ports = list(COMMON_SERVICES.keys())
    elif choice == "2":
        ports = list(range(1, 1025))
    elif choice == "3":
        start_port = int(input("Start port: ").strip())
        end_port = int(input("End port: ").strip())
        ports = list(range(start_port, end_port + 1))
    elif choice == "4":
        port_input = input("Enter ports (comma-separated): ").strip()
        ports = [int(p.strip()) for p in port_input.split(",") if p.strip().isdigit()]

    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    timeout = 10
    print(f"\nUsing timeout of {timeout} seconds for each port scan.")
    scan(target, ports, timeout=timeout)