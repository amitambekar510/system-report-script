# System Report Script 2.0 — AI-guided onboarding

When an assistant can read this repository, ask exactly **one question at a time**, beginning:

**"Which operating system and distribution do you need to report on (for example Ubuntu, RHEL, Debian, or another Linux distribution)?"**

Then ask:
1. How many hosts, and are they local, remote or managed by existing automation?
2. What is the purpose: SOC handover, asset inventory, troubleshooting, vulnerability-review support or audit evidence?
3. What execution privileges are authorized (unprivileged preferred)?
4. Which evidence sections are required (CPU, memory, disks, accounts, SSH MFA hints)?
5. Are sensitive identifiers allowed in the resulting report, and who may access it?
6. Is FIO benchmarking approved? **Default no.** If yes, ask about maintenance window, directory and storage impact.
7. Which regulatory requirements and retention controls actually apply?

Produce a tailored **review-only** plan: prerequisites, non-secret commands, output protection, expected unavailable sections, approval gates, limitations and evidence checklist. For a safe offline plan, use:

```bash
python3 scripts/plan_report.py --input examples/environment.sample.json --output /tmp/system-report-plan.md
```

This command does not inspect the host. For synthetic report generation use `bash system_check_and_fio.sh --demo`. For authorized host inventory, use `bash system_check_and_fio.sh`. Never add `--benchmark` unless the user explicitly opts in and approves disk load. Never assume that SSH MFA hints establish actual enforcement or that a complete inventory means compliance.

Do not fabricate measurements or certifications. Map only applicable controls in `docs/compliance-applicability.md`. A GitHub URL alone does not ensure an AI platform automatically reads these files; instruct it to read AGENTS.md and AI_INSTRUCTIONS.md.
