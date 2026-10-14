import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
import urllib.error
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app


class FakeOllama(BaseHTTPRequestHandler):
    received = None

    def do_POST(self):
        FakeOllama.received = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({'message': {'content': 'Forecast se entrega el viernes [1].'}}).encode())

    def log_message(self, *args):
        pass


class AppTest(unittest.TestCase):
    def test_retrieval_accents_and_no_match(self):
        chunks = [{'file': 'nota.docx', 'paragraph': 1, 'text': 'La actualización del proyecto Forecast llega el viernes.'},
                  {'file': 'otro.docx', 'paragraph': 1, 'text': 'Viaje a Córdoba.'}]
        self.assertEqual(app.retrieve('actualizacion Forecast', chunks), [chunks[0]])
        self.assertEqual(app.retrieve('elefantes', chunks), [])

    def test_http_flow_and_word_reading(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with zipfile.ZipFile(root / 'novedades.docx', 'w') as doc:
                doc.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Forecast se entrega el viernes.</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Responsable: Ana.</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>')
            (root / 'antiguo.doc').write_bytes(b'legacy')
            (root / 'roto.docx').write_bytes(b'broken')
            self.assertEqual(len(app.read_word(root / 'novedades.docx')), 2)
            mock = ThreadingHTTPServer(('127.0.0.1', 0), FakeOllama)
            threading.Thread(target=mock.serve_forever, daemon=True).start()
            # Choose a free test port.
            import socket
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            environment = {**os.environ, 'DOCUMENTS_PATH': folder, 'PORT': str(port), 'OLLAMA_URL': f'http://127.0.0.1:{mock.server_port}'}
            process = subprocess.Popen([sys.executable, str(Path(app.__file__))], env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            base = f'http://127.0.0.1:{port}'
            try:
                for _ in range(50):
                    try:
                        with urllib.request.urlopen(base + '/api/documents') as response:
                            listing = json.load(response)
                        break
                    except urllib.error.URLError:
                        time.sleep(.1)
                else:
                    self.fail('Web server did not start')
                self.assertEqual(listing['files'], ['novedades.docx'])
                self.assertEqual(listing['chunks'], 2)
                self.assertEqual(len(listing['warnings']), 2)
                with urllib.request.urlopen(base) as response:
                    self.assertIn('Consulta de novedades', response.read().decode())
                def ask(question, origin=None):
                    headers = {'Content-Type': 'application/json'}
                    if origin:
                        headers['Origin'] = origin
                    request = urllib.request.Request(base + '/api/ask', data=json.dumps({'question': question}).encode(), headers=headers)
                    with urllib.request.urlopen(request) as response:
                        return json.load(response)
                result = ask('¿Cuándo se entrega Forecast?')
                self.assertIn('[1]', result['answer'])
                self.assertEqual(result['sources'][0]['file'], 'novedades.docx')
                self.assertIn('Forecast se entrega el viernes.', FakeOllama.received['messages'][1]['content'])
                self.assertEqual(ask('elefantes')['sources'], [])
                with self.assertRaises(urllib.error.HTTPError) as error:
                    ask('')
                self.assertEqual(error.exception.code, 400)
                with self.assertRaises(urllib.error.HTTPError) as error:
                    ask('Forecast', 'https://example.com')
                self.assertEqual(error.exception.code, 403)
            finally:
                process.terminate()
                process.wait(timeout=5)
                mock.shutdown()
                mock.server_close()


if __name__ == '__main__':
    unittest.main()
