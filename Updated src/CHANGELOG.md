# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial compliance-first scaffold: authorization gate, audit log, RBAC, registry.
- Android adb integration for owner-authorized operations.
- Apple integration stub (Configurator / MDM).
- FastAPI review API with `/authorizations`, `/audit/verify`, `/healthz`.
- SQLite migrations and retention job.
- Helm chart for internal deployment.

### Security
- No activation-lock, FRP, carrier-lock, or screen-lock bypass. By design.
- Hash-chained, tamper-evident audit log.
- HMAC-signed consent evidence (optional).