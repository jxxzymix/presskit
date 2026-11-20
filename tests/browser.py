from pathlib import Path
import os, json, mimetypes, io
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; BASE='https://jxxzy.test/presskit/'; mock=('--real-assets' not in __import__('sys').argv)
# Local browser routes serve exact candidate HTML/CSS/JS, and use actual assets where present.
# Network to external sites is intentionally mocked, not claimed as a streaming test.
img=io.BytesIO();Image.new('RGB',(800,1000),'#334252').save(img,'PNG');placeholder=img.getvalue()
errors=[];layout=[];interactions=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None),headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':390,'height':844},service_workers='block',reduced_motion='reduce')
    def handler(route):
        from urllib.parse import urlparse,unquote
        u=urlparse(route.request.url)
        if not route.request.url.startswith(BASE):
            route.fulfill(status=200,content_type='text/html',body='<html><body>External media mock</body></html>') if route.request.resource_type=='document' else route.abort();return
        f=ROOT/unquote(u.path.removeprefix('/presskit/'))
        if f.is_file():route.fulfill(status=200,content_type=mimetypes.guess_type(str(f))[0] or 'application/octet-stream',body=f.read_bytes())
        elif mock and f.suffix.lower() in ('.png','.jpg','.webp','.jpeg'):route.fulfill(status=200,content_type='image/png',body=placeholder)
        else:route.fulfill(status=404,body='Missing resource')
    context.route('**/*',handler);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    names=sorted(p.name for p in ROOT.glob('*.html') if p.name not in ('404.html','offline.html'))
    widths=[320,360,390,430,768,1000,1024,1440,1920] if os.getenv('FULL_TEST')=='1' else [320,390,768,1024,1440]
    for n in names:
        for w in widths if not n.startswith('track-') else [320,1440]:
            page.set_viewport_size({'width':w,'height':844 if w<700 else 900});page.goto(BASE+n,wait_until='domcontentloaded');page.wait_for_timeout(35)
            check=page.evaluate('''()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,nav:document.querySelector('.nav')?.scrollWidth||0,headings:[...document.querySelectorAll('main h1,main h2')].filter(e=>e.getBoundingClientRect().width>0&&e.scrollWidth>e.clientWidth+3).map(e=>e.textContent.slice(0,60))})''')
            if check['scroll']>w+2 or check['nav']>w+2 or check['headings']:layout.append([n,w,check])
    page.set_viewport_size({'width':390,'height':844});page.goto(BASE+'music.html');page.wait_for_selector('.track');page.locator('[data-filter="youtube"]').click();assert page.locator('.track:visible').count()==8
    page.locator('[data-filter="soundcloud"]').click();assert page.locator('.track:visible').count()==14
    page.locator('#search').fill('no such track');assert page.locator('.track:visible').count()==0;page.locator('#search').fill('');page.locator('[data-filter="all"]').click();assert page.locator('.track:visible').count()==22;interactions.append('music filter and search')
    page.locator('#track-1 .save-track').click();page.goto(BASE+'collection.html');assert page.locator('.track:visible').count()==1;page.locator('#track-1 .save-track').click();assert page.locator('.track:visible').count()==0;interactions.append('garage persistence and removal')
    page.goto(BASE+'music.html');page.locator('#track-1 [data-queue]').click();page.locator('#track-1 [data-play]').click();assert page.locator('#pit-embed iframe').count()==1;page.evaluate("window._frame=document.querySelector('#pit-embed iframe')");page.locator('.mobile-dock a[href="shows.html"]').click();page.wait_for_url('**/shows.html');assert page.evaluate("window._frame===document.querySelector('#pit-embed iframe')");page.go_back();page.wait_for_selector('.page-music');assert page.evaluate("window._frame===document.querySelector('#pit-embed iframe')");page.locator('[data-queue-open]').click();assert page.locator('#queue-list .queue-row').count()==1;page.locator('[data-queue-close]').click();page.locator('[data-player-close]').click();assert page.locator('#pit-embed iframe').count()==0;interactions.append('player persistence, back navigation, queue, close (mocked media)')
    page.goto(BASE+'music.html');page.locator('#search').fill('nonexistent');page.locator('[data-command]').first.click();page.locator('#command-input').fill('panah asmara');page.locator('#command-results a').first.click();assert page.locator('#track-1').is_visible();assert page.locator('#search').input_value()=='';interactions.append('same-page command search clears filters')
    page.goto(BASE+'gallery.html');page.locator('[data-gallery-filter="portrait"]').click();page.locator('[data-photo]:visible').first.click();assert page.locator('.modal-controls small').inner_text().startswith('1 / ');page.locator('[data-photo-next]').click();assert page.locator('.modal-controls small').inner_text().startswith('2 / ');page.locator('[data-close]').click();interactions.append('filtered gallery counter/navigation')
    page.goto(BASE+'booking.html');assert page.locator('[data-step="0"]:visible').count()>0;page.locator('[data-wizard="2"]').click();assert page.locator('[data-step="2"]:visible').count()>0;page.locator('input[name=email]').fill('tester@example.com');assert 'tester@example.com' in page.locator('#brief-preview').text_content();page.locator('button[value=wa]').click();assert page.locator('[data-step="0"]:visible').count()>0;interactions.append('booking steps, preview and invalid-field routing')
    page.goto(BASE+'settings.html');page.locator('[data-mode=studio]').click();assert page.locator('html').evaluate("e=>e.classList.contains('studio-trim')");page.locator('[data-lang=id]').click();assert page.locator('#navlinks a[href="profile.html"]').get_attribute('lang')=='id';page.goto(BASE+'index.html');assert page.locator('#navlinks a[href="profile.html"]').inner_text()=='Profil';page.goto(BASE+'settings.html');page.locator('[data-lang=en]').click();interactions.append('visual mode and bilingual navigation')
    page.goto(BASE+'rider.html');page.locator('[data-rider-check]').first.check();assert page.locator('#rider-count').inner_text().startswith('1 /');page.locator('[data-rider-reset]').click();assert page.locator('#rider-count').inner_text().startswith('0 /');interactions.append('rider checklist')
    page.goto(BASE+'shows.html');page.locator('#event-search').fill('bandung');assert page.locator('#live article:visible').count()==1;interactions.append('live archive filter')
    page.goto(BASE+'epk.html');page.locator('[data-filter="youtube"]').click();page.emulate_media(media='print');assert page.locator('.track').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).display!=="none")');page.emulate_media(media='screen');interactions.append('EPK print restores filtered content')
    page.goto(BASE+'index.html');page.screenshot(path='/tmp/jxxzy-v4-mobile.png',full_page=False);page.set_viewport_size({'width':1440,'height':900});page.reload();page.screenshot(path='/tmp/jxxzy-v4-desktop.png',full_page=False);browser.close()
result={'layout_combinations':sum(2 if n.startswith('track-') else len(widths) for n in names),'layout_failures':layout,'js_errors':errors,'interaction_groups':interactions,'assets_mode':'substituted missing images' if mock else 'original assets','external_media':'mocked'}
print(json.dumps(result,ensure_ascii=False,indent=2));(ROOT/'browser-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));assert not layout and not errors
