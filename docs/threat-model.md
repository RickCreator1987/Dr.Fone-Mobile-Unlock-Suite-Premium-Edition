# Threat Model (STRIDE)

## Assets

- Consent evidence files
- Authorization records
- Audit log
- Device data during authorized backups
- Operator credentials

## Trust boundaries

- Operator UI -> service
- Service -> SQLite / filesystem
- Service -> device (adb, Configurator, MDM)
- Service -> audit sink

## Threats and mitigations

| Threat                       | STRIDE      | Mitigation                                              |
| ---------------------------- | ----------- | ------------------------------------------------------- |
| Forged authorization         | Spoofing    | HMAC-signed evidence, hash on ingest, expiry checks     |
| Tampered audit log           | Tampering   | Hash-chained JSONL, `verify-audit` command              |
| Repudiation of an action     | Repudiation | Signed audit entries, per-operator identity             |
| Leaked evidence              | Info disc.  | Filesystem encryption, redaction of PII in logs         |
| DoS via huge backups         | DoS         | Size limits, timeouts, quotas                           |
| Privilege escalation         | Elevation   | RBAC enforced at use-case layer, deny by default        |
| Supply chain compromise      | Tampering   | pip-audit, SBOM, pinned deps in lockfile                |
| Misuse on unauthorized device| Spoofing    | AuthorizationGate.require() is mandatory for all writes |

## Out-of-scope threats

- Physical attacks on the device
- Nation-state adversaries
- Compromise of the OEM service channel itself