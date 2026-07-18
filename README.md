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


---
## 📦 Clone & Setup
```bash
# Clone repository
git clone https://github.com/Lutfifakee-Project/wp2shell.git
cd wp2shell

# No dependencies required - uses Python standard library only!
# Python 3.7+ required
```

## 🛠️ Tools Included

### **wp2shell_scanner.py** - Fast Scanner

Multi-threaded real-time scanner for large-scale vulnerability detection.

```bash
# Basic scan
python wp2shell_scanner.py -f list.txt -o results.txt

# Skip SQLi test (faster)
python wp2shell_scanner.py -f list.txt -o results.txt --no-sqli-test

# JSON output
python wp2shell_scanner.py -f list.txt -j
```
### **wp2shell_intooutfile.py** - INTO OUTFILE Exploit

Demonstrates the INTO OUTFILE RCE variant (requires MySQL FILE privilege).

```bash
# Single target
python3 wp2shell_intooutfile.py https://target.com

# Multiple targets
python3 wp2shell_intooutfile.py -f list.txt -t 10
```
