# Exact tube signal resistors — November 12

Select the following1% metal-film parts from the dated mainland register. These preserve original resistances. Metal film is appropriate for low-noise signal circuitry; no premium “audio” markup or measured noise claim is assumed.

| References | MPN | LCSC SKU |
|---|---|---|
| R3,R8,R36,R37 | MFR50SFTE52-1K5 | C173144 |
| R11 | MFR50SFTE52-2K7 | C1373716 |
| R16 | MFR50SFTE52-1K8 | C1373587 |
| R29 | MF0207FTE52-82K | C723641 |
| R13,R14,R18,R19 | MF0207FTE52-470K | C513723 |
| R32 | MF0207FTE52-47K | C513696 |
| R33,R34 | MF0207FTE52-220K | C513655 |
| R28 | MF0207FTE52-10K | C513672 |
| R2,R10,R25,R27 | MF0207FTE52-1M | C1373811 |

Exact supplier URLs, November11 RMB prices/stock/MOQs are retained in candidate-register.json/.csv. Do not extend these selections to other references merely sharing a resistance, particularly DNP HV R100, the screen resistors or unresolved reverb interfaces.

Manufacturer Yageo-MFR.pdf gives MFR50S0.5W/70°C and300V maximum working voltage; Yageo-MF0.pdf gives MF0207 0.6W/70°C and350V. Both derate linearly to zero at155°C, and continuous voltage is further limited by sqrt(P×R). Their nominal body is6.3±0.5 by2.4±0.2mm; leads0.55±0.05mm. Standard formed10.16mm pitch is a planned assembly geometry, not a supplier preformed-lead promise.

select_signal_resistors.py produces57 nominal DC/temperature checks for19 references at70/100/125°C assumptions. All pass; maximum utilization43.842% at125°C. This screen retains400V stiff supply/-40V bias and generic tubes; no signal, high-line, startup, tube-fault, actual enclosure temperature or commercial model validation is implied. Exact footprint integration and transient review remain required. The already selected2W FMP100k plate-load parts remain separate.
