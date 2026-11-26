Reader tools. Owner: integration. Inputs: explicitly listed legacy reports or editable HTML. Process: one-time import to HTML; provision local KaTeX; check links, equations and browser layout. Outputs: current HTML reports and evidence checks. Never overwrite an edited HTML report during migration; render checks do not validate the amplifier.

Install the exact package.json dependencies in an external tool directory. Set RENEGADE_READER_DEPS to its package.json. Run check_reader.mjs from the repository; it opens only isolated headless local pages, offline. Set RENEGADE_CHROME if Chrome is at another path. decorate.mjs updates presentation only. import_legacy.mjs skips existing HTML.

export_equipment.py reads only test-equipment.html and local presentation assets; writes one current self-contained exports/test-equipment.html. It embeds fonts and KaTeX, converts local source links to repository links, and never changes engineering content. Verify offline at desktop/mobile widths after export.

check_equipment.mjs copies the export outside the repository and verifies offline desktop/mobile rendering, equations, asset independence and internal anchors; writes equipment-checks.json and three current screenshots under ../evidence/. Uses RENEGADE_READER_DEPS like check_reader.mjs.
