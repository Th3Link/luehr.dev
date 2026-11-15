"""Offline tests: deployment deltas and accepted/failed IndexNow notifications."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from indexnow import BASE, KEY_FILE, changed_urls, manifest, prepare, submit


class IndexNowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / 'site'
        self.site.mkdir()
        self.state = self.root / 'acknowledged.json'
        self.payload = self.root / 'payload.json'
        (self.site / 'index.html').write_text('<h1>Home</h1>')
        (self.site / KEY_FILE).write_text('test-key-123')
        (self.site / 'sitemap.xml').write_text(f'<urlset><url><loc>{BASE}/</loc></url></urlset>')

    def prepare(self):
        prepare(self.site, self.state, self.payload)
        return json.loads(self.payload.read_text())

    def test_new_changed_unchanged_and_removed_pages(self):
        self.assertEqual(changed_urls({BASE+'/old/': 'a', BASE+'/': 'a'},
                                      {BASE+'/new/': 'b', BASE+'/': 'a'}),
                         [BASE+'/new/', BASE+'/old/'])
        self.assertEqual(changed_urls({BASE+'/': 'a'}, {BASE+'/': 'b'}), [BASE+'/'])
        self.assertEqual(changed_urls({BASE+'/': 'a'}, {BASE+'/': 'a'}), [])

    def test_first_deployment_and_asset_change(self):
        initial = self.prepare()
        self.assertEqual(initial['submission']['urlList'], [BASE+'/'])
        self.assertFalse(self.state.exists())
        self.state.write_text(json.dumps(initial['manifest']))
        self.assertEqual(self.prepare()['submission']['urlList'], [])
        (self.site / 'portrait.webp').write_bytes(b'new image')
        self.assertEqual(self.prepare()['submission']['urlList'], [BASE+'/'])

    def test_foreign_host_or_path_traversal_is_rejected(self):
        for url in ['https://example.com/', BASE+'/../outside', BASE+'/%2e%2e/outside']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                changed_urls({url: 'a'}, {})

    def test_acknowledged_requests_save_state(self):
        for code in [200, 202]:
            data = self.prepare()
            with patch('indexnow.read_response', side_effect=[(200, b'test-key-123'), (code, b'')]) as request:
                submit(self.payload, self.state)
            self.assertEqual(json.loads(self.state.read_text()), data['manifest'])
            sent = json.loads(request.call_args.args[0].data)
            self.assertEqual(sent['urlList'], [BASE+'/'])
            self.assertNotIn('manifest', sent)
            self.state.unlink()

    def test_failure_preserves_pending_changes(self):
        self.state.write_text(json.dumps({BASE+'/old/': 'old'}))
        previous = self.state.read_text()
        self.prepare()
        with patch('indexnow.read_response', side_effect=[(200, b'test-key-123'), RuntimeError('Unavailable')]):
            with self.assertRaises(RuntimeError):
                submit(self.payload, self.state)
        self.assertEqual(self.state.read_text(), previous)
        self.assertEqual(self.prepare()['submission']['urlList'], [BASE+'/', BASE+'/old/'])

    def test_wrong_live_key_prevents_submission(self):
        self.prepare()
        with patch('indexnow.read_response', return_value=(200, b'wrong-key')) as request:
            with self.assertRaises(RuntimeError):
                submit(self.payload, self.state)
        self.assertEqual(request.call_count, 1)
        self.assertFalse(self.state.exists())

    def test_unchanged_deployment_does_not_call_indexnow(self):
        self.state.write_text(json.dumps(manifest(self.site)))
        self.prepare()
        with patch('indexnow.read_response') as request:
            submit(self.payload, self.state)
        request.assert_not_called()


if __name__ == '__main__':
    unittest.main()
