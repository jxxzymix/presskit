"""Build the photo-rich Signature V4 PDFs from original repository assets.
Production is strict by default. --preview allows a marked text-only proof for local review.
"""
from pathlib import Path
import json, sys, textwrap, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from PIL import Image
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; D=json.loads((ROOT/'data/artist.json').read_text()); C=json.loads((ROOT/'data/catalog.json').read_text()); BASE='https://jxxzymix.github.io/presskit/'
preview='--preview' in sys.argv
W,H=A4; BG='#0a1019'; PANEL='#162331'; TEXT='#f6f8fb'; MUTED='#b7c9da'; CYAN='#72d5f6'; BLUE='#1664bf'; RED='#ef3656'
required=['jxxzy-logo-transparent.webp','press-portrait-cover.webp','press-portrait-front.webp','press-portrait-action.webp','press-crowd-main.webp','press-crowd-close.webp','press-live-fyne.webp','press-live-booth.webp','press-live-logo.webp','booking-stage.webp']+[x['img'].removeprefix('assets/') for x in C]
miss=[n for n in required if not (A/n).is_file()];
if miss and not preview: raise SystemExit('Original asset files required: '+', '.join(miss))

def color(c):return HexColor(c)
def rect(c,x,y,w,h,fill=PANEL,stroke=None):
    c.setFillColor(color(fill)); c.setStrokeColor(color(stroke or fill)); c.rect(x,y,w,h,fill=1,stroke=int(bool(stroke)))
def txt(c,s,x,y,size=12,fill=TEXT,font='Helvetica-Bold'):
    c.setFont(font,size);c.setFillColor(color(fill));c.drawString(x,y,str(s))
def para(c,s,x,y,w,size=13,leading=None,fill=MUTED,bold=False):
    style=ParagraphStyle('p',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=leading or size*1.42,textColor=color(fill),spaceAfter=0)
    a=Paragraph(escape(str(s)).replace('\n','<br/>'),style); _,h=a.wrap(w,H);a.drawOn(c,x,y-h);return y-h

def stripe(c,x,y,w=88,h=5):
    for i,col in enumerate((CYAN,BLUE,RED)):rect(c,x+w*i/3,y,w/3,h,col)
def image(c,name,x,y,w,h,contain=False):
    f=A/name
    if not f.is_file():
        rect(c,x,y,w,h,'#172333','#40546b');
        if w<100:txt(c,'ART',x+8,y+h/2,10,CYAN)
        else:txt(c,'ORIGINAL ASSET PENDING',x+12,y+h-22,9,CYAN);para(c,name,x+12,y+h-33,w-24,9)
        return
    im=Image.open(f).convert('RGBA'); iw,ih=im.size; scale=(min if contain else max)(w/iw,h/ih); nw,nh=iw*scale,ih*scale
    c.saveState();path=c.beginPath();path.rect(x,y,w,h);c.clipPath(path,stroke=0,fill=0);c.drawImage(ImageReader(im),x+(w-nw)/2,y+(h-nh)/2,nw,nh,mask='auto');c.restoreState()
def link(c,label,url,x,y,w=245):
    rect(c,x,y-25,w,28,'#1a3551','#47729c');txt(c,label,x+9,y-14,10,TEXT);c.linkURL(url,(x,y-25,x+w,y+3),relative=0,thickness=0)
def qrbox(c,url,x,y,s=70):
    widget=qr.QrCodeWidget(url); x1,y1,x2,y2=widget.getBounds();d=Drawing(s,s,transform=[s/(x2-x1),0,0,s/(y2-y1),0,0]);d.add(widget);rect(c,x-4,y-4,s+8,s+8,'#ffffff');renderPDF.draw(d,c,x,y)
def begin(c,i,total,kicker,title,subtitle=''):
    rect(c,0,0,W,H,BG);rect(c,0,H-12,W,12,'#101b29');stripe(c,0,H-12,W,4);txt(c,'JXXZY / SIGNATURE MOTORSPORT',32,H-40,10,CYAN);txt(c,f'2026 • {i:02d} / {total:02d}',W-140,H-40,10,MUTED)
    if preview:txt(c,'LAYOUT PROOF — ORIGINAL PHOTOS NOT EMBEDDED',32,H-58,8,RED)
    txt(c,kicker.upper(),32,H-85,11,CYAN);y=para(c,title.upper(),32,H-103,W-64,37,39,TEXT,True);stripe(c,32,y-13,110,6);y-=30
    if subtitle:y=para(c,subtitle,32,y,W-64,12,16,MUTED)-16
    rect(c,32,40,W-64,1,'#3c4f65');txt(c,'FUN. FLY. ENJOY.  /  INDEPENDENT ARTIST IDENTITY',32,24,8,MUTED);txt(c,f'{i:02d}',W-55,24,10,CYAN)
    c.bookmarkPage(f'p{i}');c.addOutlineEntry(f'{i:02d} {title}',f'p{i}',level=0);return y

def end(c):c.showPage()
def rows(c,items,y,columns=1):
    for title,body in items:
        h=max(60,26+math.ceil(len(body)/76)*17);rect(c,32,y-h,W-64,h-5,PANEL,'#36485b');txt(c,title,45,y-20,12,CYAN);para(c,body,45,y-27,W-90,12,16);y-=h+8
        if y<60:raise ValueError('Rows overrun')
    return y

def catalog(c,items,y):
    for t in items:
        image(c,t['img'].removeprefix('assets/'),32,y-53,53,53);title=t['title'];para(c,title,98,y-4,W-132,13,15,TEXT,True);txt(c,t['platform'].upper()+' / OPEN OFFICIAL RELEASE ↗',98,y-39,9,CYAN);c.linkURL(t['url'],(32,y-54,W-32,y),relative=0,thickness=0);y-=66
    return y

def cover(c,i,total,quick=False):
    rect(c,0,0,W,H,BG);stripe(c,0,H-12,W,12);image(c,'press-portrait-cover.webp',32,220,W-64,420,True);image(c,'jxxzy-logo-transparent.webp',32,H-160,170,100,True);txt(c,'QUICK ELECTRONIC PRESS KIT' if quick else 'OFFICIAL ELECTRONIC PRESS KIT',32,185,12,CYAN);txt(c,'JXXZY.',32,111,67,TEXT,'Helvetica-BoldOblique');txt(c,'FUN. FLY. ENJOY.',34,86,16,TEXT);txt(c,'DJ / PRODUCER / MUSIC EDITOR  •  INDONESIA',34,62,10,MUTED);qrbox(c,BASE+'epk.html',W-113,70,76);txt(c,'2026 / SIGNATURE MOTORSPORT',32,28,10,CYAN)
    if preview:txt(c,'LAYOUT PROOF — ORIGINAL PHOTOS NOT EMBEDDED',32,H-30,8,RED)
    c.bookmarkPage(f'p{i}');c.addOutlineEntry('Cover',f'p{i}',level=0);end(c)

def build(path,quick=False):
    c=canvas.Canvas(str(path),pagesize=A4,pageCompression=1);c.setTitle('JXXZY Signature Motorsport — '+('Quick EPK' if quick else 'Official EPK 2026'));c.setAuthor('JXXZY');total=3 if quick else 22;cover(c,1,total,quick)
    y=begin(c,2,total,'01 / artist fact sheet','Artist DNA','A genre-fluid DJ, producer and music editor based in Indonesia.');image(c,'press-portrait-front.webp',32,y-245,200,245);para(c,D['short_bio'],250,y,W-282,14,20,TEXT);para(c,'Official name: JXXZY\nPronunciation: Jexsiii\nFormat: Solo DJ\nOrigin: Indonesia\n9 genres / 22 selected tracks and sets',250,y-125,W-282,12,19);y-=270;para(c,D['bio_en'],32,y,W-64,13,19);link(c,'Open full biography',BASE+'profile.html',32,105);end(c)
    if quick:
        y=begin(c,3,total,'02 / promoter access','Booking & essentials','Direct inquiry. Confirm all arrangements with the artist.');y=rows(c,[('TECHNICAL','Professional Pioneer DJ / AlphaTheta ecosystem, 4-channel mixer, booth monitor, FOH and stable grounded power preferred.'),('HOSPITALITY','Guest list up to 10, water and soft drinks, secure artist area and agreed transport/accommodation. Full rider by agreement.'),('MUSIC','9 genres and 22 selected tracks and DJ sets. Browse official SoundCloud and YouTube.')],y);link(c,'WhatsApp booking','https://wa.me/'+D['booking_wa'],32,206);link(c,'Email artist','mailto:'+D['booking_email'],32,163);link(c,'Full electronic press kit',BASE+'epk.html',32,120);qrbox(c,BASE+'booking.html',W-122,111,78);end(c);c.save();return
    for i,language,key in [(3,'Indonesia','bio_id'),(4,'English','bio_en')]:
        y=begin(c,i,total,'02 / biography',language);image(c,'press-portrait-action.webp',32,y-255,W-64,255);para(c,D[key],32,y-280,W-64,15,23,TEXT);link(c,'Official artist profile',BASE+'profile.html',32,100);end(c)
    y=begin(c,5,total,'03 / identity','Racing philosophy','Independent artist identity inspired by the precision, movement and visual energy of motorsport.');image(c,'press-live-logo.webp',32,y-242,W-64,242);image(c,'jxxzy-logo-transparent.webp',32,y-405,175,140,True);para(c,'FUN. FLY. ENJOY.\nThe identity emphasizes movement, energy and artistic momentum. The official logo is unchanged. No affiliation with BMW or any motorsport team is implied.',230,y-275,W-262,14,20);link(c,'Brand identity guidelines',BASE+'brand.html',32,100);end(c)
    y=begin(c,6,total,'04 / sound','Nine routes','A flexible sound map, not a fixed genre boundary.');genres=[('Dutch','Bounce-driven club energy'),('Jungle Dutch','Percussive and tribal movement'),('Breakbeat','Broken rhythm and bass momentum'),('Breakfunk','Funk and playful bounce'),('Techno','Pressure, drive and peak tension'),('Indonesian Bounce','Local recognition with club energy'),('Baile Funk','Brazilian percussion and raw bass'),('Brazilian Funk','Fast, rhythmic, club-forward sound'),('Bolha','Brazilian-influenced bounce')];
    for j,(g,b) in enumerate(genres):
        row,col=divmod(j,2);x=32+col*(W-54)/2;yy=y-row*91;ww=(W-76)/2;rect(c,x,yy-80,ww,80,PANEL,'#3b5167');txt(c,g,x+10,yy-23,13,CYAN);para(c,b,x+10,yy-31,ww-20,12,16)
    link(c,'Explore Sound DNA',BASE+'sound.html',32,100);end(c)
    y=begin(c,7,total,'05 / performance','From open to peak','Crowd response, selection, pacing and transition are at the center of a JXXZY set.');image(c,'press-crowd-main.webp',32,y-250,W-64,250);y-=270;y=rows(c,[('OPEN / BUILD','Establish atmosphere and develop momentum.'),('LIFT / PEAK','Use rhythm, edits and selection to raise energy.'),('RESET / FINAL','Create dynamic contrast and close with the room in mind.')],y);end(c)
    y=begin(c,8,total,'06 / selected releases','Featured edits','Selected official catalog highlights.');catalog(c,[C[0],C[1],C[2],C[3],C[4],C[5]],y);link(c,'Discover the full music center',BASE+'music.html',32,102);end(c)
    y=begin(c,9,total,'07 / discography','SoundCloud catalog','Remaining selected tracks and edits.');catalog(c,C[6:14],y);link(c,'Official SoundCloud','https://soundcloud.com/jxxzyshn',32,83);end(c)
    y=begin(c,10,total,'08 / DJ sets','Mix archive','Selected official YouTube DJ sets.');catalog(c,C[14:],y);link(c,'Official YouTube','https://youtube.com/@jxxzymix',32,83);end(c)
    y=begin(c,11,total,'09 / live history','Selected appearances','Dates and other details are published only when confirmed.');image(c,'press-live-fyne.webp',32,y-200,W-64,200);y-=218
    for e in D['events']:
        txt(c,e['name'],32,y,13,TEXT);txt(c,e['description'],270,y,11,MUTED);rect(c,32,y-8,W-64,1,'#304257');y-=32
    link(c,'Official live archive',BASE+'shows.html',32,89);end(c)
    y=begin(c,12,total,'10 / photography','Live in frames','Official performance photography.');image(c,'press-crowd-main.webp',32,y-270,W-64,270);image(c,'press-crowd-close.webp',32,y-476,(W-76)/2,194);image(c,'press-portrait-action.webp',32+(W-52)/2,y-476,(W-76)/2,194);link(c,'View official gallery',BASE+'gallery.html',32,89);end(c)
    y=begin(c,13,total,'11 / event fit','Built for the room','Each performance is adapted to the agreed event context.');formats=['Nightclub','Festival','Campus','Private','Brand activation','After party','Showcase','B2B'];
    for j,g in enumerate(formats):
        row,col=divmod(j,2);x=32+col*(W-54)/2;yy=y-row*90;ww=(W-76)/2;rect(c,x,yy-78,ww,78,PANEL,'#40566b');txt(c,f'{j+1:02d}',x+10,yy-23,11,CYAN);para(c,g,x+10,yy-33,ww-20,19,21,TEXT,True)
    image(c,'booking-stage.webp',32,y-495,W-64,112);link(c,'Discuss your event',BASE+'booking.html',32,87);end(c)
    y=begin(c,14,total,'12 / technical rider','Ready to perform','Preferred professional DJ, stage and audio environment. Final details by agreement.');rows(c,[('DJ SYSTEM','Professional Pioneer DJ / AlphaTheta ecosystem preferred.'),('MIXER','Professional 4-channel mixer preferred.'),('BOOTH MONITOR','Dedicated booth monitor with accessible level control.'),('FOH / PA','Professional PA with adequate sub-bass and headroom.'),('POWER','Stable, grounded and protected power.'),('BOOTH','Stable surface, sufficient space and safe crowd separation.')],y);end(c)
    y=begin(c,15,total,'13 / stage planning','Stage plot','Illustrative schematic only — confirm exact equipment, placement and venue safety.');
    boxes=[('FOH L',32,y-110,155,75),('DJ BOOTH',200,y-110,196,75),('FOH R',410,y-110,153,75),('MONITOR',32,y-214,155,75),('PROTECTED POWER',200,y-214,196,75),('MONITOR',410,y-214,153,75),('SAFE CROWD SEPARATION / DANCEFLOOR',32,y-330,W-64,90)]
    for t,x,yy,w,h in boxes:rect(c,x,yy,w,h,PANEL,'#567592');para(c,t,x+10,yy+h-21,w-20,12,16,TEXT,True)
    para(c,'Maintain safe access for the artist and technical staff. Confirm final stage plan and all electrical requirements with the venue.',32,y-355,W-64,14,20);link(c,'Illustrative web stage plan',BASE+'stage.html',32,100);end(c)
    y=begin(c,16,total,'14 / audio routing','Signal flow','Illustrative routing, not a hardware-specific wiring diagram.');image(c,'press-live-booth.webp',32,y-220,W-64,220);y-=248;rows(c,[('INPUT','Approved DJ players / sources → professional mixer channels.'),('MASTER','Mixer master output → FOH / PA, with venue-engineer-approved routing.'),('BOOTH','Mixer booth output → dedicated monitor with accessible level control.'),('SOUNDCHECK','Verify routing, monitor, player/mixer operation, headroom and safe power.')],y);end(c)
    y=begin(c,17,total,'15 / hospitality','Artist care','Subject to venue policy, local law, event type, travel and final agreement.');rows(c,[('GUEST LIST','Up to 10 persons.'),('BEVERAGES','2 bottles Jameson, subject to applicable law and venue policy.'),('MIXERS','Standard mixers included.'),('HYDRATION','Water and soft drinks.'),('BACKSTAGE','Secure artist area preferred.'),('TRAVEL','Transport and accommodation when applicable.')],y);end(c)
    y=begin(c,18,total,'16 / brand guidelines','Official identity','Use the supplied JXXZY logo and approved promotional assets.');image(c,'jxxzy-logo-transparent.webp',32,y-220,W-64,220,True);y-=255
    for j,(cl,n) in enumerate([(BG,'CARBON'),(CYAN,'CYAN'),(BLUE,'BLUE'),(RED,'RACING RED')]):x=32+j*(W-64)/4;rect(c,x,y-58,(W-80)/4,58,cl,'#66788b');txt(c,n,x,y-76,9,TEXT);txt(c,cl,x,y-91,9,MUTED)
    para(c,'Do not stretch, distort or recolor the official logo. Preserve sufficient clear space. Obtain approval for promotion and photo use. This independent identity is motorsport-inspired, not affiliated with BMW.',32,y-119,W-64,13,19);link(c,'Official downloads',BASE+'downloads.html',32,100);end(c)
    y=begin(c,19,total,'17 / promoter toolkit','Ready to publish');y=para(c,D['short_bio'],32,y,W-64,16,24,TEXT)-36;y=para(c,D['mc'],32,y,W-64,22,30,CYAN,True)-35;y=para(c,'For complete Bahasa Indonesia and English biographies, stage introduction and approved assets, use the live media center. Confirm photo credits and publication permission with the artist.',32,y,W-64,14,20);image(c,'press-portrait-front.webp',32,y-190,160,180);link(c,'Media center',BASE+'media.html',210,y-45,300);link(c,'Download official assets',BASE+'downloads.html',210,y-88,300);end(c)
    y=begin(c,20,total,'18 / booking procedure','From inquiry to show');rows(c,[('01 / INQUIRY','Share event name, date, city, venue, duration and promoter contact.'),('02 / DISCUSS','Agree event format, budget, set time, production and logistics.'),('03 / CONFIRM','A booking is confirmed only after direct agreement; sending an inquiry is not confirmation.'),('04 / PREPARE','Coordinate technical and hospitality requirements, soundcheck and arrival.')],y);link(c,'Open booking wizard',BASE+'booking.html',32,146);qrbox(c,BASE+'booking.html',W-125,96,78);end(c)
    y=begin(c,21,total,'19 / official contacts','Let’s connect','Direct artist inquiry and official music channels.');image(c,'press-portrait-event.webp',32,y-210,175,210) if (A/'press-portrait-event.webp').is_file() or preview else image(c,'press-portrait-front.webp',32,y-210,175,210)
    for j,(name,url) in enumerate([('WhatsApp booking','https://wa.me/'+D['booking_wa']),('Email artist','mailto:'+D['booking_email']),('Official Instagram','https://instagram.com/jxxzyshn'),('Official SoundCloud','https://soundcloud.com/jxxzyshn'),('Official YouTube','https://youtube.com/@jxxzymix')]):link(c,name,url,226,y-14-j*40,337)
    para(c,'Booking email: '+D['booking_email']+'\nWhatsApp: +'+D['booking_wa'],32,y-238,W-64,14,22);qrbox(c,BASE+'contact.html',32,115,90);link(c,'Official website',BASE,150,185,300);end(c)
    y=begin(c,22,total,'20 / closing','Fun. Fly. Enjoy.');image(c,'press-crowd-main.webp',32,y-340,W-64,340);image(c,'jxxzy-logo-transparent.webp',32,y-515,220,156,True);qrbox(c,BASE, W-128,y-480,82);link(c,'JXXZY official website',BASE,32,92);end(c);c.save()

full=A/'JXXZY_PRESSKIT_2026_RACING_V4.pdf';quick=A/'JXXZY_QUICK_EPK_V4.pdf';build(full);build(quick,True);print('Generated',full.name,quick.name,'PREVIEW' if preview else 'WITH ORIGINAL ASSETS')
