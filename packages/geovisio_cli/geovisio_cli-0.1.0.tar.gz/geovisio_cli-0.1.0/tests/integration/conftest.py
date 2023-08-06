import pytest
import os
from geovisio_cli.model import Geovisio


@pytest.fixture(scope="module")
def geovisio(pytestconfig):
    external_geovisio_url = pytestconfig.getoption("--external-geovisio-url")
    if external_geovisio_url:
        yield Geovisio(url=external_geovisio_url)
        return

    from testcontainers import compose

    dco_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "docker-compose-geovisio.yml"
    )
    with compose.DockerCompose(
        ".",
        compose_file_name=dco_file,
        pull=True,
    ) as compose:
        port = compose.get_service_port("geovisio-api", 5000)
        api_url = f"http://localhost:{port}"
        compose.wait_for(api_url)

        yield Geovisio(url=api_url)
        stdout, stderr = compose.get_logs()
        if stderr:
            print("Errors\n:{}".format(stderr))
