# Generated project catalog
Owner: ../tools/build_project_catalog.py. One job: present the project inventory and feedback for cold-start navigation.
Inputs: ../materials/register.json, ../feedback/events.json and visible workspace files.
Process: regenerate with python3 brain/tools/build_project_catalog.py --as-of YYYY-MM-DD from the project root. Edit source registers, not generated tables. Exclude hidden application metadata, caches and this output folder from recursive inventory.
Outputs: WORKSPACE.md, FEEDBACK.md, FILES.json and checks.json. The initial backfill report and before-inventory are retained evidence, not regenerated source state.
Human check: open the current schematic, BOM, mechanical register and latest feedback from WORKSPACE.md; verify they agree on revision and remaining work.
