"""Prepare changed public URLs, then notify IndexNow after a successful deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = 'https://luehr.dev'
ENDPOINT = 'https://api.indexnow.org/indexnow'
KEY_FILE = 'indexnow-key.txt'


def check_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.netloc != 'luehr.dev'
            or parsed.query or parsed.fragment or '%' in parsed.path
            or any(part in ('.', '..') for part in parsed.path.split('/'))):
        raise ValueError('IndexNow URLs must be canonical https://luehr.dev/ URLs')


def manifest(site):
    # Shared asset changes can alter page presentation even when HTML is unchanged.
    assets = hashlib.sha256()
    for file in sorted(site.rglob('*')):
        if file.is_file() and file.suffix not in ('.html', '.xml', '.txt'):
            assets.update(file.relative_to(site).as_posix().encode() + b'\0')
            assets.update(hashlib.sha256(file.read_bytes()).digest())
    urls = ET.parse(site / 'sitemap.xml').findall('{*}url/{*}loc')
    result = {}
    for element in urls:
        url = element.text
        check_url(url)
        path = urlsplit(url).path
        file = site / (path.lstrip('/') + ('index.html' if path.endswith('/') else ''))
        result[url] = hashlib.sha256(file.read_bytes() + assets.digest()).hexdigest()
    if not result:
        raise ValueError('Cannot prepare IndexNow without sitemap URLs')
    return result


def changed_urls(previous, current):
    for url in previous.keys() | current.keys():
        check_url(url)
    return sorted(url for url in previous.keys() | current.keys()
                  if previous.get(url) != current.get(url))


def prepare(site, state, payload):
    current = manifest(site)
    previous = json.loads(state.read_text()) if state.exists() else {}
    urls = changed_urls(previous, current)
    key = (site / KEY_FILE).read_text().strip()
    if not re.fullmatch(r'[a-zA-Z0-9-]{8,128}', key):
        raise ValueError('Invalid IndexNow verification key')
    if len(urls) > 10000:
        raise ValueError('IndexNow accepts at most 10,000 URLs per request')
    submission = {'host': 'luehr.dev', 'key': key, 'keyLocation': BASE+'/'+KEY_FILE, 'urlList': urls}
    payload.write_text(json.dumps({'submission': submission, 'manifest': current}))
    print(f'IndexNow: {len(urls)} new, changed or removed URLs; {len(current)} current pages')


def read_response(request):
    for attempt in range(3):
        try:
            with urlopen(request, timeout=20) as response:
                return response.status, response.read()
        except HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise RuntimeError(f'IndexNow HTTP {error.code}; no acknowledgement saved') from None
        except (URLError, TimeoutError):
            pass
        if attempt < 2:
            time.sleep(2 ** attempt)
    raise RuntimeError('IndexNow unavailable after three attempts; URLs will be retried next deployment')


def submit(payload, state):
    data = json.loads(payload.read_text())
    submission = data['submission']
    if submission['urlList']:
        for url in submission['urlList']:
            check_url(url)
        status, key = read_response(BASE+'/'+KEY_FILE)
        if status != 200 or key.decode().strip() != submission['key']:
            raise RuntimeError('Live IndexNow verification file does not match; no URLs submitted')
        request = Request(ENDPOINT, json.dumps(submission).encode(),
                          {'Content-Type': 'application/json; charset=utf-8'}, method='POST')
        status, _ = read_response(request)
        if status not in (200, 202):
            raise RuntimeError(f'Unexpected IndexNow HTTP {status}; no acknowledgement saved')
        print(f'IndexNow HTTP {status}: {len(submission["urlList"])} URLs received; indexing is not guaranteed')
    else:
        print('IndexNow: no page changes; nothing submitted')
    # Save only after an accepted request. Failed notifications remain pending.
    state.write_text(json.dumps(data['manifest'], sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'submit'])
    parser.add_argument('--site', type=Path, default=Path('_site'))
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--payload', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.site, args.state, args.payload)
    else:
        submit(args.payload, args.state)
