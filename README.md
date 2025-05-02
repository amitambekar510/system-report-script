# 🖥️ Linux System & FIO Benchmark Report Script

This Bash script generates comprehensive system reports for Linux servers, including hardware information, user and security data, and disk I/O performance using FIO. Reports are generated in **text**, **HTML**, **CSV**, and **JSON** formats for easy readability and integration.
## 📌 Features

- 📄 Collects CPU, RAM, and Disk information
- 👤 Lists user password change dates and account statuses
- 🔐 Checks MFA (Multi-Factor Authentication) status on SSH
- ⚙️ Runs FIO benchmarks for random read/write performance
- 📂 Generates reports in multiple formats:
  - Plain Text
  - HTML (with styled headers and sections)
  - CSV (structured data)
  - JSON (FIO output)

## 📦 Output Directory

All reports are saved to:  
`/tmp/system_reports/`

You can change this path in the `REPORT_DIR` variable.

## 📋 Requirements

- Bash (Linux shell)
- `fio` (Flexible I/O Tester) – [Install Guide](https://fio.readthedocs.io/en/latest/fio_doc.html)
- `jq` (for parsing JSON output) – `sudo apt install jq` on Debian-based systems

## 🛠️ How to Use

1. Make the script executable:
 
   chmod +x system_report.sh

2. Run the script:
./system_report.sh

3. View reports in /tmp/system_reports/
