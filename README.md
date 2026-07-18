# 🔍 wp2shell - WordPress CVE-2026-63030 Vulnerability Scanner & Exploit

<p align="center">
  <img src="https://img.shields.io/badge/WordPress-Vulnerability%20Scanner-red?style=for-the-badge&logo=wordpress"/>
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/CVE-2026--63030-critical?style=for-the-badge"/>
</p>

<p align="center">
  <b>⚡ Fast, Real-time Vulnerability Scanner & Exploit for CVE-2026-63030 (wp2shell)</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen"/>
  <img src="https://img.shields.io/badge/Version-1.0-blue"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen"/>
</p>

---

## 📌 Overview

**wp2shell** is a comprehensive toolkit for detecting and exploiting **CVE-2026-63030**, a critical vulnerability in WordPress that allows unauthenticated attackers to execute remote code via REST API batch route confusion combined with SQL injection.

### 🔍 What is CVE-2026-63030?

CVE-2026-63030 (wp2shell) is a critical vulnerability discovered by **Adam Kues** (Assetnote / Searchlight Cyber) that affects WordPress core. It combines two bugs:

1. **GHSA-ff9f-jf42-662q** - REST Batch Route Confusion
2. **GHSA-fpp7-x2x2-2mjf** - `author__not_in` SQL Injection

### 📊 Affected Versions

| Version Range | Impact | Status |
|---------------|--------|--------|
| 6.9.0 - 6.9.4 | 🔴 RCE (Critical) | ❌ Vulnerable |
| 7.0.0 - 7.0.1 | 🔴 RCE (Critical) | ❌ Vulnerable |
| 6.8.0 - 6.8.5 | 🟡 SQLi (High) | ❌ Vulnerable |
| 6.9.5+ / 7.0.2+ | ✅ Patched | ✅ Safe |

---

## 📁 Repository Structure

```bash
wp2shell/
│
├── 📄 wp2shell_scanner.py          # 🔍 Fast multi-threaded scanner
├── 📄 wp2shell_intooutfile.py      # 📂 INTO OUTFILE exploit variant
│
├── 📋 list.txt                     # Example target list
├── 📊 results.txt                  # Scan results output
│
└── 📖 README.md                    # Documentation
🛠️ Tools Included
1️⃣ wp2shell_scanner.py - Fast Scanner
Multi-threaded real-time scanner for large-scale vulnerability detection.

bash
# Basic scan
python wp2shell_scanner.py -f list.txt -o results.txt

# Skip SQLi test (faster)
python wp2shell_scanner.py -f list.txt -o results.txt --no-sqli-test

# JSON output
python wp2shell_scanner.py -f list.txt -j
2️⃣ wp2shell_intooutfile.py - INTO OUTFILE Exploit
Demonstrates the INTO OUTFILE RCE variant (requires MySQL FILE privilege).

bash
# Single target
python3 wp2shell_intooutfile.py https://target.com

# Multiple targets
python3 wp2shell_intooutfile.py -f list.txt -t 10
✨ Features
<table> <tr> <td>🚀 <b>Multi-threading</b></td> <td>Scan hundreds of targets simultaneously</td> </tr> <tr> <td>📊 <b>Real-time Output</b></td> <td>Results appear instantly as they're discovered</td> </tr> <tr> <td>🎨 <b>Color-coded Results</b></td> <td>Easy-to-read output with risk levels</td> </tr> <tr> <td>💾 <b>Save Vulnerable URLs</b></td> <td>Export only vulnerable sites to a file</td> </tr> <tr> <td>🔬 <b>SQLi Detection</b></td> <td>Optional time-based SQL injection testing</td> </tr> <tr> <td>🌐 <b>Smart Protocol Detection</b></td> <td>Auto-adds <code>https://</code> if missing</td> </tr> <tr> <td>📋 <b>Batch File Support</b></td> <td>Scan from a list of targets</td> </tr> <tr> <td>🛡️ <b>Non-destructive</b></td> <td>Safe scanning - no exploitation</td> </tr> </table>
📸 Screenshot
bash
              ___      __       ____
 _    _____  |_  |___ / /  ___ / / /
| |/|/ / _ \/ __/(_-</ _ \/ -_) / / 
|__,__/ .__/____/___/_//_/\__/_/_/  
     /_/                            

  wp2shell Scanner | Target: 100 | Threads: 10
  ============================================================

================================================================================
wp2shell Exposure Check Results (REAL-TIME)
================================================================================
example.com                               [HIGH] VULNERABLE (by version) - RCE (CRITICAL)
                                             Version: v6.9.4  |  Batch: [YES]  |  SQLi: NO
                                             Endpoint: standard (status 400)
--------------------------------------------------------------------------------
example2.com                              [LOW] NOT AFFECTED - Safe
                                             Version: v7.0.2  |  Batch: [YES]  |  SQLi: NO
                                             Endpoint: standard (status 400)
--------------------------------------------------------------------------------
example3.com                              [ERROR] 'risk'
--------------------------------------------------------------------------------
🚀 Installation
📦 Clone & Setup
bash
# Clone repository
git clone https://github.com/Lutfifakee-Project/wp2shell.git
cd wp2shell

# No dependencies required - uses Python standard library only!
# Python 3.7+ required
🔧 Requirements
Requirement	Version
Python	3.7+
Operating System	Windows / Linux / macOS
Dependencies	None (standard library only)
📖 Detailed Usage
Scanner Mode (wp2shell_scanner.py)
bash
# Scan a single target
python wp2shell_scanner.py https://example.com

# Scan multiple targets
python wp2shell_scanner.py https://target1.com https://target2.com

# Scan from a file
python wp2shell_scanner.py -f targets.txt

# Scan and save vulnerable URLs only
python wp2shell_scanner.py -f targets.txt -o vulnerable.txt
Scanner Options
Option	Description
-f, --file	File with target list (one per line)
-o, --output	Save ONLY vulnerable URLs to file
-t, --threads	Number of threads (default: 10)
--timeout	Request timeout (default: 15s)
--no-sqli-test	Skip SQLi test for faster scanning
-j, --json	Output as JSON
Exploit Mode (wp2shell_intooutfile.py)
bash
# Single target
python wp2shell_intooutfile.py https://target.com

# Multiple targets from file
python wp2shell_intooutfile.py -f targets.txt

# With custom threads and timeout
python wp2shell_intooutfile.py -f targets.txt -t 10 --timeout 30

# Save results to file
python wp2shell_intooutfile.py -f targets.txt -o results.txt
📊 Output
Color Legend
Color	Risk Level	Description
🔴 HIGH	Critical	RCE vulnerability detected
🟡 MEDIUM	Medium	Version affected but batch inactive
🟢 LOW	Safe	Not affected / Patched
⚪ UNKNOWN	Unknown	WordPress not detected
Output Fields
Field	Description
Version	Detected WordPress version
Batch	[YES] = endpoint active / [NO] = inactive
SQLi	Time-based SQL injection test result
Endpoint	Batch endpoint used (standard/alternate)
File Output (-o results.txt)
The output file contains only vulnerable URLs (one per line):

txt
example.com
example2.com
example3.com
🛡️ Detection Methods
1️⃣ Version Detection
The scanner detects WordPress version using three methods:

Meta generator tag in HTML

readme.html file

wp-includes/version.php file

2️⃣ Batch Endpoint Detection
Checks both possible batch endpoints:

/wp-json/batch/v1 (standard)

/?rest_route=/batch/v1 (alternate)

3️⃣ SQL Injection Test (Optional)
Performs time-based SQL injection detection using SLEEP(3) payload.

🔬 How It Works







Risk Assessment Logic
text
If SQLi confirmed:
    → [HIGH] VULNERABLE - SQLi CONFIRMED

Elif RCE version and batch active:
    → [HIGH] VULNERABLE (by version) - RCE (CRITICAL)

Elif RCE version and batch inactive:
    → [MEDIUM] VERSION AFFECTED - Batch endpoint not active

Elif SQLi version and batch active:
    → [HIGH] VULNERABLE (by version) - SQLi (HIGH)

Elif SQLi version and batch inactive:
    → [MEDIUM] VERSION AFFECTED - Batch endpoint not active

Elif WordPress detected:
    → [LOW] NOT AFFECTED - Safe

Else:
    → [UNKNOWN] WORDPRESS NOT DETECTED
📊 Example Output
Terminal Output
text
================================================================================
wp2shell Exposure Check Results (REAL-TIME)
================================================================================
example.com                               [HIGH] VULNERABLE (by version) - RCE (CRITICAL)
                                             Version: v6.9.4  |  Batch: [YES]  |  SQLi: NO
                                             Endpoint: standard (status 400)
--------------------------------------------------------------------------------
example2.com                              [LOW] NOT AFFECTED - Safe
                                             Version: v7.0.2  |  Batch: [YES]  |  SQLi: NO
                                             Endpoint: standard (status 400)
--------------------------------------------------------------------------------
example3.com                              [ERROR] 'risk'
--------------------------------------------------------------------------------

Scan completed: 100 target(s) processed.
Vulnerable: 36
JSON Output (-j)
json
[
  {
    "host": "example.com",
    "version": "6.9.4",
    "batch_route": true,
    "batch_endpoint": "standard",
    "batch_status": 400,
    "verdict": "VULNERABLE (by version) - RCE (CRITICAL)",
    "risk": "HIGH",
    "sqli_confirmed": false,
    "sqli_delay": 0,
    "vulnerable": true
  }
]
⚡ Performance Tips
Tip	Description
Increase Threads	Use -t 20 for faster scanning (default: 10)
Skip SQLi Test	Use --no-sqli-test for ~3x faster scanning
Increase Timeout	Use --timeout 30 for slow targets
Batch File	Use -f for large-scale scanning
🎯 Use Cases
✅ Security Audits - Identify vulnerable WordPress sites in your infrastructure

✅ Bug Bounty - Quickly scan large number of targets

✅ Research - Study CVE-2026-63030 impact on live sites

✅ Compliance - Verify patching status across multiple sites

🛡️ Vulnerability Chain Explained
Stage 1: Batch Route Confusion
text
Outer: [ "http://" , POST /wp/v2/posts (body=inner) , /batch/v1 ]
     ↓
Misaligned $matches → sub-request dispatched to wrong handler
     ↓
Recursive batch call → inner requests can use GET
Stage 2: SQL Injection
text
Inner: [ "http://" , POST /wp/v2/categories?author_exclude=<SQLi> , GET /wp/v2/posts ]
     ↓
categories → posts handler (misaligned)
     ↓
author_exclude unsanitized → SQL Injection
Stage 3: Impact
text
SQL Injection → Data Exposure / Hash Extraction → Potential RCE
🔑 Hash Cracking Reference
WordPress Hash Formats
Format	Prefix	Hashcat Mode	Speed
phpass (old)	$P$B	400	⚡ Fast
bcrypt (new)	$wp$2y$10$	2612 / 3200	🐢 Slow
Cracking Commands
bash
# phpass (fast)
hashcat -m 400 -a 0 hash.txt rockyou.txt

# bcrypt (slow - use GPU)
hashcat -m 2612 -a 0 hash.txt rockyou.txt

# Using john
john --format=phpass hash.txt --wordlist=rockyou.txt
📚 Example Target File (list.txt)
txt
https://example1.com
https://example2.com
example3.com  # Will auto-add https://
https://example4.com
⚠️ Legal Disclaimer
IMPORTANT: This tool is for educational and authorized testing purposes only.

Only use on systems you own or have explicit written permission to test.

Unauthorized access to computer systems is illegal.

The developers assume no responsibility for misuse of this software.

Use responsibly and ethically.

📚 References
CVE-2026-63030

Assetnote Research

WordPress Security Advisory
