from requests import Session
from geovisio_cli.model import Geovisio
from geovisio_cli.exception import CliException, raise_for_status
import getpass
from rich.prompt import Prompt


def _get_keycloak_authenticate_form_url(response):
    """Little hack to parse keycloak HTML to get the url to the authenticate form"""
    import re

    url = re.search('action="(.*login-actions/authenticate[^"]*)"', response.text)

    if not url:
        raise CliException(
            f"The geovisio instance does not seems to be configurated with keycloak, log in is not implemented with other solution for the moment"
        )
    url = url.group(1).replace("&amp;", "&")
    return url


def login(s: Session, geovisio: Geovisio):
    """
    Login to geovisio and store auth cookie in session
    """

    # we need to authenticate ourselves
    login = s.get(f"{geovisio.url}/api/auth/login")

    # For the moment we only manage login on keycloak via password, we'll need to change this for api token
    url = _get_keycloak_authenticate_form_url(login)

    if geovisio.user is None:
        username = Prompt.ask("👤 Enter username")
    else:
        username = geovisio.user

    if geovisio.password is None:
        password = Prompt.ask(prompt="🗝 Enter password", password=True)
    else:
        password = geovisio.password

    r = s.post(
        url,
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=True,
    )

    # a bit hacky, but since for the moment we only submit a form to keycloak, to know if the login was successful,
    # we need to check that we were redirected to geovisio
    raise_for_status(r, "Impossible to log in geovisio")
    if len(r.history) == 0:
        raise CliException(
            "The username or password is invalid, make sure you have correct credentials and please retry."
        )
