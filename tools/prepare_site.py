"""Normalize source metadata using actual image dimensions before staging."""
from pathlib import Path
import json
from bs4 import BeautifulSoup
from PIL import Image
root=Path(__file__).resolve().parents[1]
cat=json.loads((root/'data/catalog.json').read_text());(root/'assets/catalog.js').write_text('window.JXXZY_CATALOG = '+json.dumps(cat,ensure_ascii=False)+';\n')
sizes={}
for file in root.glob('*.html'):
    doc=BeautifulSoup(file.read_text(),'html.parser')
    for img in doc.select('img[src]'):
        name=img['src'];path=root/name
        if name.startswith('assets/') and path.is_file():
            if name not in sizes:
                with Image.open(path) as image:sizes[name]=image.size
            img['width'],img['height']=map(str,sizes[name])
    file.write_text(str(doc),encoding='utf-8')
print('Verified image dimensions:',len(sizes))
