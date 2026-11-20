from pathlib import Path
import sys, fitz
root=Path(__file__).resolve().parents[1]
forbidden='motor'+'sport'
errors=[];count=0
for f in root.rglob('*'):
    if not f.is_file() or any(x in f.parts for x in ('.git','_site','__pycache__')):continue
    if f.suffix.lower() in ('.html','.css','.js','.json','.md','.txt','.xml','.yml','.yaml','.py','.webmanifest','.svg','.bat'):
        count+=1
        if forbidden in (str(f.relative_to(root))+'\n'+f.read_text(encoding='utf-8',errors='replace')).casefold():errors.append(str(f.relative_to(root)))
    elif f.suffix.lower()=='.pdf' and f.name in ('JXXZY_PRESSKIT_2026_RACING_V4.pdf','JXXZY_QUICK_EPK_V4.pdf'):
        count+=1
        with fitz.open(f) as d:
            if forbidden in (str(d.metadata)+'\n'.join(p.get_text() for p in d)).casefold():errors.append(f.name)
            if '--production' in sys.argv and any('LAYOUT PROOF' in p.get_text() for p in d):errors.append(f.name+' is a layout proof')
print('Brand audit:',count,'files;',len(errors),'violations')
if errors: print('\n'.join(errors));sys.exit(1)
