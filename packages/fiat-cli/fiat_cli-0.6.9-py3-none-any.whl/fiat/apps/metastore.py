from pathlib import Path

import typer
from rich import print
from typer import Abort

from .utils import get_logger, docker_compose_execution, docker_scripts_path

app = typer.Typer()
logger = get_logger()

metastore_docker_scripts_path = docker_scripts_path / "metastore"


@app.command("up")
def setup_metastore():
    """
    📦 Set up a Fiat metastore within local docker.
    """
    print(":star-struck: Starting Fiat metastore...")
    ret_code, container_id = docker_compose_execution(
        path=metastore_docker_scripts_path / "metastore-local.yaml",
        up_or_down=True,
        target_container="/fiat_metastore"
    )
    logger.debug(f"The exit code was: {ret_code}")
    if ret_code or not container_id:
        logger.exception("Setting up failed.")
        raise Abort()
    print(":yum: [bold green]Setup Done![/]")


@app.command("down")
def teardown_metastore():
    """
    🛑 Tearing down docker metastore.
    """
    print(":stop_sign: Closing Fiat Metastore...")
    ret_code, container_id = docker_compose_execution(
        path=metastore_docker_scripts_path / "metastore-local.yaml",
        up_or_down=False,
        target_container="/fiat_metastore"
    )
    logger.debug(f"The exit code was: {ret_code}")
    if ret_code or not container_id:
        logger.exception("Tearing down failed.")
        raise Abort()
    print(":hugging_face: [bold green]Metastore stopped![/]")


if __name__ == "__main__":
    app()
