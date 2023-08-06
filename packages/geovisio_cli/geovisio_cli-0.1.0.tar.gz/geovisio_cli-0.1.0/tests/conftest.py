import os

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


def pytest_addoption(parser):
    parser.addoption("--external-geovisio-url", action="store")
