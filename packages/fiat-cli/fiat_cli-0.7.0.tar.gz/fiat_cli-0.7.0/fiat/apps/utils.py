import json
import logging
import os
import subprocess
from pathlib import Path

import click
from typer import Abort
from rich import print
from rich.logging import RichHandler

import docker
from rich.progress import Progress, SpinnerColumn, TextColumn

home_path = Path(os.environ['HOME'])
app_conf_dir = home_path / ".fiat"
docker_scripts_path = app_conf_dir / "docker"
current_path = os.getcwd()


def get_user_config() -> dict:
    try:
        with open(f"{current_path}/fiat.json", "r+") as file_obj:
            conf = json.load(file_obj)

        logging.debug(f"User configuration loaded: {conf}")
    except FileNotFoundError:
        logging.error("Please make sure you have the config file 'fiat.json' on your current folder.")
        raise Abort()

    return conf


def get_logger():
    conf = get_user_config()

    if "log_level" in conf.keys():
        log_level = conf['log_level']
    else:
        log_level = "INFO"

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[click])]
    )
    log = logging.getLogger("rich")

    return log


logger = get_logger()


def container_assertion(name: str, status: str):
    try:
        client = docker.from_env()
    except EnvironmentError:
        logger.exception(
            ":exclamation: Docker client setup failed, please check if you have started your docker engine.",
            extra={"markup": True}
        )
        raise click.Abort()

    container_id = [
        container.attrs['Id'] for container in client.containers.list(
            filters={
                "name": name,
                "status": status
            }
        )
    ]
    if len(container_id) == 0:
        return -1

    client.close()

    return container_id[0]


def compose_up_assertion(container_name: str):
    ret = container_assertion(container_name, "running")
    return ret


def compose_down_assertion(container_name: str):
    ret = container_assertion(container_name, "running")
    return ret


def docker_compose_execution(path: Path, up_or_down: bool, target_container: str):
    if path.is_dir():
        logger.exception(":exclamation: need to specify a docker-compose '.yml' file",
                         extra={"markup": True})
        raise click.Abort()
    if path.is_file() and not (path.name.endswith('yaml') or path.name.endswith('yml')):
        logger.exception(":exclamation:",
                         extra={"markup": True})
    prefix = 'docker-compose -p fiat -f'
    cmd = f'{prefix} {path} up -d' if up_or_down else f'{prefix} {path} down'
    output = subprocess.run(
        cmd.split(' '),
        stdout=subprocess.PIPE,
        text=True,
    )
    subproc_ret = output.returncode
    container_id = compose_up_assertion(container_name=target_container) \
        if up_or_down else compose_up_assertion(container_name=target_container)

    return subproc_ret, container_id


def execute_subprocess_cmd(cmd: str):
    output = subprocess.run(
        cmd.split(' '),
        stdout=subprocess.PIPE,
        text=True,
    )
    subproc_ret = output.returncode
    text = output.stdout

    return subproc_ret, text


def progress_execution_with_subproc(
        cmd: str,
        error_msg: str
):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description="🏷  Fiat CLI Processing...", total=None)

        ret, stdout = execute_subprocess_cmd(cmd)

        if ret == 1:
            logger.error(error_msg)
            raise Abort()

        print(stdout)


def simple_execution_with_subproc(
        cmd: str,
        error_msg: str
):
    ret, stdout = execute_subprocess_cmd(cmd)

    if ret == 1:
        logger.error(error_msg)
        raise Abort()

    print(stdout)


def progress_execution_with_system(
        cmd: str,
        error_msg: str
):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description="🏷  Fiat CLI Processing...", total=None)

        ret = os.system(cmd)

        if ret == 1:
            logger.error(error_msg)
            raise Abort()


def simple_execution_with_system(
        cmd: str,
        error_msg: str
):
    ret = os.system(cmd)

    if ret == 1:
        logger.error(error_msg)
        raise Abort()
