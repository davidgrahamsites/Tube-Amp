# Project materials map
Owner: the active Renegade agent. One job: route all project materials to their canonical owner and distinguish current work, historical drafts, received hardware and unselected candidates.
Inputs: ../../ engineering/source/planning files, ../records/, ../feedback/events.json.
Process: maintain register.json with exact project-relative paths and status. Do not copy component prices or dimensional values here; link their canonical registers. ../tools/build_project_catalog.py inventories all visible project files and checks these links.
Outputs: register.json (editable ownership map); generated ../catalog/WORKSPACE.md and FILES.json.
Human check: follow a material's link and verify its status against the actual file or received item. A file's existence is not hardware validation.
