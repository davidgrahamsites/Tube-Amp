---
id: VAL-002
type: validation
domain: cross-domain
status: verified
updated: 2026-10-04
---
# KiCad MCP installation and scoped smoke checks

## Scope and identity
User requested installation of a KiCad MCP server on October 4, 2026. Installed KiCad Agentic MCP (`konnect`) v1.2.0, native Apple Silicon standalone release, alongside KiCad CLI 10.0.6. Verification covers installation, stdio startup, tool discovery, project metadata reading and one schematic SVG export. It does not verify amplifier engineering or all server capabilities.

## Sources and installation
- [Maintainer repository](https://github.com/nevenfo/kicad-agentic-mcp) and [v1.2.0 release](https://github.com/nevenfo/kicad-agentic-mcp/releases/tag/v1.2.0).
- Downloaded `konnect-v1.2.0-aarch64-apple-darwin.tar.gz`; SHA-256 matched the release API digest: `616db20a5a6af2900a46194ca6aef8cffb8938b86b5a9e3f8fda9a11f371b112`.
- Installed executable: `/Users/appleadmin/.local/share/kicad-mcp/v1.2.0/konnect`. Release metadata and smoke-test JSON/logs are retained alongside it.
- Registered global Codex stdio server `kicad` using `codex mcp add kicad -- /Users/appleadmin/.local/share/kicad-mcp/v1.2.0/konnect`; `codex mcp get kicad` confirms it is enabled.
- Compared parsed configuration against the backup. The CLI rewrite removed the existing `node_repl.args` field; restored its original section and confirmed all prior settings were preserved, with only the `kicad` server added.
- With KiCad not running, enabled `api.enable_server` in `/Users/appleadmin/Library/Preferences/kicad/10.0/kicad_common.json` for its next launch. KiCad.app was not modified.
- Configuration backups: `/Users/appleadmin/.codex/config.toml.before-kicad-mcp-20261004-010035.bak` and `/Users/appleadmin/Library/Preferences/kicad/10.0/kicad_common.json.before-kicad-mcp-20261004-010035.bak`.
- On first startup, the server reported automatic installation of six bundled skills and two agent definitions under `/Users/appleadmin/.claude/skills/` and `/Users/appleadmin/.claude/agents/`. No agents were dispatched.

## Checks and results
1. `kicad-cli version`: 10.0.6. Host architecture: arm64.
2. Direct stdio MCP initialize: server `konnect` 1.2.0; negotiated protocol 2025-06-18. `tools/list` returned 21 startup tools.
3. `get_project_info` read the imported preview project and correctly reported the schematic present and PCB absent. Its `kicad_version` field contained a filename rather than a version; use the native CLI result for version identity.
4. Loaded `export_schematic_svg` through `load_tools`, then called it directly. MCP reported successful CLI export in approximately 0.875 seconds. The SVG exists, is 584,402 bytes and contains an SVG element. Export evidence is at `/Users/appleadmin/.local/share/kicad-mcp/v1.2.0/export-direct-check.json`; output is in that directory's `export-direct/` folder.
5. Source schematic SHA-256 was unchanged before/after the successful export: `0d3705847c099bef550fbed17de2b9043ff9c00a230f911a72875e4a134be4de`.

## Failures and limits
A prior `kicad_invoke` gateway export attempt timed out at the test client's 30-second response limit, although an SVG was produced. The subsequent direct tool route succeeded. The timeout cause was not resolved; prefer the tested direct route and investigate the gateway before relying on its transactional behavior.

The SVG was checked structurally, not visually reviewed here. No ERC, DRC, schematic editing, board editing or live IPC connection was tested. No PCB exists in the starter and KiCad was not running. The current Codex chat's callable tools do not refresh from the edited configuration automatically; restart/reload Codex to load the new server. Live PCB work additionally needs KiCad's PCB editor running with a board open. This installation does not resolve the missing original schematic or cabinet dimensions.

## Next check
After client reload and opening an appropriate board in KiCad, confirm IPC access with a read-only query before any board mutation. Use copies for initial edit trials and native KiCad validation for each resulting artifact. Preserve tube-amplifier review boundaries in the handoff.
