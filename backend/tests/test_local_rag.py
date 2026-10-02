import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


_test_directory = tempfile.TemporaryDirectory(prefix="local-rag-tests-")
_database_path = Path(_test_directory.name, "research.db").as_posix()
os.environ["DATABASE_URL"] = f"sqlite:///{_database_path}"
os.environ["LLM_BACKEND"] = "local"
os.environ["JWT_SECRET_KEY"] = "local-test-signing-secret-that-is-long-enough"

from fastapi.testclient import TestClient

from app.core.database import SessionLocal, engine
from app.main import app
from app.models.query import Query
from app.services.llm import LLMGenerationError, _generate
from app.core.security import create_access_token, decode_access_token, verify_password
from app.models.user import User


def create_pdf(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
        + stream
        + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, item in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode() + item + b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return bytes(output)


class LocalRagApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()
        registration = cls.client.post(
            "/auth/register",
            json={
                "email": "Researcher@Example.com",
                "name": "Test Researcher",
                "password": "secure-test-password",
            },
        )
        if registration.status_code != 201:
            raise AssertionError(f"Test account registration failed: {registration.text}")
        cls.session = registration.json()
        cls.user_id = cls.session["user"]["id"]
        cls.client.headers.update(
            {"Authorization": f"Bearer {cls.session['access_token']}"}
        )

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        engine.dispose()
        _test_directory.cleanup()

    def tearDown(self):
        for document in self.client.get("/documents/").json():
            self.client.delete(f"/documents/{document['document_id']}")
        with SessionLocal() as db:
            db.query(Query).filter(Query.user_id == self.user_id).delete()
            db.commit()

    def upload_text(self, filename: str, text: str):
        return self.client.post(
            "/upload/",
            files={
                "file": (
                    filename,
                    create_pdf(text),
                    "application/pdf",
                )
            },
        )

    def test_health_and_standalone_configuration(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        status = self.client.get("/").json()
        self.assertEqual(status["storage"], "sqlite")
        self.assertEqual(status["answer_mode"], "local-evidence")

    def test_registration_hashes_password_and_login_returns_jwt(self):
        with SessionLocal() as db:
            user = db.get(User, self.user_id)
            self.assertIsNotNone(user.password_hash)
            self.assertNotEqual(user.password_hash, "secure-test-password")
            self.assertTrue(verify_password("secure-test-password", user.password_hash))
            self.assertFalse(verify_password("wrong-password", user.password_hash))

        login = self.client.post(
            "/auth/login",
            json={"email": "researcher@example.com", "password": "secure-test-password"},
        )
        invalid_login = self.client.post(
            "/auth/login",
            json={"email": "researcher@example.com", "password": "wrong-password"},
        )
        duplicate = self.client.post(
            "/auth/register",
            json={
                "email": "researcher@example.com",
                "name": "Duplicate",
                "password": "secure-test-password",
            },
        )

        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["token_type"], "bearer")
        self.assertEqual(invalid_login.status_code, 401)
        self.assertEqual(duplicate.status_code, 409)

    def test_workspace_apis_require_a_valid_token(self):
        with TestClient(app) as anonymous_client:
            self.assertEqual(anonymous_client.get("/documents/").status_code, 401)
            self.assertEqual(anonymous_client.get("/chat/history").status_code, 401)
            self.assertEqual(anonymous_client.get("/synthesis/history").status_code, 401)
            self.assertEqual(
                anonymous_client.post(
                    "/chat/",
                    json={"question": "Should be unauthorized"},
                ).status_code,
                401,
            )
            self.assertEqual(
                anonymous_client.post(
                    "/upload/",
                    files={"file": ("notes.pdf", create_pdf("private"), "application/pdf")},
                ).status_code,
                401,
            )

    def test_local_jwt_key_is_generated_once_and_tokens_validate(self):
        with tempfile.TemporaryDirectory(prefix="jwt-key-test-") as directory:
            key_path = Path(directory, ".jwt_secret")
            fake_source_path = Path(directory, "app", "core", "security.py")
            with (
                patch("app.core.security.settings.JWT_SECRET_KEY", ""),
                patch("app.core.security.Path", return_value=fake_source_path),
            ):
                token = create_access_token(self.user_id)
                generated_key = key_path.read_text(encoding="utf-8")
                self.assertGreaterEqual(len(generated_key), 32)
                self.assertEqual(decode_access_token(token)["sub"], self.user_id)
                create_access_token(self.user_id)
                self.assertEqual(key_path.read_text(encoding="utf-8"), generated_key)

    def test_pdf_validation_and_empty_question(self):
        invalid_extension = self.client.post(
            "/upload/",
            files={"file": ("notes.txt", b"not a PDF", "text/plain")},
        )
        invalid_content = self.client.post(
            "/upload/",
            files={"file": ("notes.pdf", b"not a PDF", "application/pdf")},
        )
        empty_pdf = self.upload_text("empty.pdf", "")
        empty_question = self.client.post("/chat/", json={"question": ""})

        self.assertEqual(invalid_extension.status_code, 400)
        self.assertEqual(invalid_content.status_code, 400)
        self.assertEqual(empty_pdf.status_code, 422)
        self.assertEqual(empty_question.status_code, 422)
        self.assertEqual(self.client.get("/documents/").json(), [])

    def test_chat_synthesis_and_document_lifecycle(self):
        self.upload_text(
            "spiral-one.pdf",
            "The Spiral Model combines iterative development with repeated risk "
            "analysis. Each cycle plans, evaluates risks, develops software, and "
            "gathers customer feedback.",
        )
        self.upload_text(
            "spiral-two.pdf",
            "The Spiral Model is iterative and risk-driven. Every cycle identifies "
            "and mitigates risks before customer review and software release.",
        )

        documents = self.client.get("/documents/").json()
        self.assertEqual(len(documents), 2)
        self.assertTrue(all(document["chunk_count"] > 0 for document in documents))

        question = "How does the Spiral Model handle iterative development and risk analysis?"
        answer = self.client.post("/chat/", json={"question": question})
        self.assertEqual(answer.status_code, 200)
        self.assertTrue(answer.json()["sources"])
        self.assertIn("Hosted language-model generation is disabled", answer.json()["answer"])

        synthesis = self.client.post("/synthesis/", json={"question": question})
        self.assertEqual(synthesis.status_code, 200)
        self.assertEqual(synthesis.json()["documents_analyzed"], 2)
        self.assertGreaterEqual(len(synthesis.json()["sources"]), 2)
        self.assertEqual(len(self.client.get("/chat/history").json()), 1)
        saved_syntheses = self.client.get("/synthesis/history").json()
        self.assertEqual(len(saved_syntheses), 1)
        self.assertEqual(saved_syntheses[0]["question"], question)

        deleted_id = documents[0]["document_id"]
        self.assertEqual(
            self.client.delete(f"/documents/{deleted_id}").status_code,
            204,
        )
        self.assertEqual(len(self.client.get("/documents/").json()), 1)
        self.assertEqual(self.client.delete("/documents/999999").status_code, 404)

    def test_synthesis_requires_two_relevant_papers(self):
        self.upload_text(
            "single-paper.pdf",
            "The Spiral Model uses iterative development and systematic risk analysis.",
        )
        response = self.client.post(
            "/synthesis/",
            json={"question": "How does the Spiral Model handle risk analysis?"},
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_provider_responses_raise_actionable_generation_error(self):
        invalid_responses = [
            SimpleNamespace(choices=None),
            SimpleNamespace(choices=[]),
            SimpleNamespace(choices=[SimpleNamespace(message=None)]),
            SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
            ),
            SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="  "))]
            ),
        ]

        for response in invalid_responses:
            with self.subTest(response=response):
                fake_client = SimpleNamespace(
                    chat=SimpleNamespace(
                        completions=SimpleNamespace(
                            create=lambda **_kwargs: response,
                        )
                    )
                )
                with patch("app.services.llm.OpenAI", return_value=fake_client):
                    with self.assertRaises(LLMGenerationError):
                        _generate("prompt", "test-model")

    def test_provider_failure_falls_back_to_cited_evidence(self):
        self.upload_text(
            "first.pdf",
            "The Spiral Model uses iterative development and risk analysis.",
        )
        self.upload_text(
            "second.pdf",
            "The Spiral Model uses iterative development and risk analysis.",
        )

        with (
            patch("app.services.llm.settings.LLM_BACKEND", "auto"),
            patch("app.services.llm.settings.OPENROUTER_API_KEY", "test-key"),
            patch(
                "app.services.llm._generate",
                side_effect=LLMGenerationError("Empty completion"),
            ),
        ):
            chat_response = self.client.post(
                "/chat/",
                json={"question": "How does the Spiral Model handle iterative risk analysis?"},
            )
            synthesis_response = self.client.post(
                "/synthesis/",
                json={"question": "How does the Spiral Model handle iterative risk analysis?"},
            )

        self.assertEqual(chat_response.status_code, 200)
        self.assertIn("did not return a usable answer", chat_response.json()["answer"])
        self.assertIn("Spiral Model", chat_response.json()["answer"])
        self.assertTrue(chat_response.json()["sources"])
        self.assertEqual(synthesis_response.status_code, 200)
        self.assertIn(
            "did not return a usable comparison",
            synthesis_response.json()["answer"],
        )
        self.assertIn("Spiral Model", synthesis_response.json()["answer"])
        self.assertTrue(synthesis_response.json()["sources"])

    def test_documents_and_retrieval_are_isolated_between_accounts(self):
        self.upload_text(
            "private-paper.pdf",
            "The Spiral Model uses iterative development and risk analysis.",
        )
        other_registration = self.client.post(
            "/auth/register",
            json={
                "email": "another@example.com",
                "name": "Another Researcher",
                "password": "another-secure-password",
            },
        )
        self.assertEqual(other_registration.status_code, 201)

        with TestClient(app) as other_client:
            other_client.headers.update(
                {
                    "Authorization": (
                        f"Bearer {other_registration.json()['access_token']}"
                    )
                }
            )
            self.assertEqual(other_client.get("/documents/").json(), [])
            self.assertEqual(other_client.get("/chat/history").json(), [])
            self.assertEqual(
                other_client.post(
                    "/chat/",
                    json={
                        "question": "How does the Spiral Model use risk analysis?"
                    },
                ).status_code,
                404,
            )


if __name__ == "__main__":
    unittest.main()
