"""HTTP-level tests for the Flask parse endpoint using a stubbed parser backend."""
import unittest
from unittest.mock import patch

from webapp import app, ParseFailure


class FlaskParseContractTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_empty_text_returns_422(self):
        response = self.client.post("/api/parse", json={"text": "   "})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["error"], "empty input")

    def test_invalid_convention_returns_400_without_calling_parser(self):
        with patch("webapp.build_payload") as build:
            response = self.client.post("/api/parse", json={
                "text": "A sentence.", "convention_version": "V11"
            })
        self.assertEqual(response.status_code, 400)
        self.assertIn("V1-V10", response.get_json()["error"])
        build.assert_not_called()

    def test_invalid_sentence_index_returns_400(self):
        response = self.client.post("/api/parse", json={
            "text": "A sentence.", "sentence_index": -1
        })
        self.assertEqual(response.status_code, 400)

    def test_boolean_sentence_index_returns_400(self):
        response = self.client.post("/api/parse", json={
            "text": "A sentence.", "sentence_index": True
        })
        self.assertEqual(response.status_code, 400)

    def test_out_of_range_sentence_index_returns_400(self):
        with patch("webapp.build_payload", side_effect=ValueError(
                "sentence_index 2 is out of range for 2 detected sentence(s)")) as build:
            response = self.client.post("/api/parse", json={
                "text": "One. Two.", "sentence_index": 2
            })
        self.assertEqual(response.status_code, 400)
        self.assertIn("out of range", response.get_json()["error"])
        build.assert_called_once()

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/parse", data="{invalid", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_non_object_json_body_returns_400(self):
        response = self.client.post("/api/parse", json=["not", "an", "object"])
        self.assertEqual(response.status_code, 400)
        self.assertIn("JSON object", response.get_json()["error"])

    def test_all_json_routes_reject_oversize_requests(self):
        # Prevent expensive parsing and tree evaluation from reading an unbounded
        # request body. This must apply to all four JSON routes, not just
        # /api/explain and /api/evaluate.
        for endpoint in ("/api/parse", "/api/words", "/api/explain", "/api/evaluate"):
            with self.subTest(endpoint=endpoint), patch("webapp.build_payload") as build:
                response = self.client.post(
                    endpoint,
                    data='{"text":"' + ('x' * 250_000) + '"}',
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 413)
                self.assertEqual(response.get_json()["error"], "request exceeds 250000 bytes")
                build.assert_not_called()

    def test_successful_build_returns_payload(self):
        expected = {"br_analysis": {"status": "unresolved"}}
        with patch("webapp.build_payload", return_value=expected) as build:
            response = self.client.post("/api/parse", json={
                "text": "A sentence.", "convention_version": "V10"
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected)
        build.assert_called_once_with("A sentence.", sentence_index=0,
                                      convention_version="V10", chapter=None,
                                      appendix_nom=None, variety=None)

    def test_chapter_selects_its_convention_and_is_forwarded(self):
        expected = {"br_analysis": {"status": "unresolved"}}
        with patch("webapp.build_payload", return_value=expected) as build:
            response = self.client.post("/api/parse", json={
                "text": "A sentence.", "chapter": 2
            })
        self.assertEqual(response.status_code, 200)
        build.assert_called_once_with("A sentence.", sentence_index=0,
                                      convention_version="V2", chapter=2,
                                      appendix_nom=None, variety=None)

    def test_chapter_convention_mismatch_is_rejected_without_parsing(self):
        with patch("webapp.build_payload") as build:
            response = self.client.post("/api/parse", json={
                "text": "A sentence.", "chapter": 2, "convention_version": "V3"
            })
        self.assertEqual(response.status_code, 400)
        self.assertIn("requires convention_version V2", response.get_json()["error"])
        build.assert_not_called()

    def test_chapter_7_appendix_d1_is_forwarded(self):
        with patch("webapp.build_payload", return_value={"br_analysis": {"status": "unresolved"}}) as build:
            response = self.client.post("/api/parse", json={
                "text": "A sentence.", "chapter": 7, "appendix_nom": True
            })
        self.assertEqual(response.status_code, 200)
        build.assert_called_once_with("A sentence.", sentence_index=0,
                                      convention_version="V7", chapter=7,
                                      appendix_nom=True, variety=None)

    def test_variety_is_forwarded_and_trimmed(self):
        with patch("webapp.build_payload", return_value={"br_analysis": {"status": "unresolved"}}) as build:
            response = self.client.post("/api/parse", json={
                "text": "A sentence.", "chapter": 2, "variety": " AmE "
            })
        self.assertEqual(response.status_code, 200)
        build.assert_called_once_with("A sentence.", sentence_index=0,
                                      convention_version="V2", chapter=2,
                                      appendix_nom=None, variety="AmE")

    def test_empty_variety_returns_400(self):
        response = self.client.post("/api/parse", json={
            "text": "A sentence.", "variety": "   "
        })
        self.assertEqual(response.status_code, 400)

    def test_parser_failure_returns_422(self):
        with patch("webapp.build_payload", side_effect=ParseFailure("No sentence found")):
            response = self.client.post("/api/parse", json={"text": "A sentence."})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["error"], "No sentence found")

    def test_unexpected_backend_failure_returns_503(self):
        with patch("webapp.build_payload", side_effect=RuntimeError("backend unavailable")), \
             patch("webapp.health_payload", return_value={"error": "models unavailable"}):
            response = self.client.post("/api/parse", json={"text": "A sentence."})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "backend unavailable")
        self.assertIn("hint", response.get_json())

    def test_real_shared_api_model_failure_returns_503_with_install_hint(self):
        with patch("api.analyze", side_effect=RuntimeError("benepar model not installed")), \
             patch("webapp.health_payload", return_value={"error": "benepar model not installed"}):
            response = self.client.post("/api/parse", json={
                "text": "A sentence.", "chapter": 2
            })
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "benepar model not installed")
        self.assertIn("hint", response.get_json())


if __name__ == "__main__":
    unittest.main(verbosity=2)
