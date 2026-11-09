"""HTTP contract tests for the standard-library SynTutor transport."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import app as stdlib_app


class StdlibParseTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), stdlib_app.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.httpd.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def post(self, payload, path="/api/parse"):
        request = Request(
            self.base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))

    def test_non_object_json_body_returns_400(self):
        request = Request(
            self.base_url + "/api/parse",
            data=json.dumps(["not", "an", "object"]).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=3) as response:
                status = response.status
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            status = error.code
            payload = json.loads(error.read().decode("utf-8"))
        self.assertEqual(status, 400)
        self.assertIn("JSON object", payload["error"])

    def test_words_reject_non_string_elements(self):
        with patch.object(stdlib_app, "word_info") as words:
            status, payload = self.post({"words": ["hello", 7]}, path="/api/words")
        self.assertEqual(status, 422)
        self.assertIn("list of strings", payload["error"])
        words.assert_not_called()

    def test_words_accept_string_elements(self):
        with patch.object(stdlib_app, "word_info", return_value=[{"word": "hello"}]) as words:
            status, payload = self.post({"words": ["hello"]}, path="/api/words")
        self.assertEqual(status, 200)
        words.assert_called_once_with(["hello"])
        self.assertEqual(payload, {"results": [{"word": "hello"}]})

    def test_optional_rate_limit_rejects_replay(self):
        from rate_limit import RateLimiter
        limiter = RateLimiter(clock=lambda: 100)
        with patch.object(stdlib_app, "API_RATE_PER_MINUTE", 1), \
             patch.object(stdlib_app, "API_LIMITER", limiter):
            first, _ = self.post({"text": ""})
            second, payload = self.post({"text": ""})
        self.assertEqual(first, 422)
        self.assertEqual(second, 429)
        self.assertEqual(payload["error"], "too many requests")

    def test_chapter_and_variety_are_forwarded_to_shared_analysis(self):
        expected = {"br_analysis": {"status": "unresolved"}}
        with patch.object(stdlib_app, "build_payload", return_value=expected) as build:
            status, payload = self.post({
                "text": "A sentence.", "chapter": 2, "variety": " AmE ",
            })
        self.assertEqual(status, 200)
        self.assertEqual(payload, expected)
        build.assert_called_once_with(
            "A sentence.", sentence_index=0, convention_version="V2",
            chapter=2, appendix_nom=None, variety="AmE",
        )

    def test_chapter_convention_mismatch_returns_400_without_analysis(self):
        with patch.object(stdlib_app, "build_payload") as build:
            status, payload = self.post({
                "text": "A sentence.", "chapter": 2, "convention_version": "V3",
            })
        self.assertEqual(status, 400)
        self.assertIn("requires convention_version V2", payload["error"])
        build.assert_not_called()

    def test_boolean_sentence_index_returns_400_without_analysis(self):
        with patch.object(stdlib_app, "build_payload") as build:
            status, payload = self.post({
                "text": "A sentence.", "sentence_index": True,
            })
        self.assertEqual(status, 400)
        self.assertIn("sentence_index must be an integer", payload["error"])
        build.assert_not_called()

    def test_out_of_range_sentence_index_returns_400(self):
        with patch.object(stdlib_app, "build_payload",
                          side_effect=ValueError("sentence_index 1 is out of range for 1 sentence(s)")):
            status, payload = self.post({
                "text": "A sentence.", "sentence_index": 1,
            })
        self.assertEqual(status, 400)
        self.assertIn("out of range", payload["error"])

    def test_invalid_variety_returns_400_without_analysis(self):
        with patch.object(stdlib_app, "build_payload") as build:
            status, payload = self.post({"text": "A sentence.", "variety": " "})
        self.assertEqual(status, 400)
        self.assertIn("variety", payload["error"])
        build.assert_not_called()

    def test_missing_model_failure_returns_503_with_install_hint(self):
        with patch.object(stdlib_app, "build_payload",
                          side_effect=RuntimeError("benepar model not installed")), \
             patch.object(stdlib_app, "_model_status",
                          return_value={"error": "benepar model not installed"}):
            status, payload = self.post({"text": "A sentence.", "chapter": 2})
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"], "benepar model not installed")
        self.assertIn("hint", payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
