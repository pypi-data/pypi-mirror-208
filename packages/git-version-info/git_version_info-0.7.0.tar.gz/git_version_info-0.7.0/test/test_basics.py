import os
import re

import version_info as vs


def test_version_of_package():
    print(f"Version = {vs.__version__}")

    assert re.match(r"^v\d+\.\d+(\.\d+)?", vs.__version__)


def test_calling_git():
    assert "unknown" not in vs.get_version()


def test_overriding():
    os.environ["GIT_DESCRIBE"] = "123.321"
    assert vs.get_version() == "123.321"
    del os.environ["GIT_DESCRIBE"]

    assert "unknown" not in vs.get_version()
