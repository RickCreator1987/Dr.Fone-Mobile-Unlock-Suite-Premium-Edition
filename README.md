# Mobile Service Suite

Compliance-first toolkit for servicing mobile devices you own or are explicitly authorized to service.

## What this is

- Authorization gate with evidence and expiry checks
- Tamper-evident audit log
- Device registry
- Official OEM/service integration stubs

## What this is not

- No iCloud/Google FRP bypass
- No carrier unlock circumvention
- No lock-screen bypass
- No use on devices without documented authorization

## Quick start

```bash
pip install -e ".[dev]"
pytest -q
mss --audit-log audit.jsonl verify-authorization dev-1 --evidence ./consent.pdf --authorized-by owner@example.com
mss --audit-log audit.jsonl verify-audit
