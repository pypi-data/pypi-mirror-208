import kivalu


def test_with_defaults(tmp_path, capsys):
    file = tmp_path.joinpath("kivalu.conf")

    kivalu.main(["--configuration-file", str(file)])

    assert capsys.readouterr().out == ""
    assert file.read_text(kivalu.ENCODING) == '{"url": "https://hub.zebr0.io", "failover": "", "levels": [], "extra-vars": {}, "timeout": 3.05, "cache": 300}'


def test_nominal(server, tmp_path, capsys):
    server.data = {"alpha/beta/key": "{{ variable }}"}
    file = tmp_path.joinpath("kivalu.conf")

    kivalu.main(["--url", "http://localhost:8001", "--failover", "http://localhost:8000", "--level", "alpha", "--level", "beta", "--extra-vars", "variable", "value", "--timeout", "2", "--cache", "1", "--configuration-file", str(file), "--test", "key"])

    assert capsys.readouterr().out == "value\n"
    assert file.read_text(kivalu.ENCODING) == '{"url": "http://localhost:8001", "failover": "http://localhost:8000", "levels": ["alpha", "beta"], "extra-vars": {"variable": "value"}, "timeout": 2.0, "cache": 1}'
