"""Retain one lossless compressed waveform per HD-011 run; verify before removal."""
from pathlib import Path
import gzip,hashlib,json
M=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
rows=[]
for name in ['fixture','fixture-rejected','fault-550','startup-550','resetprobe-550','resetprobe-550-fine']:
 p=M/'results'/('monitor-'+name+'.csv');z=p.with_suffix('.csv.gz');receipt=json.loads(p.with_suffix('.json').read_text())
 if p.exists():
  raw=p.read_bytes();assert sha(raw)==receipt['csv_sha256']
  compressed=gzip.compress(raw,compresslevel=6,mtime=0);assert gzip.decompress(compressed)==raw
  z.write_bytes(compressed);p.unlink()
 else:compressed=z.read_bytes();raw=gzip.decompress(compressed);assert sha(raw)==receipt['csv_sha256']
 rows.append(dict(file=z.name,compressed_sha256=sha(compressed),raw_sha256=sha(raw),raw_bytes=len(raw),compressed_bytes=len(compressed)))
(M/'results/monitor-waveforms.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Packed',len(rows),'waveforms')
