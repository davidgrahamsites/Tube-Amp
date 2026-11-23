"""Screen a decoupled SEND branch. Electrical loading, not galvanic isolation."""
import json
import math
from run import ac_case, OUT, sp
from fixture import fingerprint

def main():
    rows=[]
    changes=[]
    for channel in ['clean','dirty']:
        for volume in [.01,.25,1]:
            for tone in [0,.5,1]:
                for stimulus in ['dry','wet']:
                    group=[]
                    for mode in ['native','send-isolated','send-isolated-short']:
                        row,deck,_=ac_case(channel=channel,volume=volume,tone=tone,stimulus=stimulus,mode=mode,amp=0)
                        rows.append(row);group.append(row)
                        if volume==.25 and tone==.5 and stimulus=='dry':
                            (OUT/f'{channel}-{mode}.cir').write_text(deck)
                    for row in group[1:]:
                        for hz in ['82.4','1000','5000']:
                            for node in ['PI_G1','SEND_IN']:
                                ref=group[0]['points'][hz]['magnitude'][node]
                                if ref>1e-12:
                                    changes.append(dict(config=row['config'],frequency=hz,node=node,
                                        delta_dB=20*math.log10(row['points'][hz]['magnitude'][node]/ref)))
    worst=max(changes,key=lambda x:abs(x['delta_dB']))
    result=dict(source_hashes=fingerprint(),cases=rows,comparisons=changes,
                worst_change=worst,screen_limit_dB=.5,
                screen_pass=abs(worst['delta_dB'])<=.5,
                limitation='Ideal unlimited follower. No real amplifier, clamp, fault-current, noise or return recovery qualification.')
    (OUT/'send-isolation-summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cases=len(rows),worst=worst,screen_pass=result['screen_pass']),indent=2))

if __name__=='__main__':
    try:main()
    finally:(OUT/'send-isolation.log').write_text('\n'.join(line.rstrip() for line in sp.logs)+'\n')
