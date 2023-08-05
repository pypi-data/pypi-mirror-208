import argparse
from pathlib import Path

import kivalu


def test_defaults():
    argparser = kivalu.build_argument_parser()
    args = argparse.Namespace(url=None, failover=None, levels=None, extra_vars=None, timeout=None, cache=None, configuration_file=Path("/etc/kivalu.conf"))

    assert args == argparser.parse_args([])


def test_parameters():
    argparser = kivalu.build_argument_parser()
    args = argparse.Namespace(url="http://localhost:8000", failover="http://localhost:8001", levels=["lorem", "ipsum"], extra_vars={"alpha": "beta"}, timeout=0.5, cache=1, configuration_file=Path("/tmp/kivalu.conf"))

    assert argparser.parse_args(["-u", "http://localhost:8000", "--failover", "http://localhost:8001", "-l", "lorem", "-l", "ipsum", "-e", "alpha", "beta", "-t", "0.5", "-c", "1", "-f", "/tmp/kivalu.conf"]) == args
    assert argparser.parse_args(["--url", "http://localhost:8000", "--failover", "http://localhost:8001", "--level", "lorem", "--level", "ipsum", "--extra-vars", "alpha", "beta", "--timeout", "0.5", "--cache", "1", "--configuration-file", "/tmp/kivalu.conf"]) == args
