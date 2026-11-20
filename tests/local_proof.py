from pathlib import Path
import re,json,base64,io
from PIL import Image
from bs4 import BeautifulSoup as B
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
css='\n'.join((ROOT/'assets'/f).read_text() for f in ['racing.css','experience.css','signature.css']);css=re.sub(r'@import[^;]+;','',css)
img=io.BytesIO();Image.new('RGB',(800,1000),'#354458').save(img,'PNG');placeholder='data:image/png;base64,'+base64.b64encode(img.getvalue()).decode()
code=(ROOT/'assets/catalog.js').read_text()+'\n'+(ROOT/'assets/signature.js').read_text()
# Browser navigation is prohibited locally. Inject original code, substitute only asset geometry and storage, and test DOM interactions.
shim='''<script>const mem={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>mem[k]??null,setItem:(k,v)=>mem[k]=String(v),removeItem:k=>delete mem[k]}});window.testMem=mem;</script>'''
def content(name,mem={}):
 s=B((ROOT/name).read_text(),'html.parser');
 for x in s.select('script[src],link[rel=stylesheet],link[rel=preconnect],link[rel=preload],link[rel=manifest]'):x.decompose()
 for x in s.select('img'):x['src']=placeholder;x.attrs.pop('srcset',None)
 for x in s.select('video'):x.decompose()
 # player urls do not load; intercepted via mock frames on about:blank
 s.head.append(B('<style>'+css+'</style>','html.parser'));s.head.append(B('<base href="https://jxxzymix.github.io/presskit/">','html.parser'));s.head.append(B(shim,'html.parser'));s.head.append(B('<script>Object.assign(testMem,'+json.dumps(mem)+')</script>','html.parser'));s.body.append(B('<script>'+code+'</script>','html.parser'));return str(s)
layout=[];errors=[];groups=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(reduced_motion='reduce');pg=ctx.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.route('**/*',lambda r:r.abort())
 def load(n,mem={}):pg.set_content(content(n,mem),wait_until='domcontentloaded');pg.wait_for_timeout(25)
 # new page per load prevents repeated global listeners on the same document.
 def load(n,mem={}):
  global pg
  pg.close();pg=ctx.new_page();pg.set_viewport_size({'width':390,'height':844});pg.on('pageerror',lambda e:errors.append(str(e)));pg.route('**/*',lambda r:r.abort());pg.set_content(content(n,mem),wait_until='domcontentloaded');pg.wait_for_timeout(25)
 total=0
 for name in sorted(f.name for f in ROOT.glob('*.html') if f.name not in ('404.html','offline.html')):
  load(name)
  for w in ([320,1440] if name.startswith('track-') else [320,360,390,430,768,1000,1024,1440,1920]):
   total+=1;pg.set_viewport_size({'width':w,'height':844 if w<700 else 900});pg.wait_for_timeout(10)
   result=pg.evaluate('''()=>({scroll:document.documentElement.scrollWidth,nav:document.querySelector('.nav')?.scrollWidth||0,headings:[...document.querySelectorAll('main h1,main h2')].filter(e=>e.clientWidth>0&&e.scrollWidth>e.clientWidth+3).map(e=>e.textContent.slice(0,60))})''')
   if result['scroll']>w+2 or result['nav']>w+2 or result['headings']:layout.append([name,w,result])
 print('LAYOUT',total,json.dumps(layout),flush=True)
 load('music.html');pg.locator('[data-filter=youtube]').click();assert pg.locator('.track:visible').count()==8;pg.locator('[data-filter=soundcloud]').click();assert pg.locator('.track:visible').count()==14;pg.locator('#search').fill('fake track');assert pg.locator('.track:visible').count()==0;pg.locator('#search').fill('');pg.locator('[data-filter=all]').click();assert pg.locator('.track:visible').count()==22;groups.append('music filter/search')
 pg.locator('#track-1 .save-track').click();mem=pg.evaluate('testMem');load('collection.html',mem);assert pg.locator('.track:visible').count()==1;pg.locator('#track-1 .save-track').click();assert pg.locator('.track:visible').count()==0;groups.append('garage save/remove')
 load('music.html');pg.locator('#track-1 [data-queue]').click();pg.locator('#track-1 [data-play]').click();assert pg.locator('#pit-embed iframe').count()==1;pg.locator('[data-queue-open]').click();assert pg.locator('#queue-list .queue-row').count()==1;pg.locator('[data-queue-close]').click();pg.locator('[data-player-next]').click();pg.locator('[data-player-close]').click();assert pg.locator('#pit-embed iframe').count()==0;groups.append('player/queue controls, not streaming')
 load('gallery.html');pg.locator('[data-gallery-filter=portrait]').click();pg.locator('[data-photo]:visible').first.click();assert pg.locator('.modal-controls small').inner_text().startswith('1 / ');pg.locator('[data-photo-next]').click();assert pg.locator('.modal-controls small').inner_text().startswith('2 / ');pg.locator('[data-close]').click();groups.append('filtered gallery counter')
 load('booking.html');pg.locator('[data-wizard="2"]').click();pg.locator('input[name=email]').fill('tester@example.com');assert 'tester@example.com' in pg.locator('#brief-preview').text_content();pg.locator('button[value=wa]').click();assert pg.locator('[data-step="0"]:visible').count()>0;groups.append('booking wizard and validation')
 load('settings.html');pg.locator('[data-mode=studio]').click();assert pg.locator('html').evaluate("e=>e.classList.contains('studio-trim')");pg.locator('[data-lang=id]').click();assert pg.locator('html').get_attribute('lang')=='id';groups.append('visual and navigation language preferences')
 load('rider.html');pg.locator('[data-rider-check]').first.check();assert pg.locator('#rider-count').inner_text().startswith('1 /');pg.locator('[data-rider-reset]').click();assert pg.locator('#rider-count').inner_text().startswith('0 /');groups.append('rider checklist')
 load('shows.html');pg.locator('#event-search').fill('bandung');assert pg.locator('#live article:visible').count()==1;groups.append('live filter')
 load('epk.html');pg.locator('[data-filter=youtube]').click();pg.emulate_media(media='print');assert pg.locator('.track').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).display!=="none")');pg.emulate_media(media='screen');groups.append('EPK print restores filtered catalog')
 load('index.html');pg.locator('.menu').click();assert pg.locator('#navlinks').evaluate("e=>e.classList.contains('open')");pg.locator('.menu').click();pg.locator('[data-command]').first.click();pg.locator('#command-input').fill('panah asmara');assert pg.locator('#command-results a').count()==1;pg.locator('[data-command-close]').click();groups.append('mobile menu and command results');pg.screenshot(path='/tmp/jxxzy-v4-mobile.png');pg.set_viewport_size({'width':1440,'height':900});pg.screenshot(path='/tmp/jxxzy-v4-desktop.png');b.close()
result={'layout_combinations':total,'layout_failures':layout,'js_errors':errors,'interaction_groups':groups,'scope':'Chromium set_content, placeholder asset geometry, in-memory storage, blocked real navigation / streaming'};print(json.dumps(result,indent=2));(ROOT/'browser-results.json').write_text(json.dumps(result,indent=2));assert not layout and not errors
