# Repository skill sources

This directory keeps skill instructions and their bundled references, scripts,
fonts, examples, and other assets in Git. `skill-sources.json` records the 25
skills added from local installations on October 10, 2026. Plugin caches and
Codex system skills remain managed by their own installers.

The source copies preserve their original instructions. Some target Claude
host tools, authenticated connectors, or particular local paths. A tracked
copy does not install those dependencies or establish runtime compatibility.
In particular, `docs`, `import-memory`, and `morning` retain their Claude host
requirements. Command wrappers are saved as instructions; importing a wrapper
does not run its command or copy any account data.

Refresh the generated Codex layer from the repository root:

```powershell
python scripts/export_codex_layer.py
python scripts/export_codex_layer.py --check
```

The exporter leaves global skill installations and local MCP settings alone
unless their explicit flags are supplied. It treats `figma` as an external
connector capability; its original skill is retained here even though no
Codex skill mirror is generated for it.

Run portable validation with the locked core environment as described in
`CODEX_TEAM/README.md`. To restore skills to another machine, use that host's
skill installation workflow and retain each skill's supporting files. Avoid
copying private memory, credentials, generated outputs, or plugin caches.
