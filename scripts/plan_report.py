#!/usr/bin/env python3
"""Offline, non-invasive report planning. No host inspection or benchmarking."""
import argparse
import json
from pathlib import Path

REQUIRED=("operating_system","host_count","purpose","access","sections","benchmark_approved","output_classification")
def plan(data):
    if not isinstance(data,dict): raise ValueError("Input must be a JSON object")
    missing=[k for k in REQUIRED if k not in data]
    if missing: raise ValueError("Missing required fields: "+", ".join(missing))
    if type(data["host_count"]) is not int or not 1<=data["host_count"]<=100000:
        raise ValueError("host_count must be a positive integer")
    if type(data["benchmark_approved"]) is not bool: raise ValueError("benchmark_approved must be boolean")
    if not isinstance(data["sections"],list) or not data["sections"] or not all(isinstance(x,str) and x.strip() for x in data["sections"]):
        raise ValueError("sections must be nonempty strings")
    for k in ("operating_system","purpose","access","output_classification"):
        if not isinstance(data[k],str) or not data[k].strip(): raise ValueError(k+" must be nonempty")
    def safe(value):
        return str(value).replace("\r"," ").replace("\n"," ").replace("<","&lt;").replace(">","&gt;")
    lines=["# System Report Script 2.0 — Deployment Plan","","**Offline planning only. No host commands executed.**","",
           "## Environment",""]
    for key in REQUIRED:
        value=", ".join(data[key]) if isinstance(data[key],list) else data[key]
        lines.append("- **"+safe(key.replace("_"," ").title())+":** "+safe(value))
    lines+=["","## Safe deployment steps","",
        "1. Verify Linux and Python 3.10+ on each approved host.",
        "2. Start with `bash system_check_and_fio.sh --demo` to view synthetic report output.",
        "3. Obtain written approval before running `bash system_check_and_fio.sh` on real hosts.",
        "4. Run without sudo initially; mark restricted sections unavailable, not compliant.",
        "5. Restrict access to HTML/TXT/CSV/JSON reports; apply organizational retention and deletion controls.",
        "6. Review MFA hints manually and document exceptions and ownership.",
        "7. Attach redacted, time-stamped evidence to authorized tickets or audit records."]
    if data["benchmark_approved"]:
        lines+=["","## Optional FIO — approved in questionnaire","",
          "Before running: obtain an approved maintenance window, choose an existing filesystem directory, confirm free space and understand that disk load will occur. Benchmarking still requires an explicit command-line opt-in and separate operational approval."]
    else:
        lines+=["","## FIO benchmarking","",
          "**Not approved:** Do not pass `--benchmark`. The report remains an inventory-only inspection."]
    lines+=["","## Regulatory note","","See docs/compliance-applicability.md. This report supports evidence gathering, not compliance certification."]
    return "\n".join(lines)+"\n"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    output=plan(json.loads(a.input.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(output,encoding="utf-8")
    print("Wrote",a.output)
if __name__=="__main__":main()
