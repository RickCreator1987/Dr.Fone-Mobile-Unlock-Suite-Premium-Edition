# Contributing

## Ground rules

1. No code that bypasses OEM security, activation locks, FRP, carrier locks,
   screen locks, or encryption.
2. Every device-mutating feature must go through `AuthorizationGate` and
   `AuditLog`.
3. New integrations must use official vendor APIs or documented service
   interfaces.
4. Add tests for authorization, denial, and audit paths.
5. Run `ruff check src tests` and `pytest -q` before opening a PR.

## PR checklist

- [ ] Compliance impact documented in `docs/compliance/`
- [ ] Authorization path covered by tests
- [ ] Audit event emitted for new actions
- [ ] No secrets, tokens, or PII committed
- [ ] SBOM and dependency audit pass in CI