import http.server
import time
from pathlib import Path

import pytest
import requests.exceptions

import kivalu


def test_default_url():
    client = kivalu.Client(configuration_file=Path(""))

    assert client.get("domain-name") == "zebr0.io"


def test_default_levels(server):
    server.data = {"knock-knock": "who's there?"}
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""))

    assert client.get("knock-knock") == "who's there?"


def test_deepest_level(server):
    server.data = {"lorem/ipsum/dolor": "sit amet"}
    client = kivalu.Client(url="http://127.0.0.1:8000", levels=["lorem", "ipsum"], configuration_file=Path(""))

    assert client.get("dolor") == "sit amet"


def test_intermediate_level(server):
    server.data = {"consectetur/elit": "sed do"}
    client = kivalu.Client(url="http://127.0.0.1:8000", levels=["consectetur", "adipiscing"], configuration_file=Path(""))

    assert client.get("elit") == "sed do"


def test_root_level(server):
    server.data = {"incididunt": "ut labore"}
    client = kivalu.Client(url="http://127.0.0.1:8000", levels=["eiusmod", "tempor"], configuration_file=Path(""))

    assert client.get("incididunt") == "ut labore"


def test_missing_key_and_default_value(server):
    server.data = {}
    client = kivalu.Client(url="http://127.0.0.1:8000", levels=["dolore", "magna"], configuration_file=Path(""))

    assert client.get("aliqua") == ""
    assert client.get("aliqua", default="default") == "default"


def test_strip(server):
    server.data = {"knock-knock": "\nwho's there?\n"}
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""))

    assert client.get("knock-knock", strip=False) == "\nwho's there?\n"
    assert client.get("knock-knock") == "who's there?"


def test_basic_render(server):
    server.data = {"template": "{{ url }}"}
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""))

    assert client.get("template", template=False) == "{{ url }}"
    assert client.get("template") == "http://127.0.0.1:8000"


def test_globals(server):
    server.data = {
        "url": "{{ url }}",
        "failover": "{{ failover }}",
        "levels": "{{ levels | join(' ') }}",
        "extra-var": "{{ lorem }}",
        "configuration": "{{ configuration }}"
    }
    client = kivalu.Client(url="http://127.0.0.1:8000", failover="http://127.0.0.1:8001", levels=["alpha", "beta"], extra_vars={"lorem": "ipsum"}, configuration_file=Path(""))

    assert client.get("url") == "http://127.0.0.1:8000"
    assert client.get("failover") == "http://127.0.0.1:8001"
    assert client.get("levels") == "alpha beta"
    assert client.get("extra-var") == "ipsum"
    assert client.get("configuration") == '{"url": "http://127.0.0.1:8000", "failover": "http://127.0.0.1:8001", "levels": ["alpha", "beta"], "extra-vars": {"lorem": "ipsum"}, "timeout": 3.05, "cache": 300}'


def test_recursive_render(server):
    server.data = {
        "answer": "42",
        "template": "the answer is {{ 'answer' | get }}"
    }
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""))

    assert client.get("template") == "the answer is 42"


def test_recursive_nested_render(server):
    server.data = {
        "what": "memes",
        "star_wars/what": "droids",
        "star_wars/punctuation_mark": ".",
        "star_wars/slang/punctuation_mark": ", duh!",
        "template": "these aren't the {{ 'what' | get }} you're looking for{{ 'punctuation_mark' | get }}"
    }
    client = kivalu.Client(url="http://127.0.0.1:8000", levels=["star_wars", "slang"], configuration_file=Path(""))

    assert client.get("template") == "these aren't the droids you're looking for, duh!"


def test_render_with_default(server):
    server.data = {"template": "{{ 'missing_key' | get('default') }}"}
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""))

    assert client.get("template") == "default"


def test_render_with_extra_vars(server):
    server.data = {"template": "{{ variable }}"}
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""), extra_vars={"variable": "lorem ipsum"})

    assert client.get("template") == "lorem ipsum"
    assert client.get("template", extra_vars={"variable": "dolor sit amet"}) == "dolor sit amet"


def test_read_ok(tmp_path, server):
    file = tmp_path.joinpath("file")
    file.write_text("content")
    server.data = {"template": "{{ '" + str(file) + "' | read }}"}
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""))

    assert client.get("template") == "content"


def test_read_ko(tmp_path, server):
    server.data = {"template": "{{ '" + str(tmp_path.joinpath("unknown_file")) + "' | read }}"}
    client = kivalu.Client(url="http://127.0.0.1:8000", configuration_file=Path(""))

    assert client.get("template") == ""


def test_timeout():
    class TimeoutRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            time.sleep(0.2)
            self.send_response(404)
            self.end_headers()

    with kivalu.TestServer(port=8001) as server:
        server.server.RequestHandlerClass = TimeoutRequestHandler

        with pytest.raises(requests.exceptions.Timeout):
            kivalu.Client(url="http://127.0.0.1:8001", timeout=0.1, configuration_file=Path("")).get("dummy")


def test_cache(server):
    server.access_logs = []  # resetting server logs from previous tests
    server.data = {"ping": "pong", "yin": "yang"}
    client = kivalu.Client(url="http://127.0.0.1:8000", cache=1, configuration_file=Path(""))  # cache of 1 second for the purposes of the test

    assert client.get("ping") == "pong"  # "pong" is now in cache for "/ping"
    time.sleep(0.5)
    assert client.get("yin") == "yang"  # "yang" is now in cache for "/yin"
    time.sleep(0.1)
    server.data = {"ping": "peng", "yin": "yeng"}  # new values, shouldn't be used until cache has expired
    time.sleep(0.3)
    assert client.get("ping") == "pong"  # using cache for "/ping"
    time.sleep(0.2)
    assert client.get("ping") == "peng"  # 1.1 second has passed, cache has expired for "/ping", now fetching the new value
    assert client.get("yin") == "yang"  # still using cache for "/yin"
    time.sleep(0.5)
    assert client.get("yin") == "yeng"  # cache also has expired for "/yin", now fetching the new value

    assert server.access_logs == ["/ping", "/yin", "/ping", "/yin"]


def test_connection_error():
    with pytest.raises(requests.exceptions.ConnectionError):
        kivalu.Client(url="http://10.1.1.1", timeout=0.1).get("dummy")


def test_failover_ok(server):
    server.data = {"key": "value"}

    assert kivalu.Client(url="http://10.1.1.1", failover="http://127.0.0.1:8000", timeout=0.1).get("key") == "value"


def test_failover_ko(server):
    with pytest.raises(requests.exceptions.ConnectionError):
        kivalu.Client(url="http://10.1.1.1", failover="http://10.2.2.2", timeout=0.1).get("dummy")


def test_configuration_file(server, tmp_path):
    configuration_file = tmp_path.joinpath("kivalu.conf")
    configuration_file.write_text('{"url": "http://127.0.0.1:8001", "failover": "http://127.0.0.1:8000", "levels": ["lorem", "ipsum"], "extra-vars": {"variable": "value"}, "timeout": 0.5, "cache": 1}', kivalu.ENCODING)

    server.data = {"lorem/ipsum/key": "{{ variable }}"}
    client = kivalu.Client(configuration_file=configuration_file)

    assert client.get("key") == "value"


def test_save_configuration(tmp_path):
    configuration_file = tmp_path.joinpath("kivalu.conf")

    client = kivalu.Client(url="http://127.0.0.1:8000", failover="http://127.0.0.1:8001", levels=["lorem", "ipsum"], extra_vars={"variable": "value"}, timeout=0.5, cache=1, configuration_file=configuration_file)
    client.save_configuration()

    assert configuration_file.read_text(kivalu.ENCODING) == '{"url": "http://127.0.0.1:8000", "failover": "http://127.0.0.1:8001", "levels": ["lorem", "ipsum"], "extra-vars": {"variable": "value"}, "timeout": 0.5, "cache": 1}'


def test_reset_parameters(tmp_path):
    configuration_file = tmp_path.joinpath("kivalu.conf")

    client = kivalu.Client(url="http://127.0.0.1:8000", failover="http://127.0.0.1:8001", levels=["lorem", "ipsum"], extra_vars={"variable": "value"}, timeout=3, cache=1, configuration_file=configuration_file)
    client.save_configuration()

    client = kivalu.Client(url="", failover="", levels=[], extra_vars={}, timeout=1, cache=0, configuration_file=configuration_file)

    assert client.url == ""
    assert client.failover == ""
    assert client.levels == []
    assert client.extra_vars == {}
    assert client.timeout == 1
    assert client.cache == 0
