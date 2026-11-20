from pathlib import Path
import fitz
root=Path(__file__).resolve().parents[1]/'assets'
for filename,pages,min_images in [('JXXZY_PRESSKIT_2026_RACING_V4.pdf',22,30),('JXXZY_QUICK_EPK_V4.pdf',3,3)]:
    d=fitz.open(root/filename)
    assert len(d)==pages,(filename,len(d))
    assert len(d.get_toc())==pages
    images=sum(len(p.get_images()) for p in d)
    assert images>=min_images,(filename,images)
    assert all('LAYOUT PROOF' not in p.get_text() and 'ORIGINAL ASSET PENDING' not in p.get_text() for p in d), 'Preview PDF must not be deployed'
    assert all(p.get_text().strip() for p in d)
    print(filename, pages,'pages',images,'image references',sum(len(p.get_links()) for p in d),'links')
