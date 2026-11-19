from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote
import json, shutil, sys
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parent
base="https://raw.githubusercontent.com/jxxzymix/presskit/a5b134c816fdc61c51ea9090125bb617c84b1484/assets/"
items=json.loads((root/'asset-manifest.json').read_text())
def get(name):
    dest=root/'assets'/name
    if dest.is_file() and dest.stat().st_size: return name, True
    dest.parent.mkdir(parents=True,exist_ok=True)
    try:
        with urlopen(Request(base+quote(name),headers={'User-Agent':'JXXZY-asset-setup'}),timeout=90) as src, open(str(dest)+'.tmp','wb') as out: shutil.copyfileobj(src,out)
        Path(str(dest)+'.tmp').replace(dest)
        return name,True
    except Exception as e:
        Path(str(dest)+'.tmp').unlink(missing_ok=True)
        print(name, e)
        return name,False
with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(get,items))
print(sum(ok for _,ok in results),'/',len(results),'original assets available')
sys.exit(0 if all(ok for _,ok in results) else 1)
