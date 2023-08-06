import os.path

import pytest

import pymadx

PATH_TO_TEST_INPUT = "{}/../test_input/".format(
    os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def atf2_tfs_path():
    return "{}/atf2-nominal-twiss-v5.2.tfs.tar.gz".format(
        PATH_TO_TEST_INPUT)

@pytest.fixture()
def atf2(atf2_tfs_path):
    return pymadx.Data.Tfs(atf2_tfs_path)

def test_IndexFromNearestS(atf2):
    assert atf2.IndexFromNearestS(0.) == 3
    assert atf2.IndexFromNearestS(0.2) == 3
    assert atf2.IndexFromNearestS(0.5) == 9
    assert atf2.IndexFromNearestS(0.6) == 12
