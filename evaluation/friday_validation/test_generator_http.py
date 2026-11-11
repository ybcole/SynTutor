"""Independent QA: real HTTP transport and diagnostic consistency."""

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from werkzeug.serving import make_server
from webapp import app


class GeneratorHTTPTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = make_server("127.0.0.1", 0, app, threaded=True)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(
            target=cls.server.serve_forever, daemon=True
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def post(self, body):
        request = Request(
            f"http://127.0.0.1:{self.port}/api/parse",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            response = urlopen(request, timeout=120)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def test_real_http_returns_consistent_tree_authority(self):
        status, data = self.post({"text": "The birds sing."})
        self.assertEqual(status, 200)
        self.assertEqual(data["parse"]["text"], "The birds sing.")
        self.assertEqual(
            data["meta"]["br_normalization_status"],
            data["br_analysis"]["status"],
        )
        self.assertEqual(
            data["summary"]["verdict_authority"],
            "legacy_diagnostic",
        )

    def test_real_http_preserves_correction_consistency(self):
        status, data = self.post({"text": "These book are heavy."})
        self.assertEqual(status, 200)
        correction = data["summary"]["correction"]
        self.assertEqual(
            correction["corrected_sentence"],
            data["summary"]["corrected_sentence"],
        )
        self.assertEqual(
            correction["corrected_sentence"],
            "These books are heavy.",
        )

    def test_real_http_rejects_invalid_sentence_index(self):
        status, data = self.post({
            "text": "The birds sing.",
            "sentence_index": True,
        })
        self.assertEqual(status, 400)
        self.assertIn("sentence_index", data["error"])

    def test_real_http_modal_diagnosis_is_not_run_on(self):
        status, data = self.post({"text": "Can she swims?"})
        self.assertEqual(status, 200)
        explanation = data["summary"]["explanation"].lower()
        self.assertNotIn(
            "two full parts",
            explanation,
            "Known QA-009 defect persists in the HTTP response.",
        )


if __name__ == "__main__":
    unittest.main()
