# Architecture

## Goals

- Every device action is gated by an authorization record with retained evidence.
- Every action is written to a tamper-evident audit log.
- No code path bypasses OEM security (iCloud, FRP, carrier locks, screen locks).
- Integrations use official vendor APIs or documented service interfaces only.

## Layers

```

+---------------------------------------------+

| CLI / API / Web UI                          |
+---------------------------------------------+

| Use-cases (authorize, backup, reset, ...)   |
+---------------------------------------------+

| Authorization | Audit | RBAC | Registry     |
+---------------------------------------------+

| Integrations: adb, Apple Configurator, MDM  |
+---------------------------------------------+

| Storage: SQLite, JSONL audit, filesystem    |
+---------------------------------------------+

```

## Key modules

| Module                   | Responsibility                                |
| ------------------------ | --------------------------------------------- |
| `core.authorization`     | Consent records, validity checks              |
| `core.audit`             | Append-only, hash-chained JSONL log           |
| `core.consent`           | Evidence hashing and optional HMAC signing    |
| `core.rbac`              | Roles and permissions                         |
| `core.store`             | SQLite persistence of authorizations          |
| `core.device_registry`   | Known devices per tenant                      |
| `integrations.adb`       | Android owner-authorized operations           |
| `integrations.apple`     | Apple Configurator / MDM authorized workflows |

## Data flow for a device action

1. Operator authenticates and presents credentials.
2. RBAC check for the requested permission.
3. `AuthorizationGate.require(device_id)` must succeed.
4. Integration performs the action via official interface.
5. `AuditLog.append(...)` records the action and its result.

Any failure at step 2–4 short-circuits to a denial audit entry.

## Non-goals

- No activation lock or FRP bypass.
- No carrier unlock circumvention.
- No covert data extraction.
- No use without documented authorization.
