"""Actual Flask, stdlib and ASGI routes share deterministic source evidence."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch

import app as stdlib_app
from webapp import app
from test_explanations import analysis, registry


class ExplanationTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), stdlib_app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(2)

    def stdlib_post(self, data):
        request = Request(f'http://127.0.0.1:{self.server.server_port}/api/explain',
                          data=data, headers={'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_same_canonical_tree_has_same_evidence_in_flask_and_stdlib(self):
        data = {'tree': analysis()['tree']}
        with patch('explanations.load_registry', return_value=registry()):
            flask = app.test_client().post('/api/explain', json=data)
            code, stdlib = self.stdlib_post(json.dumps(data).encode())
        self.assertEqual(flask.status_code, 200); self.assertEqual(code, 200)
        self.assertEqual(flask.get_json(), stdlib)
        self.assertEqual(stdlib['status'], 'EXPLAINED')

    def test_invalid_missing_source_and_unresolved_inputs(self):
        for data in [[], {'tree': {}}, {'tree': None, 'templates': []}]:
            with self.subTest(data=data):
                flask = app.test_client().post('/api/explain', json=data)
                code, _ = self.stdlib_post(json.dumps(data).encode())
                self.assertEqual(flask.status_code, 400); self.assertEqual(code, 400)
        response = app.test_client().post('/api/explain', json={'tree': None})
        self.assertEqual(response.get_json()['status'], 'ANALYSIS_UNRESOLVED')
        response = app.test_client().post('/api/explain', json={'tree': analysis()['tree']})
        self.assertEqual(response.get_json()['status'], 'NO_BOOK_BASIS')

    def test_malformed_json_and_oversized_request(self):
        for raw, expected in [(b'{invalid', 400), (b' ' * 250001, 413)]:
            self.assertEqual(app.test_client().post('/api/explain', data=raw, content_type='application/json').status_code, expected)
            self.assertEqual(self.stdlib_post(raw)[0], expected)

    def test_hosted_asgi_route_matches_flask(self):
        from fastapi import FastAPI, Request as ASGIRequest
        from fastapi.testclient import TestClient
        from explanation_transport import api_explain
        async def endpoint(request: ASGIRequest):
            return await api_explain(request)
        asgi = FastAPI()
        asgi.add_api_route('/api/explain', endpoint, methods=['POST'])
        with TestClient(asgi) as client, patch('explanations.load_registry', return_value=registry()):
            data = {'tree': analysis()['tree']}
            hosted = client.post('/api/explain', json=data)
            flask = app.test_client().post('/api/explain', json=data)
            self.assertEqual(hosted.status_code, 200)
            self.assertEqual(hosted.json(), flask.get_json())
            self.assertEqual(client.post('/api/explain', json=[]).status_code, 400)
            self.assertEqual(client.post('/api/explain', content=b' ' * 250001).status_code, 413)
