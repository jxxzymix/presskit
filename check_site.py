from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, sys, re
root=Path(__file__).resolve().parent
assets=set(json.loads((root/'asset-manifest.json').read_text()))
strict='--require-assets' in sys.argv
class Check(HTMLParser):
    def __init__(self): super().__init__(); self.ids=set(); self.refs=[]; self.duplicate=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if not v: continue
            if k=='id':
                if v in self.ids:self.duplicate.append(v)
                self.ids.add(v)
            if k in ('src','href','poster','data-photo'):self.refs.append(v)
            if k=='srcset':self.refs.extend(x.strip().split()[0] for x in v.split(',') if x.strip())
            if k=='style':self.refs.extend(re.findall(r'url\([\'\"]?([^\)\'\"]+)[\'\"]?\)',v))
docs={}; errors=[]; count=0
for p in sorted(root.glob('*.html')):
    d=Check();d.feed(p.read_text(encoding='utf-8'));docs[p.name]=d;errors.extend(p.name+': duplicate '+i for i in d.duplicate)
for name,d in docs.items():
    for ref in d.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        path=unquote(u.path)
        if path.startswith('/presskit/'):path=path.removeprefix('/presskit/') or 'index.html'
        elif path.startswith('/'):continue
        count+=1;target=path or name
        if not (root/target).exists() and not (not strict and target.startswith('assets/') and target[7:] in assets):errors.append(name+': missing '+target)
        if u.fragment and target in docs and unquote(u.fragment) not in docs[target].ids:errors.append(name+': missing '+ref)
for filename in ['racing.css','experience.css','signature.css']:
    for ref in re.findall(r'url\([\'\"]?([^\)\'\"]+)[\'\"]?\)',(root/'assets'/filename).read_text()):
        if not urlsplit(ref).scheme and not (root/'assets'/ref).exists() and not (not strict and ref in assets):errors.append(filename+': missing '+ref)
missing=[p for p in sorted(assets) if not (root/'assets'/p).is_file() or not (root/'assets'/p).stat().st_size]
if strict:errors.extend('Missing original asset: '+x for x in missing)
print(len(docs),'HTML pages;',count,'local references checked;',len(errors),'errors')
print('Original binary assets present:',len(assets)-len(missing),'/',len(assets))
if errors:print('\n'.join(errors));sys.exit(1)
