---
id: VAL-008
type: validation
domain: cross-domain
status: verified
updated: 2026-10-04
---
# Requested mixelpixx KiCAD MCP server installation

## Claim and revision
The specifically requested [mixelpixx/KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server) stable release v2.8.2, commit `670d2a9c48e1588f2e07edaf656b5e301fc55a50`, is installed and enabled globally in Codex as `kicad_mixelpixx`. This is separate from the existing `kicad` / Konnect installation in [VAL-002](VAL-002-kicad-mcp-install.md).

## Task and method
Owner: this Codex chat. Inputs: user-specified repository, existing Codex configuration, KiCad 10.0.6 and preview schematic. Outputs: local runtime, backed-up Codex registration and this scoped validation. Dependencies: Node.js and KiCad bundled Python 3.9.13. Done-condition: successful build, MCP initialization/tool discovery, read-only schematic/library queries and enabled registration with prior settings preserved. Estimated effort: approximately ten minutes. No human engineering evidence is required for installation; amplifier validation remains separate.

Followed the repository's macOS setup instructions: created `venv` using KiCad's bundled Python with `--system-site-packages`, installed `requirements.txt`, and built TypeScript via `npm ci` (prepare runs `npm run build`). The setup script's `--verify` passed. No Claude configuration was written. Runtime is at `/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/`.

`npm audit fix --omit=dev` applied compatible dependency updates to the local lockfile and removed development dependencies after the build. The production audit reported zero vulnerabilities. The upstream source was not patched; the local dependency lock differs from upstream. Do not use `npm ci` later without reviewing the retained lock and rebuilding if source changes.

## Actual result
- MCP initialization returned `kicad-mcp-server` v2.8.2 and 244 registered tools.
- `list_schematic_components` read the imported preview and returned RT1, T1 and J1 with their expected custom library IDs and pin counts.
- `list_symbol_libraries` returned 223 libraries.
- `check_kicad_ui` returned without an MCP error, but its process matching also identifies MCP processes as KiCad. Its `running` flag is not evidence that the actual KiCad GUI or IPC session is available.
- Preview schematic SHA-256 before/after: `0d3705847c099bef550fbed17de2b9043ff9c00a230f911a72875e4a134be4de`; unchanged.
- `codex mcp get kicad_mixelpixx` confirms enabled stdio registration. Parsed TOML comparison proves all previous settings were preserved and only the new server table was added.

The first check called a backend tool immediately after the MCP handshake, before Python had started, and received `Python process for KiCAD scripting is not running`. The corrected check waits for the explicit `KiCAD MCP SERVER READY` message before backend queries; all subsequent checks passed. The Python warm-up logs a wxWidgets assertion (`create wxApp before calling this`) but completes successfully. Board mutation and live GUI behavior remain untested.

## Evidence
- [Check script](/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/install-check.mjs)
- [Successful results](/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/install-check.json) and [stderr](/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/install-check.stderr.log)
- [First attempt](/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/install-check-first-attempt.json)
- [Codex registration and backup identity](/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/codex-registration.json)
- [Final production audit](/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/install-audit-final.json)
- [Python dependency inventory](/Users/appleadmin/.local/share/kicad-mcp/mixelpixx/installed-python.txt)
- [Codex configuration](/Users/appleadmin/.codex/config.toml) and backup `/Users/appleadmin/.codex/config.toml.before-mixelpixx-kicad-mcp-20261004-033705.bak`.
- [Official Codex MCP configuration documentation](https://developers.openai.com/codex/mcp).

## Scope and follow-up
Installation and the named read-only queries are verified. Restart/reload Codex to load the newly registered server's tools; this chat's existing `mcp__kicad__` tools refer to Konnect. No amplifier design files were changed, no ERC/DRC was run, and no board editing or IPC connection was verified. Use disposable copies and native validation when first qualifying mutation tools. Electrical review remains governed by the handoff.
