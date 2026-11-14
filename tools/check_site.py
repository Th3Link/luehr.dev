"""Check rendered HTML, local links, language pairs and JSON-LD without dependencies."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids=set(); self.links=[]; self.h1=0; self.canonical=[]; self.alternates={}; self.lang=None; self.schema=[]; self.in_schema=False; self.json=''
        self.meta={}; self.title=''; self.in_title=False; self.in_head=False; self.headings=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html': self.lang=a.get('lang')
        if tag=='h1': self.h1+=1
        if re.fullmatch(r'h[1-6]',tag): self.headings.append(int(tag[1]))
        if tag=='head': self.in_head=True
        if tag=='title' and self.in_head: self.in_title=True
        if tag=='meta': self.meta[a.get('name') or a.get('property')]=a.get('content','')
        if tag=='img':
            assert 'alt' in a and 'width' in a and 'height' in a, 'Image needs alt text and dimensions'
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id: {a["id"]}'
            self.ids.add(a['id'])
        if tag=='link' and a.get('rel')=='canonical': self.canonical.append(a['href'])
        if tag=='link' and a.get('rel')=='alternate': self.alternates[a['hreflang']]=a['href']
        if tag in ['a','link','img','script']:
            target=a.get('href') or a.get('src')
            if target: self.links.append(target)
        if tag=='script' and a.get('type')=='application/ld+json': self.in_schema=True; self.json=''
    def handle_data(self,data):
        if self.in_schema: self.json+=data
        if self.in_title: self.title+=data
    def handle_endtag(self,tag):
        if tag=='head': self.in_head=False
        if tag=='title': self.in_title=False
        if tag=='script' and self.in_schema:
            self.schema.append(json.loads(self.json)); self.in_schema=False

pages={}
for file in ROOT.rglob('*.html'):
    if '.git' in file.parts: continue
    page=Page(file.read_text()); pages[file]=page
    assert page.h1==1,(file,page.h1)
    assert len(page.canonical)==1,file
    assert page.lang in ['de','en'],file
    assert {'de','en','x-default'}<=page.alternates.keys(),file
    assert page.schema,file
    assert page.title.strip(),file
    for key in ['description','og:title','og:description','og:url','og:image','og:locale']:
        assert page.meta.get(key),(file,key)
    assert 'noindex' not in page.meta.get('robots','').lower(),file
    assert page.canonical[0]==page.meta['og:url'],file
    previous=0
    for heading in page.headings:
        assert heading<=previous+1,(file,'Skipped heading level')
        previous=heading
assert len({p.title for p in pages.values()})==len(pages),'Duplicate page titles'
assert len({p.meta['description'] for p in pages.values()})==len(pages),'Duplicate meta descriptions'
for file,page in pages.items():
    for target in page.links:
        url=urlsplit(target)
        if url.scheme or url.netloc: continue
        resolved=(ROOT / unquote(url.path).lstrip('/')) if url.path.startswith('/') else file.parent / unquote(url.path)
        if not url.path: resolved=file
        if resolved.is_dir(): resolved=resolved/'index.html'
        assert resolved.exists(),f'{file.name}: missing {target}'
        if url.fragment and resolved in pages: assert unquote(url.fragment) in pages[resolved].ids, f'{file.name}: missing anchor {target}'
    for language in ['de','en']:
        target=ROOT/urlsplit(page.alternates[language]).path.lstrip('/')
        if target.is_dir(): target=target/'index.html'
        other=pages[target]
        assert other.lang==language,(file,language)
        assert other.alternates==page.alternates,(file,'non-reciprocal language links')
    assert page.alternates[page.lang]==page.canonical[0],(file,'Canonical does not match language URL')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
sitemap=ET.parse(ROOT/'sitemap.xml')
assert {el.text for el in sitemap.findall('s:url/s:loc',ns)}=={p.canonical[0] for p in pages.values()}
print(f'PASS: {len(pages)} HTML pages, local links, anchors, language pairs, canonical URLs, JSON-LD and sitemap')
for path, language in [('rust-fuer-engineering-manager.html','de'),('rust-for-engineering-managers.html','en')]:
    text=(ROOT/path).read_text()
    assert ('500 € zzgl. MwSt.' in text and '700 € zzgl. MwSt.' in text) if language=='de' else ('€500 plus VAT' in text and '€700 plus VAT' in text)
print('PASS: unique titles, social metadata, heading hierarchy, image dimensions and manager VAT prices')
courses=0
for file,page in pages.items():
    graph=page.schema[0]['@graph']
    assert {'Person','WebSite'}<={node['@type'] for node in graph},file
    for node in graph:
        if node['@type']=='Course':
            courses+=1
            assert node['url']==page.canonical[0],file
            assert node['inLanguage']==page.lang,file
            assert node['name'] and node['description'],file
            assert node['provider']['@id']=='https://luehr.dev/#person',file
        if node['@type']=='BreadcrumbList':
            assert [item['position'] for item in node['itemListElement']]==list(range(1,len(node['itemListElement'])+1)),file
assert courses==8,f'Expected eight localized courses, found {courses}'
print('PASS: eight localized courses with matching URLs and providers; ordered breadcrumbs')

def luminance(color):
    value=color.lstrip('#')
    if len(value)==3: value=''.join(c*2 for c in value)
    rgb=[int(value[i:i+2],16)/255 for i in (0,2,4)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))

css=(ROOT/'style.css').read_text()
for theme,selector in [('light',r':root\s*'),('dark',r':root\[data-theme=dark\]\s*')]:
    block=re.search(selector+r'\{([^}]+)\}',css).group(1)
    colors=dict(re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]+)',block))
    for foreground,background in [('text','bg'),('text','surface'),('muted','bg'),('muted','surface'),('accent','bg'),('accent','surface'),('button-text','accent')]:
        dark,light=sorted([luminance(colors[foreground]),luminance(colors[background])])
        ratio=(light+.05)/(dark+.05)
        assert ratio>=4.5,(theme,foreground,background,ratio)
print('PASS: WCAG AA text and button contrast in both color themes')

# Keep the original engineering detail and personal profile visible during future redesigns.
content=json.loads((ROOT/'tools/existing-content.json').read_text())
for language,path in [('en','index.html'),('de','de/index.html')]:
    text=(ROOT/path).read_text()
    for group in ['services','expertise']:
        for item in content[group]:
            assert escape(item['title'][language]) in text,(path,'Missing category',item['title'][language])
            for topic in item['items'][language]:
                assert escape(topic) in text,(path,'Missing expertise',topic)
    for project in ['ipv6-router-advertisement','homeautomation','curvyo']:
        assert f'<article id="{project}">' in text,(path,'Missing project',project)
    assert text.count('class="social-link"')==5,(path,'Missing contact buttons')
    assert ('Just Marc is perfectly fine.' if language=='en' else 'Marc reicht völlig.') in text,path
print('PASS: complete engineering content, three project blocks, five contact buttons and personal introduction')
