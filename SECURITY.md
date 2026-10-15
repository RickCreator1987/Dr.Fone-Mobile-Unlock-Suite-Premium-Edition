# Security Policy

## Reporting

Report vulnerabilities to security@your-org.example. Do not open public issues for
security reports.

## Scope

This project performs device service operations only with explicit, documented
authorization. Anything that bypasses OEM security (iCloud Activation Lock,
Google FRP, carrier locks, lock screens, encryption) is out of scope and will be
rejected from contributions.

## Hardening expectations

- All device actions must pass `AuthorizationGate.require()`.
- Every action is written to the tamper-evident `AuditLog`.
- Consent evidence files are hashed with SHA-256 and, where configured, HMAC-signed.
- RBAC enforced for every action.
- No credentials, tokens, or device PII in logs.
- Dependency scanning and SBOM generated on every release.