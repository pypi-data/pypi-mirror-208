import requests

import kivalu


def test_basic_usage():
    server = kivalu.TestServer({"key": "value"})
    server.start()

    response = requests.get("http://127.0.0.1:8000/key")
    assert response.ok
    assert response.text == "value"

    server.stop()


def test_context_manager_usage():
    with kivalu.TestServer({"key": "value"}):
        response = requests.get("http://127.0.0.1:8000/key")
        assert response.ok
        assert response.text == "value"


def test_another_address_and_port():
    with kivalu.TestServer({"key": "value"}, address="0.0.0.0", port=8001):
        response = requests.get("http://0.0.0.0:8001/key")
        assert response.ok
        assert response.text == "value"


def test_setting_the_data_afterwards():
    with kivalu.TestServer() as server:
        server.data = {"key": "value"}

        response = requests.get("http://127.0.0.1:8000/key")
        assert response.ok
        assert response.text == "value"


def test_changing_the_data_while_running():
    with kivalu.TestServer({"key": "value"}) as server:
        response = requests.get("http://127.0.0.1:8000/key")
        assert response.ok
        assert response.text == "value"

        server.data = {"key": "new value"}

        response = requests.get("http://127.0.0.1:8000/key")
        assert response.ok
        assert response.text == "new value"


def test_missing_key():
    with kivalu.TestServer():
        response = requests.get("http://127.0.0.1:8000/key")
        assert response.status_code == 404


def test_multiple_keys():
    with kivalu.TestServer({"lorem": "ipsum", "dolor/sit": "amet", "consectetur/adipiscing": "elit"}):
        assert requests.get("http://127.0.0.1:8000/lorem").text == "ipsum"
        assert requests.get("http://127.0.0.1:8000/dolor/sit").text == "amet"
        assert requests.get("http://127.0.0.1:8000/consectetur/adipiscing").text == "elit"


def test_access_logs():
    with kivalu.TestServer() as server:
        requests.get("http://127.0.0.1:8000/lorem")
        requests.get("http://127.0.0.1:8000/lorem")
        requests.get("http://127.0.0.1:8000/dolor/sit")

        assert server.access_logs == ["/lorem", "/lorem", "/dolor/sit"]
