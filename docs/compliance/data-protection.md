# Data Protection

## Principles

- Collect only what is required for the authorized service action.
- Store consent evidence with SHA-256 hashes and optional HMAC signatures.
- Encrypt evidence at rest using OS-level controls (FileVault, BitLocker, LUKS).
- Redact device identifiers, serial numbers, and user data from logs.
- Retain records only as long as required by contract or law.
- Support export and deletion requests per data subject rights.

## Retention defaults

| Record type          | Default retention |
| -------------------- | ----------------- |
| Authorization record | 24 months         |
| Consent evidence     | 24 months         |
| Audit log            | 36 months         |
| Device registry      | Until device offboarded |