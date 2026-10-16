# Data Protection Impact Assessment (DPIA) Template

## 1. Description of processing

- **Purpose:** authorized mobile device servicing (backup, transfer, factory reset).
- **Categories of data subjects:** device owners, end users of managed devices.
- **Categories of personal data:** device identifiers, contact details on device, backups.
- **Recipients:** internal technicians; no third parties without written consent.
- **Retention:** see `data-protection.md`.

## 2. Necessity and proportionality

- Is the processing necessary for the stated purpose?
- Could the same outcome be achieved with less data?
- Is the retention period the shortest that meets legal/contractual need?

## 3. Risks to data subjects

| Risk                          | Likelihood | Severity | Mitigation                          |
| ----------------------------- | ---------- | -------- | ----------------------------------- |
| Unauthorized access to backup | Low        | High     | Encrypted at rest, RBAC, audit log  |
| Over-retention of evidence    | Medium     | Medium   | Automated retention job             |
| Re-identification from logs   | Low        | Medium   | Redaction rules, hash-only IDs      |
| Insider misuse                | Medium     | High     | Separation of duties, audit review  |

## 4. Measures envisaged

- Compliance-first architecture (see `docs/architecture.md`).
- Mandatory authorization gate on every mutating action.
- Tamper-evident audit log.
- Regular access reviews.

## 5. Sign-off

| Role        | Name | Date |
| ----------- | ---- | ---- |
| DPO         |      |      |
| Engineering |      |      |
| Legal       |      |      |