import os
import sys
import uuid
import subprocess

import pytest
import packaging.metadata

import rez_pip.pip
import rez_pip.exceptions


def test_getBundledPip():
    """Test that the bundled pip exists and can be executed"""
    assert os.path.exists(rez_pip.pip.getBundledPip())

    subprocess.run([sys.executable, rez_pip.pip.getBundledPip(), "-h"])


def test_getPackages(pypi):
    # monkeypatch.setattr(subprocess.Popen, "stdout", '{"asd": "asd"}')
    # monkeypatch.setattr(
    #     subprocess.Popen,
    #     "poll",
    #     (
    #         None,
    #         True,
    #     ),
    # )

    packages = rez_pip.pip.getPackages(
        ["requests"],
        rez_pip.pip.getBundledPip(),
        ".".join(str(i) for i in sys.version_info[:2]),
        sys.executable,
        [],
        [],
        ["--index-url", pypi],
    )

    assert packages == [
        rez_pip.pip.PackageInfo(
            rez_pip.pip.DownloadInfo(
                f"{pypi}/requests/requests-2.30.0-py3-none-any.whl",
                rez_pip.pip.ArchiveInfo("asd"),
            ),
            True,
            True,
            packaging.metadata.RawMetadata(),
        )
    ]


def test_getPackages_error(tmpdir: pytest.TempdirFactory):
    with pytest.raises(rez_pip.exceptions.PipError):
        rez_pip.pip.getPackages(
            [str(uuid.uuid4())],
            rez_pip.pip.getBundledPip(),
            ".".join(str(i) for i in sys.version_info[:2]),
            sys.executable,
            [],
            [],
            ["--find-links", str(tmpdir), "-v"],
        )
