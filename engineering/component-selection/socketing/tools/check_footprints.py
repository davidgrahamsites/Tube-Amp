"""Independent source/native/drill delta checks for the five DIP sockets.

Runs native tools on current CAD and temporary baseline boards under identical
project rules. It never edits CAD or treats existing failures as release passes.
"""
import collections,copy,hashlib,json,math,re,subprocess,sys,tempfile
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];W=ROOT/'engineering/whole-amp'
sys.path.insert(0,str(W/'tools'));import native_sexpr as v
sys.path.insert(0,str(W/'control-switching/tools'))
from check_drills import export,read_hits,CLI
from check_reset_edges import graph,pad_map

def old(p,base):return subprocess.check_output(['/usr/bin/git','show',base+':'+str(p.relative_to(ROOT))],cwd=ROOT).decode()
def run(args):
    p=subprocess.run([CLI,*map(str,args)],capture_output=True,text=True,timeout=90)
    assert p.returncode==0,(args,p.stdout,p.stderr)

def verify_pad(p,n,pin):
    assert int(p[1].strip('"'))==pin
    assert p[2]=='thru_hole'
    assert p[3]==('roundrect' if pin==1 else 'circle')
    assert v.field(p,'drill')[1:]==['1.0']
    assert list(map(float,v.field(p,'size')[1:]))==[1.6,1.6]
    xy=list(map(float,v.field(p,'at')[1:3]));expected=[0 if pin<=n//2 else 7.62,2.54*(pin-1 if pin<=n//2 else n-pin)]
    assert all(abs(a-b)<1e-6 for a,b in zip(xy,expected))

def main():
    c=json.loads((M/'footprint-contract.json').read_text());assign=c['assignments'];base=c['baseline_commit'];sources=[M/'footprint-contract.json',M/'socket-envelope.json']
    cir=W/'reverb-600/circuit.json';expected=json.loads(old(cir,base));now=json.loads(cir.read_text());sources.append(cir)
    for row in expected['components']:
        if row['reference'] in assign:row['footprint']='Renegade_Selected:'+assign[row['reference']]
    assert expected==now
    for p in (W/'reverb-600/cad').glob('*.kicad_sch'):
        a=v.parse(old(p,base));b=v.parse(p.read_text())
        for sym in v.children(a,'symbol'):
            props={x[1].strip('"'):x for x in v.children(sym,'property')};ref=props['Reference'][2].strip('"')
            if ref in assign:props['Footprint'][2]=json.dumps('Renegade_Selected:'+assign[ref])
        assert a==b,p
        sources.append(p)
    for name in set(assign.values()):
        p=M.parent/'footprints/Renegade_Selected.pretty'/(name+'.kicad_mod');f=v.parse(p.read_text());sources.append(p)
        n=14 if 'DIP14' in name else 8;pads=sorted(v.children(f,'pad'),key=lambda x:int(x[1].strip('"')))
        assert len(pads)==n
        for i,pad in enumerate(pads,1):verify_pad(pad,n,i)
    bad=copy.deepcopy(pads[0]);v.field(bad,'drill')[1]='0.8'
    try:verify_pad(bad,n,1)
    except AssertionError:pass
    else:raise AssertionError('Undersize drill negative control escaped')
    bad=copy.deepcopy(pads[0]);v.field(bad,'at')[1]='7.62'
    try:verify_pad(bad,n,1)
    except AssertionError:pass
    else:raise AssertionError('Mirrored pin1 negative control escaped')
    report={};total=0
    with tempfile.TemporaryDirectory(prefix='renegade-socket-native-') as td:
        t=Path(td)
        for name in ['Control','Reverb']:
            p=W/'pcb-measured-r/boards'/('Renegade_'+name+'.kicad_pcb');sources.append(p)
            a=v.parse(old(p,base));b=v.parse(p.read_text());aa=v.fps(a);bb=v.fps(b)
            assert pad_map(a)==pad_map(b)
            followup=W/'pcb-measured-r/u12-routing-contract.json'
            routed_followup=False
            if name=='Control':
                sys.path.insert(0,str(W/'pcb-measured-r/tools'))
                from check_remaining_branches import verify_current as verify_remaining
                b=verify_remaining(name,b);bb=v.fps(b)
                sources.extend([W/'pcb-measured-r/remaining-branches-contract.json',
                    W/'pcb-measured-r/tools/check_remaining_branches.py'])
            if name=='Reverb' and followup.exists():
                # Validate the entire later board against its exact routing
                # baseline before projecting it back for the socket-only delta.
                # This is not a blanket exemption for subsequent copper edits.
                sys.path.insert(0,str(W/'pcb-measured-r/tools'))
                from check_u12_routing import verify_current as verify_routing
                route=json.loads(followup.read_text())
                route_before=v.parse(old(p,route['baseline_commit']))
                verify_routing(route_before,b,route)
                b=route_before;bb=v.fps(b);routed_followup=True
                sources.extend([followup,W/'pcb-measured-r/tools/check_u12_routing.py',
                    W/'pcb-measured-r/branch-routing-contract.json',W/'pcb-measured-r/tools/check_branch_routing.py'])
            expected_removed=collections.Counter();expected_added=collections.Counter()
            # Strip only declared package metadata/graphics and drill size;
            # every other native atom, including all routing, must be identical.
            for ref in assign:
                if ref not in aa:continue
                f0,f1=aa[ref],bb[ref];n=14 if ref in ['U1','U2'] else 8
                assert f1[1]==json.dumps('Renegade_Selected:'+assign[ref])
                for pad in v.children(f1,'pad'):verify_pad(pad,n,int(pad[1].strip('"')))
                for f in [f0,f1]:
                    f[1]='"NORMALIZED"';f[:]=[x for x in f if not (isinstance(x,list) and (x[0].startswith('fp_') or x[0] in ['model','descr','tags']))]
                for p0,p1 in zip(v.children(f0,'pad'),v.children(f1,'pad')):
                    assert v.field(p0,'drill')[1]=='0.8';assert v.field(p1,'drill')[1]=='1.0'
                    at=v.field(f0,'at');assert len(at)==3 or float(at[3])==0
                    x,y=map(float,at[1:3]);px,py=map(float,v.field(p0,'at')[1:3])
                    # Excellon uses three decimals, with KiCad's native rounding.
                    xy=(round(x+px,3),round(-y-py,3))
                    expected_removed[(*xy,.8)]+=1;expected_added[(*xy,1.0)]+=1
                    v.field(p1,'drill')[1]='0.8';total+=1
            if name=='Control':
                r=c['local_clearance_repair'];v.field(aa['C352'],'at')[2]=str(r['to_y_mm'])
                count=0
                for seg in v.children(a,'segment'):
                    uid=v.field(seg,'uuid')[1].strip('"')
                    if uid not in r['track_endpoint_y_changes']:continue
                    count+=1
                    for k,(prior,after) in r['track_endpoint_y_changes'][uid].items():
                        assert float(v.field(seg,k)[2])==prior;v.field(seg,k)[2]=str(after)
                    start,end=[list(map(float,v.field(seg,k)[1:3])) for k in ['start','end']]
                    dx,dy=[abs(start[i]-end[i]) for i in range(2)]
                    assert min(dx,dy)<1e-7 or abs(dx-dy)<1e-7
                    assert float(v.field(seg,'width')[1])>=.3
                assert count==4
            assert a==b,'Unrelated native edit: '+name
            before=t/name/'before'/p.name;before.parent.mkdir(parents=True);before.write_text(old(p,base))
            for extension in ['.kicad_pro','.kicad_dru']:
                q=p.with_suffix(extension)
                if q.exists():before.with_suffix(extension).write_bytes(q.read_bytes());sources.append(q)
            table=(p.parent/'fp-lib-table').read_text().replace('${KIPRJMOD}/../../../component-selection',str(ROOT/'engineering/component-selection')).replace('${KIPRJMOD}/../../libraries',str(W/'libraries'))
            (before.parent/'fp-lib-table').write_text(table)
            d0,d1=export(before,t/name/'drill-before'),export(p,t/name/'drill-after')
            hits0,hits1=read_hits(d0['PTH']),read_hits(d1['PTH'])
            assert hits0-hits1==expected_removed,(name,hits0-hits1,expected_removed)
            assert hits1-hits0==expected_added
            assert read_hits(d0['NPTH'])==read_hits(d1['NPTH'])
            slots=lambda s:[l for l in s.splitlines() if 'G85' in l or l.startswith(('G00','G01','M15','M16'))]
            assert all(slots(d0[k])==slots(d1[k]) for k in d0)
            drcs=[]
            for label,path in [('before',before),('after',p)]:
                out=M/'results'/f'socket-{name.lower()}-{label}-drc.json'
                run(['pcb','drc','--format','json','-o',out,path]);drcs.append(json.loads(out.read_text()))
            assert drcs[0]['violations']==drcs[1]['violations'],name+' changed DRC findings'
            # Ratsnest chooses a new spanning tree after movement; compare open
            # connection counts by net, not arbitrary nearest-item descriptions.
            def open_nets(drc):
                out=collections.Counter()
                for item in drc['unconnected_items']:
                    nets={re.search(r'\[([^]]+)\]',i['description']).group(1) for i in item['items']}
                    assert len(nets)==1
                    out[next(iter(nets))]+=1
                return out
            assert open_nets(drcs[0])==open_nets(drcs[1])
            report[name]=dict(changed_round_plated_holes=sum(expected_added.values()),other_drills_slots_and_nets_unchanged=True,
                copper_delta='four C352 endpoint adjustments plus separately verified three-branch repair' if name=='Control' else ('separate U12 and branch routing contracts verified exactly' if routed_followup else 'unchanged'),unconnected_counts_by_net=dict(open_nets(drcs[1])),
                drc_violations=len(drcs[1]['violations']),unconnected=len(drcs[1]['unconnected_items']),new_violations=0)
        assert total==52
        sch=W/'reverb-600/cad/Renegade_220V_Reverb.kicad_sch';xml=M/'results/socket-netlist.xml';erc=M/'results/socket-erc.json'
        run(['sch','export','netlist','--format','kicadxml','-o',xml,sch]);assert graph(xml)==graph(W/'control-switching/results/edge-after.xml')
        run(['sch','erc','--format','json','-o',erc,sch]);a=json.loads(erc.read_text());b=json.loads((W/'control-switching/results/edge-after-erc.json').read_text())
        a.pop('date',None);b.pop('date',None);assert a==b
    result=dict(passed=True,baseline_commit=base,boards=report,changed_holes=total,source_and_schematic_only_footprint_metadata_changed=True,native_netlist_unchanged=True,
      negative_controls_rejected=['undersize drill','mirrored pin1'],fabrication_ready=False,
      source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (M/'results/footprint-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))
if __name__=='__main__':main()
