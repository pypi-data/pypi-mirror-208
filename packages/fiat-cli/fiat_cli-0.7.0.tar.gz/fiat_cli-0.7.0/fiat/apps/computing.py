from pathlib import Path

import typer
from rich import print
from typer import Abort

from .utils import get_logger, docker_compose_execution, docker_scripts_path

app = typer.Typer()
logger = get_logger()

ray_docker_scripts_path = docker_scripts_path / "ray"


@app.command("up")
def setup_server():
    """
    🚀 Set up a Fiat computing server
    """
    print(":star-struck: Starting Fiat computing server...")
    ret_code, container_id = docker_compose_execution(
        path=ray_docker_scripts_path / "server-local.yaml",
        up_or_down=True,
        target_container="/fiat_head"
    )
    logger.debug(f"The exit code was: {ret_code}")
    if ret_code or not container_id:
        logger.exception("Setting up failed.")
        raise Abort()
    print(":yum: [bold green]Setup Done![/]")


@app.command("down")
def teardown_server():
    """
    🛑 Tearing down Fiat computing server.
    """
    print(":stop_sign: Closing Fiat computing server...")
    ret_code, container_id = docker_compose_execution(
        path=ray_docker_scripts_path / "server-local.yaml",
        up_or_down=False,
        target_container="/fiat_metastore"
    )
    logger.debug(f"The exit code was: {ret_code}")
    if ret_code or not container_id:
        logger.exception("Tearing down failed.")
        raise Abort()
    print(":hugging_face: [bold green]Fiat server stopped![/]")


if __name__ == "__main__":
    app()
