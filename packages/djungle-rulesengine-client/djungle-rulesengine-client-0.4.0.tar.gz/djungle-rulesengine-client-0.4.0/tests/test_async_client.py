import json
from unittest import IsolatedAsyncioTestCase

import respx

from rulesengine.async_client import AsyncEngineClient, AsyncEngineClientError


class AsyncEngineClientTestCase(IsolatedAsyncioTestCase):
    @respx.mock
    async def test_push_action_success(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.post("https://example.com/api/v1/subjects/sys-1/props/", params__eq={"a": "my-action"})

        ret = await engine.push_action("sys-1", "my-action", {"key": "value"})

        self.assertIsNone(ret)

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"payload": {"key": "value"}})

    @respx.mock
    async def test_push_action_failure(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.post(
            "https://example.com/api/v1/subjects/sys-1/props/",
            params__eq={"a": "my-action"},
        ).respond(status_code=400, json={"error": "ko"})

        with self.assertRaises(AsyncEngineClientError) as cm:
            await engine.push_action("sys-1", "my-action", {"key": "value"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"payload": {"key": "value"}})

    @respx.mock
    async def test_get_pluggable_props_success(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.get(
            "https://example.com/api/v1/subjects/sys-1/props/",
            params__eq={"p": "my-prop"},
        ).respond(json={"status": "ok"})

        ret = await engine.get_pluggable_props("sys-1", "my-prop")

        self.assertEqual(ret, {"status": "ok"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @respx.mock
    async def test_get_pluggable_props_failure(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.get(
            "https://example.com/api/v1/subjects/sys-1/props/",
            params__eq={"p": "my-prop", "key": "value"},
        ).respond(status_code=400, json={"error": "ko"})

        with self.assertRaises(AsyncEngineClientError) as cm:
            await engine.get_pluggable_props("sys-1", "my-prop", key="value")

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @respx.mock
    async def test_direct_get_success(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.get(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key": "value"},
        ).respond(json={"status": "ok"})

        ret = await engine.direct_get("sys-1", "/my-path/", {"key": "value"})

        self.assertEqual(ret, {"status": "ok"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @respx.mock
    async def test_direct_get_failure(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.get(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key": "value"},
        ).respond(status_code=400, json={"error": "ko"})

        with self.assertRaises(AsyncEngineClientError) as cm:
            await engine.direct_get("sys-1", "/my-path/", {"key": "value"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @respx.mock
    async def test_direct_post_success(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.post(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key1": "value1"},
        ).respond(json={"status": "ok"})

        ret = await engine.direct_post("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(ret, {"status": "ok"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"key2": "value2"})

    @respx.mock
    async def test_direct_post_failure(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.post(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key1": "value1"},
        ).respond(status_code=400, json={"error": "ko"})

        with self.assertRaises(AsyncEngineClientError) as cm:
            await engine.direct_post("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"key2": "value2"})

    @respx.mock
    async def test_direct_put_success(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.put(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key1": "value1"},
        ).respond(json={"status": "ok"})

        ret = await engine.direct_put("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(ret, {"status": "ok"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"key2": "value2"})

    @respx.mock
    async def test_direct_put_failure(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.put(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key1": "value1"},
        ).respond(status_code=400, json={"error": "ko"})

        with self.assertRaises(AsyncEngineClientError) as cm:
            await engine.direct_put("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"key2": "value2"})

    @respx.mock
    async def test_direct_patch_success(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.patch(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key1": "value1"},
        ).respond(json={"status": "ok"})

        ret = await engine.direct_patch("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(ret, {"status": "ok"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"key2": "value2"})

    @respx.mock
    async def test_direct_patch_failure(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.patch(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key1": "value1"},
        ).respond(status_code=400, json={"error": "ko"})

        with self.assertRaises(AsyncEngineClientError) as cm:
            await engine.direct_patch("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(json.loads(request.content), {"key2": "value2"})

    @respx.mock
    async def test_direct_delete_success(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.delete(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key": "value"},
        )

        ret = await engine.direct_delete("sys-1", "/my-path/", {"key": "value"})

        self.assertIsNone(ret)

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @respx.mock
    async def test_direct_delete_failure(self):
        engine = AsyncEngineClient(base_url="https://example.com", token="abcde")
        respx.delete(
            "https://example.com/s/sys-1/my-path/",
            params__eq={"key": "value"},
        ).respond(status_code=400)

        with self.assertRaises(AsyncEngineClientError):
            await engine.direct_delete("sys-1", "/my-path/", {"key": "value"})

        request = respx.calls.last.request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
