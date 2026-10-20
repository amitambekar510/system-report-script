# System Report Script 2.0 — regulatory/framework applicability

**Evidence-support matrix only.** These 12 requested references do not mean 12 certifications, complete audit coverage or that the tool is mandated. Check current law, amendments, entity category, contractual requirements and audit scope.

| Reference | Possible system inventory evidence | Qualification |
|---|---|---|
| CERT-In Directions 2022 | Host identification and time-stamped investigation context | Tool does not implement required incident reporting or log retention |
| SEBI CSCRF 2024 | Asset inventory and security configuration review | Applies to covered SEBI-regulated entities |
| RBI IT and Cyber | IT asset, access and configuration review | Requirements depend on RBI entity category |
| DPDP Act 2023 | Safeguards and handling of personal data in report files | Verify commenced provisions; reports may contain personal data |
| NSE/BSE technology audit | System and access-review evidence | Exchange/member-specific audit scope |
| NPCI/UPI | Infrastructure inventory and security review | Participant-specific obligations |
| SEBI PFUTP 2003 | Potential investigation context | Not a Linux inventory or cybersecurity scanning mandate |
| ISO/IEC 27001:2022 | Asset management, access control, configuration and logging context | ISMS scope and Statement of Applicability govern |
| ISO/IEC 27090 | Identifier/title not independently verified | No compliance claim |
| MITRE ATT&CK | Host telemetry context for threat-hunting planning | Not a compliance standard |
| ISO/IEC 42001:2023 | Governance if AI assistants process host report data | Conditional AI management system scope |
| NIST CSF 2.0 | Identify assets and protect/monitor controls | Framework mapping, not certification |

**Evidence gaps:** The script does not perform authenticated vulnerability scanning, full CIS benchmarking, centralized log collection, continuous monitoring, SIEM correlation or conclusive SSH MFA validation. Mark absent evidence as unavailable and assign manual owners.

Official starting points: https://www.cert-in.org.in/ · https://www.sebi.gov.in/ · https://www.rbi.org.in/ · https://www.meity.gov.in/ · https://www.iso.org/ · https://attack.mitre.org/ · https://www.nist.gov/cyberframework
