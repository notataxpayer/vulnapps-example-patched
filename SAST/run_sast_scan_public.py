#!/usr/bin/env python3
"""
Automated SAST Scanner using Semgrep (Public Rulesets Only)
=============================================================

This script performs automated security scanning on the src/ directory
using Semgrep PUBLIC RULESETS and generates comprehensive reports in the SAST/ folder.

Requirements:
    - Python 3.7+
    - semgrep (install: pip install semgrep)

Usage:
    python run_sast_scan_public.py
    
Output:
    - SAST/semgrep_report_public_<timestamp>.json (JSON format)
    - SAST/semgrep_report_public_<timestamp>.txt (Human-readable format)
    - SAST/semgrep_report_public_<timestamp>.html (HTML format)
    - SAST/semgrep_summary_public.md (Markdown summary)
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
SCAN_DIR = PROJECT_ROOT  # Scan root project directory
SAST_DIR = SCRIPT_DIR
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Semgrep will use AUTO mode - automatically detects appropriate rules
RULESETS = ["auto"]  # Auto-detect rules based on project

# Output files (dengan suffix _public)
REPORT_JSON = SAST_DIR / f"semgrep_report_public_{TIMESTAMP}.json"
REPORT_TXT = SAST_DIR / f"semgrep_report_public_{TIMESTAMP}.txt"
REPORT_HTML = SAST_DIR / f"semgrep_report_public_{TIMESTAMP}.html"
REPORT_SARIF = SAST_DIR / f"semgrep_report_public_{TIMESTAMP}.sarif"
SUMMARY_MD = SAST_DIR / "semgrep_summary_public.md"

# Latest report symlinks
LATEST_JSON = SAST_DIR / "semgrep_report_public_latest.json"
LATEST_TXT = SAST_DIR / "semgrep_report_public_latest.txt"
LATEST_HTML = SAST_DIR / "semgrep_report_public_latest.html"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print script banner"""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║        Automated SAST Scanner with Semgrep (PUBLIC)        ║
║              Using Auto-Detected Security Rules            ║
╚════════════════════════════════════════════════════════════╝
{Colors.ENDC}
{Colors.OKCYAN}Target Directory:{Colors.ENDC} {SCAN_DIR}
{Colors.OKCYAN}Output Directory:{Colors.ENDC} {SAST_DIR}
{Colors.OKCYAN}Timestamp:{Colors.ENDC} {TIMESTAMP}
{Colors.OKCYAN}Mode:{Colors.ENDC} {', '.join(RULESETS)}
"""
    print(banner)


def check_semgrep_installed():
    """Check if Semgrep is installed"""
    print(f"{Colors.OKBLUE}[1/6] Checking Semgrep installation...{Colors.ENDC}")
    try:
        result = subprocess.run(
            ["semgrep", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"{Colors.OKGREEN}✓ Semgrep installed: {version}{Colors.ENDC}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{Colors.FAIL}✗ Semgrep not found!{Colors.ENDC}")
        print(f"{Colors.WARNING}Please install Semgrep:{Colors.ENDC}")
        print(f"  pip install semgrep")
        print(f"  or: brew install semgrep (macOS)")
        return False


def ensure_directories():
    """Ensure required directories exist"""
    print(f"\n{Colors.OKBLUE}[2/6] Ensuring directories exist...{Colors.ENDC}")
    SAST_DIR.mkdir(exist_ok=True)
    print(f"{Colors.OKGREEN}✓ SAST directory ready: {SAST_DIR}{Colors.ENDC}")
    
    if not SCAN_DIR.exists():
        print(f"{Colors.FAIL}✗ Scan directory not found: {SCAN_DIR}{Colors.ENDC}")
        return False
    print(f"{Colors.OKGREEN}✓ Scan directory found: {SCAN_DIR}{Colors.ENDC}")
    return True


def run_semgrep_scan():
    """Run Semgrep scan with auto-detected rules"""
    print(f"\n{Colors.OKBLUE}[3/6] Running Semgrep scan with AUTO mode...{Colors.ENDC}")
    print(f"{Colors.WARNING}This may take a few minutes...{Colors.ENDC}\n")
    
    # Build Semgrep command - using --config auto for automatic rule detection
    cmd = [
        "semgrep",
        "scan",
        str(SCAN_DIR),
        "--json",
        "--output", str(REPORT_JSON),
        "--config", "auto"  # Auto-detect appropriate rules
    ]
    
    print(f"{Colors.OKCYAN}Using AUTO mode - Semgrep will detect appropriate rules{Colors.ENDC}")
    print(f"  • Automatically analyzes project structure")
    print(f"  • Selects relevant security rules")
    print(f"  • Optimized for your codebase")
    
    try:
        # Run scan
        print(f"\n{Colors.OKCYAN}Executing: semgrep scan ...{Colors.ENDC}\n")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        # Semgrep returns different codes:
        # 0 = success, no findings
        # 1 = success, findings found  
        # 2+ = error
        if result.returncode in [0, 1]:
            print(f"{Colors.OKGREEN}✓ Semgrep scan completed{Colors.ENDC}")
            
            # Show stdout (debugging info)
            if result.stdout:
                print(f"\n{Colors.OKCYAN}Semgrep output:{Colors.ENDC}")
                lines = result.stdout.strip().split('\n')
                for line in lines[:5]:
                    print(line)
                if len(lines) > 5:
                    print(f"... ({len(lines) - 5} more lines)")
            
            return True
        else:
            print(f"{Colors.FAIL}✗ Semgrep scan failed with code {result.returncode}{Colors.ENDC}")
            if result.stderr:
                print(f"{Colors.FAIL}Error: {result.stderr}{Colors.ENDC}")
            if result.stdout:
                print(f"{Colors.WARNING}Output: {result.stdout}{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error running Semgrep: {e}{Colors.ENDC}")
        return False


def generate_text_report():
    """Generate human-readable text report"""
    print(f"\n{Colors.OKBLUE}[4/6] Generating text report...{Colors.ENDC}")
    
    try:
        with open(REPORT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        errors = data.get('errors', [])
        
        with open(REPORT_TXT, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SEMGREP SECURITY SCAN REPORT (AUTO MODE)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {SCAN_DIR}\n")
            f.write(f"Mode: Auto-detect rules\n")
            f.write(f"\nTotal Findings: {len(results)}\n")
            f.write(f"Total Errors: {len(errors)}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # Group by severity
            severity_counts = {'ERROR': 0, 'WARNING': 0, 'INFO': 0}
            findings_by_severity = {'ERROR': [], 'WARNING': [], 'INFO': []}
            
            for result in results:
                severity = result.get('extra', {}).get('severity', 'INFO').upper()
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                findings_by_severity.setdefault(severity, []).append(result)
            
            f.write("SUMMARY BY SEVERITY\n")
            f.write("-" * 80 + "\n")
            for sev in ['ERROR', 'WARNING', 'INFO']:
                count = severity_counts.get(sev, 0)
                f.write(f"  {sev}: {count}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # Detailed findings
            for severity in ['ERROR', 'WARNING', 'INFO']:
                findings = findings_by_severity.get(severity, [])
                if not findings:
                    continue
                
                f.write(f"\n{severity} FINDINGS ({len(findings)})\n")
                f.write("=" * 80 + "\n\n")
                
                for idx, finding in enumerate(findings, 1):
                    f.write(f"[{idx}] {finding.get('check_id', 'Unknown')}\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Message: {finding.get('extra', {}).get('message', 'No message')}\n")
                    f.write(f"File: {finding.get('path', 'Unknown')}\n")
                    f.write(f"Line: {finding.get('start', {}).get('line', '?')}\n")
                    
                    # Metadata
                    metadata = finding.get('extra', {}).get('metadata', {})
                    if 'cwe' in metadata:
                        f.write(f"CWE: {metadata['cwe']}\n")
                    if 'owasp' in metadata:
                        f.write(f"OWASP: {metadata['owasp']}\n")
                    if 'confidence' in metadata:
                        f.write(f"Confidence: {metadata['confidence']}\n")
                    
                    # Code snippet
                    lines = finding.get('extra', {}).get('lines', '')
                    if lines:
                        f.write(f"\nCode:\n{lines}\n")
                    
                    f.write("\n" + "-" * 80 + "\n\n")
            
            # Errors
            if errors:
                f.write(f"\nERRORS DURING SCAN ({len(errors)})\n")
                f.write("=" * 80 + "\n\n")
                for idx, error in enumerate(errors, 1):
                    f.write(f"[{idx}] {error.get('type', 'Unknown error')}\n")
                    f.write(f"Message: {error.get('message', 'No message')}\n")
                    f.write(f"Path: {error.get('path', 'Unknown')}\n\n")
        
        print(f"{Colors.OKGREEN}✓ Text report generated: {REPORT_TXT}{Colors.ENDC}")
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error generating text report: {e}{Colors.ENDC}")
        return False


def generate_html_report():
    """Generate HTML report"""
    print(f"\n{Colors.OKBLUE}[5/6] Generating HTML report...{Colors.ENDC}")
    
    try:
        with open(REPORT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        
        # Group by severity
        severity_counts = {'ERROR': 0, 'WARNING': 0, 'INFO': 0}
        findings_by_severity = {'ERROR': [], 'WARNING': [], 'INFO': []}
        
        for result in results:
            severity = result.get('extra', {}).get('severity', 'INFO').upper()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            findings_by_severity.setdefault(severity, []).append(result)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semgrep Security Scan Report (Public Rulesets)</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .header .badge {{ display: inline-block; background: rgba(255,255,255,0.2); padding: 5px 12px; border-radius: 12px; font-size: 12px; margin-top: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #fafafa; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 4px solid; }}
        .summary-card.error {{ border-color: #e74c3c; }}
        .summary-card.warning {{ border-color: #f39c12; }}
        .summary-card.info {{ border-color: #3498db; }}
        .summary-card h3 {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
        .summary-card .count {{ font-size: 32px; font-weight: bold; }}
        .summary-card.error .count {{ color: #e74c3c; }}
        .summary-card.warning .count {{ color: #f39c12; }}
        .summary-card.info .count {{ color: #3498db; }}
        .findings {{ padding: 30px; }}
        .finding {{ background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .finding.error {{ border-left: 4px solid #e74c3c; }}
        .finding.warning {{ border-left: 4px solid #f39c12; }}
        .finding.info {{ border-left: 4px solid #3498db; }}
        .finding-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px; }}
        .finding-title {{ font-size: 18px; font-weight: bold; color: #333; }}
        .severity-badge {{ padding: 5px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        .severity-badge.error {{ background: #e74c3c; color: white; }}
        .severity-badge.warning {{ background: #f39c12; color: white; }}
        .severity-badge.info {{ background: #3498db; color: white; }}
        .finding-message {{ color: #555; margin-bottom: 15px; line-height: 1.6; white-space: pre-wrap; }}
        .finding-meta {{ display: flex; gap: 20px; margin-bottom: 15px; color: #666; font-size: 14px; }}
        .finding-meta span {{ display: flex; align-items: center; gap: 5px; }}
        .code-block {{ background: #282c34; color: #abb2bf; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.5; }}
        .metadata {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }}
        .metadata-tag {{ background: #ecf0f1; padding: 5px 10px; border-radius: 4px; font-size: 12px; color: #555; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Semgrep Security Scan Report</h1>
            <span class="badge">AUTO MODE</span>
            <p>Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Target: {SCAN_DIR.relative_to(PROJECT_ROOT) if SCAN_DIR != PROJECT_ROOT else 'Root Project'}</p>
            <p>Mode: Auto-detect rules</p>
        </div>
        
        <div class="summary">
            <div class="summary-card error">
                <h3>CRITICAL / ERROR</h3>
                <div class="count">{severity_counts.get('ERROR', 0)}</div>
            </div>
            <div class="summary-card warning">
                <h3>WARNING</h3>
                <div class="count">{severity_counts.get('WARNING', 0)}</div>
            </div>
            <div class="summary-card info">
                <h3>INFO</h3>
                <div class="count">{severity_counts.get('INFO', 0)}</div>
            </div>
            <div class="summary-card">
                <h3>TOTAL FINDINGS</h3>
                <div class="count" style="color: #667eea;">{len(results)}</div>
            </div>
        </div>
        
        <div class="findings">
"""
        
        # Add findings for each severity
        for severity in ['ERROR', 'WARNING', 'INFO']:
            findings = findings_by_severity.get(severity, [])
            if not findings:
                continue
            
            html_content += f'<h2 style="margin-bottom: 20px; color: #333;">{severity} Findings ({len(findings)})</h2>\n'
            
            for idx, finding in enumerate(findings, 1):
                check_id = finding.get('check_id', 'Unknown')
                message = finding.get('extra', {}).get('message', 'No message')
                path = finding.get('path', 'Unknown')
                line = finding.get('start', {}).get('line', '?')
                code = finding.get('extra', {}).get('lines', '').replace('<', '&lt;').replace('>', '&gt;')
                metadata = finding.get('extra', {}).get('metadata', {})
                
                html_content += f"""
        <div class="finding {severity.lower()}">
            <div class="finding-header">
                <div class="finding-title">{check_id}</div>
                <span class="severity-badge {severity.lower()}">{severity}</span>
            </div>
            <div class="finding-message">{message}</div>
            <div class="finding-meta">
                <span>📁 {path}</span>
                <span>📍 Line {line}</span>
            </div>
"""
                
                # Add metadata tags
                if metadata:
                    html_content += '<div class="metadata">\n'
                    if 'cwe' in metadata:
                        cwe_list = metadata['cwe'] if isinstance(metadata['cwe'], list) else [metadata['cwe']]
                        for cwe in cwe_list:
                            html_content += f'<span class="metadata-tag">CWE: {cwe}</span>\n'
                    if 'owasp' in metadata:
                        owasp_list = metadata['owasp'] if isinstance(metadata['owasp'], list) else [metadata['owasp']]
                        for owasp in owasp_list:
                            html_content += f'<span class="metadata-tag">OWASP: {owasp}</span>\n'
                    if 'confidence' in metadata:
                        html_content += f'<span class="metadata-tag">Confidence: {metadata["confidence"]}</span>\n'
                    html_content += '</div>\n'
                
                # Add code snippet
                if code:
                    html_content += f'<pre class="code-block">{code}</pre>\n'
                
                html_content += '</div>\n'
        
        html_content += """
        </div>
        
        <div class="footer">
            Generated by Automated SAST Scanner using Semgrep Public Rulesets
        </div>
    </div>
</body>
</html>
"""
        
        with open(REPORT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"{Colors.OKGREEN}✓ HTML report generated: {REPORT_HTML}{Colors.ENDC}")
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error generating HTML report: {e}{Colors.ENDC}")
        return False


def generate_markdown_summary():
    """Generate Markdown summary"""
    print(f"\n{Colors.OKBLUE}[6/6] Generating Markdown summary...{Colors.ENDC}")
    
    try:
        with open(REPORT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        
        # Group by severity and vulnerability type
        severity_counts = {'ERROR': 0, 'WARNING': 0, 'INFO': 0}
        vuln_types = {}
        
        for result in results:
            severity = result.get('extra', {}).get('severity', 'INFO').upper()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            check_id = result.get('check_id', 'Unknown')
            vuln_types[check_id] = vuln_types.get(check_id, 0) + 1
        
        md_content = f"""# Semgrep SAST Scan Summary (Auto Mode)

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Target:** `{SCAN_DIR.relative_to(PROJECT_ROOT) if SCAN_DIR != PROJECT_ROOT else 'Root Project'}`  
**Mode:** Auto-detect rules

---

## 📊 Summary

| Severity | Count |
|----------|-------|
| 🔴 **CRITICAL/ERROR** | **{severity_counts.get('ERROR', 0)}** |
| 🟡 **WARNING** | **{severity_counts.get('WARNING', 0)}** |
| 🔵 **INFO** | **{severity_counts.get('INFO', 0)}** |
| **TOTAL** | **{len(results)}** |

---

## 🎯 Top Vulnerability Types

| Vulnerability Type | Count |
|--------------------|-------|
"""
        
        # Sort by count
        sorted_vulns = sorted(vuln_types.items(), key=lambda x: x[1], reverse=True)
        for vuln, count in sorted_vulns[:10]:  # Top 10
            md_content += f"| `{vuln}` | {count} |\n"
        
        md_content += f"""
---

## 📁 Report Files

- **JSON Report:** `{REPORT_JSON.name}`
- **Text Report:** `{REPORT_TXT.name}`
- **HTML Report:** `{REPORT_HTML.name}`

---

## 🔍 Key Findings

"""
        
        # Highlight critical findings
        critical_findings = [r for r in results if r.get('extra', {}).get('severity', '').upper() == 'ERROR']
        if critical_findings:
            md_content += "### 🔴 Critical Issues\n\n"
            for finding in critical_findings[:5]:  # Top 5 critical
                check_id = finding.get('check_id', 'Unknown')
                message = finding.get('extra', {}).get('message', 'No message')
                path = finding.get('path', 'Unknown')
                line = finding.get('start', {}).get('line', '?')
                
                md_content += f"#### `{check_id}`\n\n"
                md_content += f"**Message:** {message}\n\n"
                md_content += f"**Location:** `{path}:{line}`\n\n"
                md_content += "---\n\n"
        
        md_content += f"""
## 📚 References

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)

---

**Scan completed successfully. Review the detailed reports for more information.**
"""
        
        with open(SUMMARY_MD, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"{Colors.OKGREEN}✓ Markdown summary generated: {SUMMARY_MD}{Colors.ENDC}")
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error generating Markdown summary: {e}{Colors.ENDC}")
        return False


def create_symlinks():
    """Create symlinks to latest reports"""
    try:
        # Remove old symlinks if exist
        for latest in [LATEST_JSON, LATEST_TXT, LATEST_HTML]:
            if latest.exists():
                latest.unlink()
        
        # Create new symlinks
        LATEST_JSON.symlink_to(REPORT_JSON.name)
        LATEST_TXT.symlink_to(REPORT_TXT.name)
        LATEST_HTML.symlink_to(REPORT_HTML.name)
        
        print(f"\n{Colors.OKGREEN}✓ Symlinks created for latest reports{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.WARNING}⚠ Could not create symlinks: {e}{Colors.ENDC}")


def print_summary():
    """Print final summary"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}SCAN COMPLETED SUCCESSFULLY (AUTO MODE){Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    print(f"{Colors.OKGREEN}✓ All reports generated successfully!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Generated Files:{Colors.ENDC}")
    print(f"  📄 JSON:     {REPORT_JSON.relative_to(PROJECT_ROOT)}")
    print(f"  📄 Text:     {REPORT_TXT.relative_to(PROJECT_ROOT)}")
    print(f"  📄 HTML:     {REPORT_HTML.relative_to(PROJECT_ROOT)}")
    print(f"  📄 Summary:  {SUMMARY_MD.relative_to(PROJECT_ROOT)}")
    
    print(f"\n{Colors.BOLD}Quick Links:{Colors.ENDC}")
    print(f"  📄 Latest JSON:  {LATEST_JSON.relative_to(PROJECT_ROOT)}")
    print(f"  📄 Latest Text:  {LATEST_TXT.relative_to(PROJECT_ROOT)}")
    print(f"  📄 Latest HTML:  {LATEST_HTML.relative_to(PROJECT_ROOT)}")
    
    print(f"\n{Colors.OKCYAN}💡 Tip: Open the HTML report in your browser for the best viewing experience!{Colors.ENDC}")
    print(f"{Colors.OKCYAN}   file://{REPORT_HTML.absolute()}{Colors.ENDC}\n")


def main():
    """Main execution function"""
    print_banner()
    
    # Step 1: Check Semgrep installation
    if not check_semgrep_installed():
        sys.exit(1)
    
    # Step 2: Ensure directories
    if not ensure_directories():
        sys.exit(1)
    
    # Step 3: Run Semgrep scan
    if not run_semgrep_scan():
        sys.exit(1)
    
    # Step 4: Generate text report
    if not generate_text_report():
        sys.exit(1)
    
    # Step 5: Generate HTML report
    if not generate_html_report():
        sys.exit(1)
    
    # Step 6: Generate Markdown summary
    if not generate_markdown_summary():
        sys.exit(1)
    
    # Create symlinks to latest reports
    create_symlinks()
    
    # Print summary
    print_summary()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠ Scan interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
