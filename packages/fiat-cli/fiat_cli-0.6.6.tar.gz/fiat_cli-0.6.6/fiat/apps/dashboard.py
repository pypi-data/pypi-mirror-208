from pathlib import Path

import requests
import typer
from rich import print
from typer import Option, Abort

from .utils import get_logger, docker_compose_execution, docker_scripts_path

APP_NAME = "fiat"
app = typer.Typer()
logger = get_logger()

dash_docker_scripts_path = docker_scripts_path / "dash"


@app.command("up")
def setup_dashboard(
        username: str = Option(
            "cheng2029@foxmail.com", help="Fiat username", prompt="Please enter your username"
        ),
        password: str = Option(
            "lijiacheng",
            help="Fiat password", prompt="Please enter your password",
            confirmation_prompt=True, hide_input=True
        ),
        metastore: str = Option(
            "localhost:8090", help="Fiat metastore URI", prompt="Metastore URL"
        )
):
    """
    🥸 Dashboard setup command - You need to specify your personbal USERNAME & PASSWORD, and the URI of Fiat Metastore.
    """
    body = {
        "identity": username,
        "password": password
    }
    print(f":sleuth_or_spy: User: {username}, Password: {password}, MetastoreURL: {metastore}")
    print(":star-struck: Starting Fiat Dashboard...")
    ret = requests.post(f"http://{metastore}/api/admins/auth-with-password", data=body)
    if ret.status_code == 200:
        ret_code, container_id = docker_compose_execution(
            path=dash_docker_scripts_path / "dash-local.yaml",
            up_or_down=True,
            target_container="/fiat_dashboard"
        )
        logger.debug(f"The exit code was: {ret_code}")
        if ret_code or not container_id:
            logger.exception("Setting up failed.")
            raise Abort()
    print(":yum: [bold green]Done![/]")


@app.command("down")
def teardown_dashboard():
    """
    🛑 Tearing down dashboard application.
    """
    print(":stop_sign: Closing Fiat Dashboard...")
    ret_code, container_id = docker_compose_execution(
        path=dash_docker_scripts_path / "dash-local.yaml",
        up_or_down=False,
        target_container="/fiat_dashboard"
    )
    logger.debug(f"The exit code was: {ret_code}")
    if ret_code or not container_id:
        logger.exception("Teardown failed.")
        raise Abort()
    print(":hugging_face: [bold green]Dashboard stopped![/]")


if __name__ == "__main__":
    app()
