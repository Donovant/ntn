from uuid import UUID, uuid4
import pytest
import json
import requests
import os
import sys
import inspect
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)

# All tests are skipped for endpoints in unimplemented.
unimplemented = []

def pytest_addoption(parser):
    """Called before the command line is parsed"""
    parser.addoption('--host', action='store',
        default='http://127.0.0.1:2300',
        help='<http|https>://<host>:<port>. * default: http://127.0.0.1:2300')


def pytest_runtest_setup(item):
    """Called before each test is run"""
    # skip enpoints not implemented yet
    for endpoint in unimplemented:
        if endpoint in item.name:
            pytest.skip("Not Implemented: {}".format(endpoint))


@pytest.fixture(scope='session')
def http_pool(request):
    with requests.Session() as s:
        yield s


@pytest.fixture(scope='session')
def host(request):
    return request.config.getoption('--host')
