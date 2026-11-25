# Manufacturer evidence

TI-SN74HC14-L.pdf, Diodes-MMBT3904-2025.pdf and KNSCHA-CL23-2023.pdf support the unadopted delay candidate. Exact URLs/hashes are in ../results/rail-delay-sources.json. Distinguish room-temperature and post-cooling tests from continuous hot operation.
Owner: Renegade integration. Inputs: exact AOS datasheet/package URLs recorded in manufacturer-documents.json. Process: retain original bytes and source hashes; compare dimensions and pinout with selected native footprint. Outputs: primary source PDFs for the control-switching review. Human check: verify the delivered AOS-marked part and actual assembly against these exact drawings; a listing title alone is insufficient.

TI-LM393-AH.pdf and TI-comparator-guidelines-SNOAA35F.pdf are primary inputs for the proposed analog-rail monitor. Their source URLs/hashes are in ../results/rail-monitor-source-observation.json. Classic and B-version characteristics must not be interchanged.

Vishay-TNPW-e3-2026.pdf and Diodes-BAV199-2026.pdf support the buffered rail candidate. URLs/hashes and incomplete Chinese sourcing are in ../results/rail-monitor-buffered-sources.json. Exact temperature/life test conditions must accompany each limit.

TI-REF50-O.pdf and precision-source-observation.json retain the precision-reference manufacturer source and dated exact domestic comparator/reference listing fields. The record links reused comparator/HC14 source hashes and the domestic shipping policy. Listings are not checkout confirmations.

onsemi-1N914-2024.pdf includes exact1N4148TR ordering and diode limits. KNSCHA-82CL0125-2023.pdf is the manufacturer approval for the220nF/63V candidate. Original URLs/hashes and dated Chinese listing observations are in ../results/ac-loss/source-observations.json. Hot leakage and film operating-temperature allocations remain unqualified; no purchasing release.
