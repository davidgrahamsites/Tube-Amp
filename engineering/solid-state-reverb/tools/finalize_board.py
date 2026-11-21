import pcbnew as p
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'pcb/Renegade_Reverb.kicad_pcb';b=p.LoadBoard(str(path))
for old in list(b.Zones()):b.Remove(old)
# Continuous reference copper for recovery and buffer currents, in addition to routed ground.
z=p.ZONE(b);z.SetLayer(p.B_Cu);z.SetNetCode(b.FindNet('GND').GetNetCode());z.SetLocalClearance(p.FromMM(.3));z.SetMinThickness(p.FromMM(.25));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.4));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
z.Outline().NewOutline()
for x,y in [(9,1.5),(151,1.5),(151,9),(158.5,9),(158.5,91),(151,91),(151,98.5),(9,98.5),(9,91),(1.5,91),(1.5,9),(9,9)]:z.Outline().Append(p.FromMM(x),p.FromMM(y))
b.Add(z);p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b);print('Added and filled bottom GND zone')
