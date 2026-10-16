# Runbook

## On-call quick reference

| Symptom                          | First check                              |
| -------------------------------- | ---------------------------------------- |
| `mss verify-audit` returns TAMPERED | Freeze writes, snapshot the log, page security |
| Authorization denied unexpectedly | Check evidence file exists, not expired, matches device_id |
| Backup fails with `AdbError`     | Confirm device authorized, `adb devices` shows `device` state |
| API returns 401                  | Missing `X-MSS-User` header or bad identity provider token |
| API returns 403                  | Principal lacks the permission for the action |

## Standard device intake

1. Record the device in the registry: `mss register-device ...`.
2. Obtain written owner consent. Store the signed PDF in the evidence vault.
3. Grant authorization: `mss grant-authorization ...`.
4. Perform only the action the consent covers.
5. Confirm the audit chain: `mss verify-audit`.

## Incident: suspected tampered audit log

1. Stop all writers (scale API to zero, disable CLI access).
2. Copy `audit.jsonl` and `mss.db` to a read-only evidence bucket.
3. Run `mss verify-audit` on the copy and capture output.
4. Compare against the last known-good export.
5. Notify security and legal. Do not modify the original files.

## Incident: unauthorized device action attempt

1. Locate the `authorization_denied` entries in the audit log.
2. Identify the operator id and source IP from the API access log.
3. Revoke any related authorizations: `mss revoke-authorization --id N`.
4. Follow HR / legal process for the operator.

## Incident: leaked consent evidence

1. Rotate the HMAC signing key used for evidence signatures.
2. Re-hash and re-sign all active evidence under the new key.
3. Notify affected data subjects per your DPIA and local law.
4. Record the event in the audit log with `event=incident_declared`.

## Retention and deletion

- Delete expired authorizations and their evidence after the retention window.
- Every deletion is itself audited (`event=authorization_deleted`).
- Audit log entries are never deleted; only rotated to cold storage.