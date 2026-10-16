# Versioning Policy

This project uses [Semantic Versioning](https://semver.org/).

## What counts as a breaking change

- Removing or renaming a public function, class, or CLI subcommand.
- Changing the audit log record shape.
- Changing the database schema in a way that requires manual migration.
- Removing a permission or renaming a role.

## What does not

- Adding new permissions or roles (additive, permitted in a minor bump).
- Adding new CLI subcommands.
- Adding new optional fields to audit records.
- Documentation-only changes.

## Release process

1. Update `CHANGELOG.md` under `[Unreleased]`.
2. Bump `version` in `pyproject.toml` and `src/mss/__init__.py`.
3. Tag `vX.Y.Z` and push.
4. The release workflow builds, tests, signs, and publishes the SBOM.