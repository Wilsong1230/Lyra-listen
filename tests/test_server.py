import io
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    mock_whisper_model = MagicMock()
    mock_whisper_model.transcribe.return_value = {"text": "hello world"}

    with patch("server.whisper") as mock_whisper, \
         patch("server.sd"):
        mock_whisper.load_model.return_value = mock_whisper_model
        import server
        with TestClient(server.app) as c:
            yield c


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "stt_model" in data
    assert "recording" in data
    assert data["recording"] is False


def test_transcribe_returns_text(client):
    fake_wav = io.BytesIO(b"RIFF" + b"\x00" * 36)
    r = client.post("/transcribe", files={"file": ("test.wav", fake_wav, "audio/wav")})
    assert r.status_code == 200
    assert r.json()["text"] == "hello world"


def test_transcribe_requires_file(client):
    r = client.post("/transcribe")
    assert r.status_code == 422
