---
id: VAL-001
type: validation
domain: schematic
status: verified
updated: 2026-10-03
---
# Extracted starter matches supplied archive

## Claim and revision
At import, all nine extracted files matched the bytes in the project's `Renegade_KiCad_Library_Starter.zip`.

## Method and actual result
A Python zipfile comparison read each non-directory archive entry and compared its bytes with the corresponding file in the project. Result: nine files checked, zero missing or different. The script was run in this chat on October 3, 2026.

## Evidence
[Archive](../../Renegade_KiCad_Library_Starter.zip) and [extracted package](../../Renegade_Library_Starter/README.md). The full comparison command and result are retained in this Codex chat's tool output.

## Scope and follow-up
This is only an import-integrity check at that time. It does not verify native KiCad loading, symbol correctness, circuit operation or electrical safety. Repeat a revision-specific comparison if files change.
