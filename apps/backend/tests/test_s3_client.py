import unittest
from unittest.mock import patch

from app.modules.file_module.services.s3_client import S3Client


class _FakeContent:
    def __init__(self, chunks):
        self._chunks = chunks
        self.chunk_sizes = []

    async def iter_chunked(self, chunk_size):
        self.chunk_sizes.append(chunk_size)
        for chunk in self._chunks:
            yield chunk


class _FakeStream:
    def __init__(self, chunks):
        self.content = _FakeContent(chunks)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeClient:
    def __init__(self, stream):
        self._stream = stream

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get_object(self, **kwargs):
        return {"Body": self._stream}


class S3ClientIterChunksTests(unittest.IsolatedAsyncioTestCase):
    async def test_iter_chunks_uses_stream_content_iterator(self) -> None:
        stream = _FakeStream([b"chunk-1", b"chunk-2"])
        client = S3Client()

        with patch.object(client, "_client", return_value=_FakeClient(stream)):
            chunks = [chunk async for chunk in client.iter_chunks("http://minio/bucket/key", chunk_size=512)]

        self.assertEqual(chunks, [b"chunk-1", b"chunk-2"])
        self.assertEqual(stream.content.chunk_sizes, [512])
