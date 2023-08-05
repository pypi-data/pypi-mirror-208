import pytest
from PyraUtils.common.download import DownloadUtil as dl

def test_dl_01():
    url = "https://www.python.org/static/img/python-logo.png",
    dl_path="./tmp/python-logo.png"
    assert (dl.dl_01(url, dl_path), True)
