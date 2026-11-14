"""Guard the responsive-image transfer budget without browser or imaging dependencies."""
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = (192, 320, 480, 720)

class Portrait(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.source=None; self.image=None; self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='source' and attrs.get('type')=='image/webp': self.source=attrs
        if tag=='img' and attrs.get('src')=='/avatar.jpg': self.image=attrs

for page in ['index.html','de/index.html']:
    portrait=Portrait((ROOT/page).read_text())
    assert portrait.source and portrait.image, f'{page}: responsive portrait or fallback missing'
    expected={f'/assets/images/marc-luehr-{width}.webp {width}w' for width in WIDTHS}
    assert set(portrait.source['srcset'].split(', '))==expected,page
    assert portrait.source.get('sizes')=='(max-width: 700px) 88px, (max-width: 1050px) 200px, 240px',page
    assert portrait.image.get('fetchpriority')=='high',page
    assert portrait.image.get('width')=='1192' and portrait.image.get('height')=='1299',page
    for width in WIDTHS:
        file=ROOT/f'assets/images/marc-luehr-{width}.webp'
        content=file.read_bytes()
        assert content[:4]==b'RIFF' and content[8:12]==b'WEBP',file
        assert len(content)<=40000, f'{file}: exceeds the 40 KB image budget'
assert (ROOT/'avatar.jpg').exists(), 'Original social image and JPEG fallback missing'
print('PASS: responsive portrait selection, JPEG fallback, dimensions and 40 KB per-image budget')
