from unittest import TestCase

import requests_mock

from rulesengine.client import EngineClient, EngineClientError


class EngineClientTestCase(TestCase):
    @requests_mock.Mocker()
    def test_push_action_success(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.post(
            "https://example.com/api/v1/subjects/sys-1/props/?a=my-action", complete_qs=True
        )

        ret = engine.push_action("sys-1", "my-action", {"key": "value"})

        self.assertIsNone(ret)

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"payload": {"key": "value"}})

    @requests_mock.Mocker()
    def test_push_action_failure(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.post(
            "https://example.com/api/v1/subjects/sys-1/props/?a=my-action",
            json={"error": "ko"},
            status_code=400,
            complete_qs=True,
        )

        with self.assertRaises(EngineClientError) as cm:
            engine.push_action("sys-1", "my-action", {"key": "value"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"payload": {"key": "value"}})

    @requests_mock.Mocker()
    def test_get_pluggable_props_success(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.get(
            "https://example.com/api/v1/subjects/sys-1/props/?p=my-prop",
            json={"status": "ok"},
            complete_qs=True,
        )

        ret = engine.get_pluggable_props("sys-1", "my-prop")

        self.assertEqual(ret, {"status": "ok"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @requests_mock.Mocker()
    def test_get_pluggable_props_failure(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.get(
            "https://example.com/api/v1/subjects/sys-1/props/?p=my-prop&key=value",
            json={"error": "ko"},
            status_code=400,
            complete_qs=True,
        )

        with self.assertRaises(EngineClientError) as cm:
            engine.get_pluggable_props("sys-1", "my-prop", key="value")

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @requests_mock.Mocker()
    def test_direct_get_success(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.get(
            "https://example.com/s/sys-1/my-path/?key=value", json={"status": "ok"}, complete_qs=True
        )

        ret = engine.direct_get("sys-1", "/my-path/", {"key": "value"})

        self.assertEqual(ret, {"status": "ok"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @requests_mock.Mocker()
    def test_direct_get_failure(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.get(
            "https://example.com/s/sys-1/my-path/?key=value",
            json={"error": "ko"},
            status_code=400,
            complete_qs=True,
        )

        with self.assertRaises(EngineClientError) as cm:
            engine.direct_get("sys-1", "/my-path/", {"key": "value"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @requests_mock.Mocker()
    def test_direct_post_success(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.post(
            "https://example.com/s/sys-1/my-path/?key1=value1", json={"status": "ok"}, complete_qs=True
        )

        ret = engine.direct_post("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(ret, {"status": "ok"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"key2": "value2"})

    @requests_mock.Mocker()
    def test_direct_post_failure(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.post(
            "https://example.com/s/sys-1/my-path/?key1=value1",
            json={"error": "ko"},
            status_code=400,
            complete_qs=True,
        )

        with self.assertRaises(EngineClientError) as cm:
            engine.direct_post("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"key2": "value2"})

    @requests_mock.Mocker()
    def test_direct_put_success(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.put(
            "https://example.com/s/sys-1/my-path/?key1=value1", json={"status": "ok"}, complete_qs=True
        )

        ret = engine.direct_put("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(ret, {"status": "ok"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"key2": "value2"})

    @requests_mock.Mocker()
    def test_direct_put_failure(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.put(
            "https://example.com/s/sys-1/my-path/?key1=value1",
            json={"error": "ko"},
            status_code=400,
            complete_qs=True,
        )

        with self.assertRaises(EngineClientError) as cm:
            engine.direct_put("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"key2": "value2"})

    @requests_mock.Mocker()
    def test_direct_patch_success(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.patch(
            "https://example.com/s/sys-1/my-path/?key1=value1", json={"status": "ok"}, complete_qs=True
        )

        ret = engine.direct_patch("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(ret, {"status": "ok"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"key2": "value2"})

    @requests_mock.Mocker()
    def test_direct_patch_failure(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.patch(
            "https://example.com/s/sys-1/my-path/?key1=value1",
            json={"error": "ko"},
            status_code=400,
            complete_qs=True,
        )

        with self.assertRaises(EngineClientError) as cm:
            engine.direct_patch("sys-1", "/my-path/", {"key1": "value1"}, {"key2": "value2"})

        self.assertEqual(cm.exception.__cause__.response.json(), {"error": "ko"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
        self.assertEqual(request.json(), {"key2": "value2"})

    @requests_mock.Mocker()
    def test_direct_delete_success(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.delete("https://example.com/s/sys-1/my-path/?key=value", complete_qs=True)

        ret = engine.direct_delete("sys-1", "/my-path/", {"key": "value"})

        self.assertIsNone(ret)

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")

    @requests_mock.Mocker()
    def test_direct_delete_failure(self, engine_api_mock):
        engine = EngineClient(base_url="https://example.com", token="abcde")
        engine_api_mock.delete(
            "https://example.com/s/sys-1/my-path/?key=value", status_code=400, complete_qs=True
        )

        with self.assertRaises(EngineClientError):
            engine.direct_delete("sys-1", "/my-path/", {"key": "value"})

        request = engine_api_mock.last_request
        self.assertEqual(request.headers["X-Auth-Token"], "abcde")
