import os

import typer
from rich import print
from typer import Option

from .utils import get_logger, progress_execution_with_system

app = typer.Typer()
logger = get_logger()

current_path = os.getcwd()


@app.command("run")
def start_dagster_dev_server(
        asset_files: str = Option(
            ...,
            "--file", "-f",
            help="Your assets file paths. Use ',' to divide each path if there are multiple files. (e.g. 'a.py,b.py')",
            prompt="Please enter your assets file paths"
        ),
        host: str = Option(
            None,
            "--host", "-h",
            help="Development Dagster server host"
        ),
        port: str = Option(
            None,
            "--port", "-p",
            help="Development Dagster server port"
        )

):
    """
    🤹 Start a local dagster dev instance to run assets.
    """
    asset_file_paths = asset_files.split(',')
    command = "dagster dev"
    if host:
        command += f"--host {host}"
    if port:
        command += f"--port {port}"

    if len(asset_file_paths) == 1:
        command = command + f" --python-file {asset_files}"
    else:
        for path in asset_file_paths:
            command += f" -f {path}"
    logger.debug(f"Fiat Dagster DagitUI instance Create command: {command}")

    print(":octopus: Creating Dagster DagitUI instance")

    progress_execution_with_system(
        cmd=command,
        error_msg="Create Dagster DagitUI instance failed! Aborting."
    )

    print(":yum: [bold green]Done![/]")
