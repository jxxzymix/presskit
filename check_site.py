from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,sys
root=Path(__file__).resolve().parent
assets=set(json.loads((root/'asset-manifest.json').read_text()))
class Check(HTMLParser):
    def __init__(self): super().__init__(); self.ids=set();self.refs=[];self.duplicate=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=='id':
                if v in self.ids:self.duplicate.append(v)
                self.ids.add(v)
            if k in ('src','href') and v:self.refs.append(v)
docs={}; errors=[]; count=0
for p in root.glob('*.html'):
    d=Check();d.feed(p.read_text(encoding='utf-8'));docs[p.name]=d;errors.extend(p.name+': duplicate '+i for i in d.duplicate)
for name,d in docs.items():
    for ref in d.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc or u.path.startswith('/'):continue
        count+=1;target=u.path or name
        if not (root/target).exists() and not (target.startswith('assets/') and target[7:] in assets):errors.append(name+': missing '+target)
        if u.fragment and target in docs and u.fragment not in docs[target].ids:errors.append(name+': missing '+ref)
print(len(docs),'HTML pages;',count,'local references checked;',len(errors),'errors')
print('Original binary assets present:',sum((root/'assets'/p).exists() for p in assets),'/',len(assets))
if errors:print('\n'.join(errors));sys.exit(1)
