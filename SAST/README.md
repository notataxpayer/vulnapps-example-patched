# SAST (Static Application Security Testing)

Automated security scanning menggunakan **Semgrep** untuk mendeteksi vulnerabilities di aplikasi.

---

## 📋 Prerequisites

### 1. Install Python 3.7+
```bash
python --version
```

### 2. Install Semgrep
```bash
# Via pip
pip install semgrep

# Atau via Homebrew (macOS)
brew install semgrep

# Atau via npm
npm install -g @semgrep/cli
```

### 3. Verify Installation
```bash
semgrep --version
```

---

## 🚀 Quick Start

### Run SAST Scan

```bash
# Windows PowerShell
cd SAST
python run_sast_scan.py

# Linux/macOS
cd SAST
python3 run_sast_scan.py
```

---

## 📁 Output Files

Setelah scan selesai, file-file berikut akan di-generate di folder `SAST/`:

### Timestamped Reports
- `semgrep_report_YYYYMMDD_HHMMSS.json` - JSON format (machine-readable)
- `semgrep_report_YYYYMMDD_HHMMSS.txt` - Text format (human-readable)
- `semgrep_report_YYYYMMDD_HHMMSS.html` - HTML format (browser-viewable)

### Latest Reports (Symlinks)
- `semgrep_report_latest.json` - Link ke JSON terbaru
- `semgrep_report_latest.txt` - Link ke text terbaru
- `semgrep_report_latest.html` - Link ke HTML terbaru

### Summary
- `semgrep_summary.md` - Markdown summary dengan statistik

---

## 📊 Report Formats

### 1. JSON Report
Machine-readable format untuk CI/CD integration atau parsing otomatis.

```json
{
  "results": [
    {
      "check_id": "javascript.react.security.audit.react-dangerouslysetinnerhtml.react-dangerouslysetinnerhtml",
      "path": "src/components/Chat/Chat.tsx",
      "start": { "line": 23 },
      "extra": {
        "message": "Detected usage of dangerouslySetInnerHTML...",
        "severity": "WARNING",
        "metadata": {
          "cwe": ["CWE-79"],
          "owasp": ["A03:2021"]
        }
      }
    }
  ]
}
```

### 2. Text Report
Human-readable format dengan grouping by severity.

```
================================================================================
SEMGREP SECURITY SCAN REPORT
================================================================================

Scan Date: 2025-10-28 10:30:00
Target: src/
Rulesets: p/react, p/javascript, p/xss, p/security-audit

Total Findings: 15
Total Errors: 0

SUMMARY BY SEVERITY
--------------------------------------------------------------------------------
  ERROR: 5
  WARNING: 7
  INFO: 3
```

### 3. HTML Report
Interactive browser-based report dengan syntax highlighting dan filtering.

**Features:**
- ✅ Summary cards dengan severity breakdown
- ✅ Color-coded findings
- ✅ Code snippets dengan syntax highlighting
- ✅ CWE/OWASP tags
- ✅ Responsive design

**Open in browser:**
```bash
# Windows
start SAST/semgrep_report_latest.html

# macOS
open SAST/semgrep_report_latest.html

# Linux
xdg-open SAST/semgrep_report_latest.html
```

### 4. Markdown Summary
Quick overview dengan top vulnerabilities.

---

## 🎯 Rulesets Used

Script menggunakan multiple Semgrep rulesets:

1. **`p/react`** - React-specific security rules
   - dangerouslySetInnerHTML usage
   - React anti-patterns
   - Component security issues

2. **`p/javascript`** - JavaScript security rules
   - eval() usage
   - Prototype pollution
   - Insecure randomness

3. **`p/typescript`** - TypeScript security rules
   - Type safety issues
   - Any type usage in sensitive contexts

4. **`p/xss`** - XSS vulnerability detection
   - Reflected XSS
   - Stored XSS
   - DOM-based XSS

5. **`p/security-audit`** - General security audit
   - Authentication issues
   - Authorization bypass
   - Sensitive data exposure

6. **`p/owasp-top-ten`** - OWASP Top 10 vulnerabilities
   - Injection attacks
   - Broken authentication
   - Sensitive data exposure
   - XML external entities (XXE)
   - Broken access control
   - Security misconfiguration
   - Cross-site scripting (XSS)
   - Insecure deserialization
   - Components with known vulnerabilities
   - Insufficient logging & monitoring

---

## 🔍 Understanding Severity Levels

### 🔴 ERROR / CRITICAL
- **Impact:** High
- **Exploitability:** Easy
- **Action Required:** **Fix immediately**
- **Examples:** 
  - Remote Code Execution (eval usage)
  - SQL Injection
  - Hardcoded credentials

### 🟡 WARNING
- **Impact:** Medium
- **Exploitability:** Moderate
- **Action Required:** **Fix soon**
- **Examples:**
  - XSS vulnerabilities
  - Weak cryptography
  - Path traversal

### 🔵 INFO
- **Impact:** Low
- **Exploitability:** Hard
- **Action Required:** Review and consider fixing
- **Examples:**
  - Code style issues
  - Best practice violations
  - Potential security improvements

---

## 🛠️ Advanced Usage

### Custom Rulesets

Edit `run_sast_scan.py` untuk menambah/mengurangi rulesets:

```python
RULESETS = [
    "p/react",
    "p/javascript",
    "p/typescript",
    "p/xss",
    "p/security-audit",
    "p/owasp-top-ten",
    # Add your custom rules
    "p/nodejs",
    "p/sql-injection",
]
```

### Scan Specific Directory

```bash
# Edit SRC_DIR in script atau run manual:
semgrep scan src/components --config p/react --json -o report.json
```

### CI/CD Integration

Tambahkan ke GitHub Actions, GitLab CI, atau Jenkins:

```yaml
# .github/workflows/sast.yml
name: SAST Scan
on: [push, pull_request]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Semgrep
        run: pip install semgrep
      - name: Run SAST Scan
        run: python SAST/run_sast_scan.py
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: sast-reports
          path: SAST/semgrep_report_*
```

---

## 📚 Resources

- **Semgrep Documentation:** https://semgrep.dev/docs/
- **Semgrep Rules Registry:** https://semgrep.dev/r
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CWE Database:** https://cwe.mitre.org/

---

## 🐛 Troubleshooting

### Semgrep Not Found
```bash
# Install Semgrep
pip install semgrep

# Verify installation
semgrep --version
```

### Permission Denied (Windows)
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Out of Memory
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
```

### Slow Scan
```bash
# Reduce rulesets atau scan specific directories
# Edit RULESETS in run_sast_scan.py
```

---

## 📝 Example Output

```
╔════════════════════════════════════════════════════════════╗
║           Automated SAST Scanner with Semgrep              ║
║                    Vulnerability Scanner                   ║
╚════════════════════════════════════════════════════════════╝

Target Directory: c:\Users\USER\...\src
Output Directory: c:\Users\USER\...\SAST
Timestamp: 20251028_103000
Rulesets: p/react, p/javascript, p/typescript, p/xss, p/security-audit, p/owasp-top-ten

[1/6] Checking Semgrep installation...
✓ Semgrep installed: 1.45.0

[2/6] Ensuring directories exist...
✓ SAST directory ready
✓ Source directory found

[3/6] Running Semgrep scan...
This may take a few minutes...

Scanning 50 files with 1500+ rules...
✓ Semgrep scan completed

[4/6] Generating text report...
✓ Text report generated: semgrep_report_20251028_103000.txt

[5/6] Generating HTML report...
✓ HTML report generated: semgrep_report_20251028_103000.html

[6/6] Generating Markdown summary...
✓ Markdown summary generated: semgrep_summary.md

✓ Symlinks created for latest reports

================================================================================
SCAN COMPLETED SUCCESSFULLY
================================================================================

✓ All reports generated successfully!

Generated Files:
  📄 JSON:     SAST/semgrep_report_20251028_103000.json
  📄 Text:     SAST/semgrep_report_20251028_103000.txt
  📄 HTML:     SAST/semgrep_report_20251028_103000.html
  📄 Summary:  SAST/semgrep_summary.md

Quick Links:
  📄 Latest JSON:  SAST/semgrep_report_latest.json
  📄 Latest Text:  SAST/semgrep_report_latest.txt
  📄 Latest HTML:  SAST/semgrep_report_latest.html

💡 Tip: Open the HTML report in your browser for the best viewing experience!
```

---

## ⚠️ Important Notes

1. **False Positives:** SAST tools dapat menghasilkan false positives. Review setiap finding secara manual.

2. **Performance:** Scan pertama mungkin lambat karena download rules. Subsequent scans akan lebih cepat.

3. **Updates:** Update Semgrep secara berkala untuk rule terbaru:
   ```bash
   pip install --upgrade semgrep
   ```

4. **Secrets Scanning:** Semgrep tidak detect hardcoded secrets by default. Gunakan tools seperti `trufflehog` atau `gitleaks` untuk secrets scanning.

---

## 🔒 Security Best Practices

1. ✅ Run SAST scan pada setiap commit (CI/CD)
2. ✅ Fix critical findings sebelum deploy
3. ✅ Review warning findings secara periodic
4. ✅ Keep Semgrep rules updated
5. ✅ Combine SAST dengan DAST (Dynamic testing)
6. ✅ Use secrets scanning tools
7. ✅ Regular security audits

---

**Happy Scanning! 🔍🛡️**
