# Legal Framework

This project operates under the assumption that every device action requires one of:

- **Ownership** — the operator owns the device.
- **Written authorization** — the owner signed a service authorization.
- **Enterprise admin** — the operator is the MDM/IT admin for a managed fleet.
- **Legal process** — a lawful court order or equivalent with retained evidence.

## Relevant law categories

- Computer misuse / unauthorized access statutes
- Consumer protection and unfair business practice rules
- Data protection (GDPR, CCPA, and equivalents)
- Copyright / anti-circumvention (DMCA §1201 and equivalents)
- Carrier and telecommunications regulation
- Export control (cryptographic tooling)

## Enforcement

No code path may proceed without an active `AuthorizationRecord`. Denials are
logged. The audit log is append-only and tamper-evident.