from pathlib import Path
import sys,json,shutil
root=Path(__file__).resolve().parents[1]; out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
required=json.loads((root/'asset-manifest.json').read_text())+['racing.css','experience.css','signature.css','signature.js','catalog.js','icon.svg','icon-192.png','icon-512.png','JXXZY_PRESSKIT_2026_RACING_V4.pdf','JXXZY_QUICK_EPK_V4.pdf']
for name in sorted(set(required)):
    src=root/'assets'/name; dst=out/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
print('Staged',len(set(required)),'assets only')
