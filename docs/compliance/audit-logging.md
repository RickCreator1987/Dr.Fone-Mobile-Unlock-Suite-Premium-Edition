# Audit Logging

## Format

Append-only JSONL. Each line contains:

- `ts` — ISO-8601 UTC timestamp
- `event` — event type
- `prev_hash` — SHA-256 of previous record
- `hash` — SHA-256 of this record
- plus event-specific fields

## Required events

- `authorization_granted`
- `authorization_denied`
- `authorization_revoked`
- `device_registered`
- `device_backup_started`
- `device_backup_completed`
- `device_factory_reset`
- `audit_exported`

## Verification

`mss verify-audit` walks the chain and confirms no record was modified or removed.