import json
import os
from enum import Enum

import typer
from rich import print
from typer import Abort, Option

from .templates import get_build_envd_template
from .utils import get_logger, progress_execution_with_system

app = typer.Typer()
logger = get_logger()

current_path = os.getcwd()


class BuildOutput(Enum):
    image = "image"
    tar = "tar"


def get_envd_conf(path: str | None = None):
    target_path = f"{current_path}/fiat.json" if not path else path
    with open(target_path) as file_obj:
        envd_conf = json.load(file_obj)['envd']

    logger.debug(f"Envd config loaded: {envd_conf}")

    return envd_conf


@app.command("init")
def init_envd_file(
        server: bool = Option(
            False,
            "--server", "-s",
            help="Whether to use Envd-Server or not. Set True to use the envd-server."
        ),
        server_name: str = Option(
            None,
            "--name", "-n",
            help="Envd server name."
        ),
        server_url: str = Option(
            None,
            "--url",
            help="Envd server URL."
        )
):
    """
    📝 Initialize build file into current path.
    """
    print(":yo-yo: Fiat Envd File Initialization.")
    template = get_build_envd_template()

    with open(f"{current_path}/build.envd", "w+", encoding='utf-8') as file_io:
        file_io.write(template)

    if "build.envd" not in os.listdir(current_path):
        logger.error("Init 'build.envd' file failed!")
        raise Abort()

    if server:
        command = f"envd context create " \
                  f"--name {server_name} " \
                  f"--use --builder docker-container " \
                  f"--runner envd-server " \
                  f"--runner-address {server_url}"
        logger.debug(f"Fiat Envd Context Create command: {command}")

        print(":woman_fairy: Creating envd-server context.")

        progress_execution_with_system(
            cmd=command,
            error_msg="Create Envd server context failed! Aborting."
        )

    print(":yum: [bold green]Done! Envd initialized.[/]")

    return


@app.command("build")
def setup_new_environment(
        tag: str = Option(
            None,
            "--tag", "-t",
            help="Name and optionally a tag in the 'name:tag' format. (default: PROJECT:dev)"
        ),
        output: BuildOutput = Option(
            None,
            "--output", "-o",
            help="Output format. Leave empty to package into local image hub. (e.g. tar)"
        ),
        name: str = Option(
            None,
            "--name", "-n",
            help="Image name. If output is docker hub, you may follow the formt: 'docker.io/username/image'."
        ),
        destination: str = Option(
            None,
            "--dest", "-d",
            help="Output destination."
        ),
        push: bool = Option(
            True,
            "--push", "-p",
            help="Whether to push the image onto a docker hub/registry."
        )
):
    """
    ⚒️  Build a new development environment image.
    """
    if not tag:
        tag = f"--tag {tag}"
    if output is BuildOutput.image:
        output = f"--output type={output},name={name},pull={'true' if push else 'false'}"
    elif output is BuildOutput.tar:
        output = f"--output type={output},dest={destination},pull={'true' if push else 'false'}"
    command = f"envd build {tag} {output}"
    logger.debug(f"Fiat Envd Build command: {command}")

    print(":woman_wage: Start building Envd image.")

    progress_execution_with_system(
        cmd=command,
        error_msg="Building Envd image failed! Aborting."
    )

    print(":yum: [bold green]Done! Envd image built.[/]")


@app.command("run")
def setup_new_environment(
        username: str = Option(
            ...,
            "--username", "-u",
            help="Envd Server username", prompt="Please enter your username"
        ),
        password: str = Option(
            ...,
            "--password", "-p",
            help="Envd Server password", prompt="Please enter your password"
        ),
        image: str = Option(
            ...,
            "--image", "-i",
            help="Target image that you'd like to use.", prompt="Please enter the image that you want to use"
        ),
        env_name: str = Option(
            ...,
            "--name", "-n",
            help="Name of your development environment.", prompt="Please enter your env name"
        ),
        config: str = Option(
            None,
            "--conf", "-f",
            help="Fiat config path."
        )
):
    """
    🏃️ Run the Envd environment from the existing image. ('run' is only supported in envd-server runner currently)
    """
    # First login into the Envd Server
    login_command = f"envd login -u {username} -p {password}"
    logger.debug(f"Fiat Envd Login command: {login_command}")

    print(":stuck_out_tongue: Try login into Envd server")

    progress_execution_with_system(
        cmd=login_command,
        error_msg="Cannot login into target envd server! Aborting."
    )

    print(":stuck_out_tongue_closed_eyes: Login complete!")

    # Then try to run the target environment
    envd_conf = get_envd_conf(path=config)
    run_command = f"envd run --image {image} --name {env_name} " \
                  f"--host {envd_conf['host']}" \
                  f"--cpus {envd_conf['cpu']} " \
                  f"--memory {envd_conf['mem']} " \
                  f"--gpu {envd_conf['gpu']} --detach"
    logger.debug(f"Fiat Envd Run command: {run_command}")

    progress_execution_with_system(
        cmd=run_command,
        error_msg="Cannot run the target environment on Envd-server! Aborting."
    )

    print(":yum: [bold green]Done! Envd environment is running.[/]")


@app.command("up")
def setup_new_environment(
        env_name: str = Option(
            os.getcwd().split('/')[-1],
            "--name", "-n",
            help="Name of your development environment."
        ),
        tag: str = Option(
            None,
            "--tag", "-t",
            help="Name and optionally a tag in the 'name:tag' format. (default: PROJECT:dev)"
        ),
        use_gpu: bool = Option(
            False,
            "--gpu",
            help="Use CPU container or GPU container."
        ),
        config: str = Option(
            None,
            "--conf", "-f",
            help="Fiat config path."
        ),
        volume: str = Option(
            None,
            "--volume", "-v",
            help="Mount host directory into container."
        ),
):
    """
    🧸 Use Envd to set up a new development environment and attach to it. (build & run)
    """
    envd_conf = get_envd_conf(path=config)
    if tag:
        tag = f"--tag {tag} "
    if env_name:
        env_name = f"--name {env_name} "
    up_command = f"envd up --detach " \
                 f"{tag}" \
                 f"{env_name}" \
                 f"--volume {volume} " \
                 f"--host {envd_conf['host']} " \
                 f"--cpus {envd_conf['cpu']} " \
                 f"--memory {envd_conf['mem']} " \
                 f"{'--no-gpu' if not use_gpu else None}"
    logger.debug(f"Fiat Envd Up command: {up_command}")

    progress_execution_with_system(
        cmd=up_command,
        error_msg="Cannot set up the target environment on local! Aborting."
    )

    print(":yum: [bold green]Done! Envd environment is running.[/]")


@app.command("list")
def setup_new_environment():
    """
    🗑️  !!!DANGER!!! Destroy an environment.
    """
    print(":eyes: List all Envd environments.")

    command = "envd envs list"
    progress_execution_with_system(
        cmd=command,
        error_msg="Cannot list available environments! Aborting."
    )

    print(":yum: [bold green]Done![/]")


@app.command("destroy")
def setup_new_environment(
        name: str = Option(
            ...,
            "--name", "-n",
            help="Name or container ID of the Envd environment that you want to destroy.",
            prompt="Please enter the name of your target env"
        ),
        path: str = Option(
            None,
            "--path", "-p",
            help="Path to the directory containing the 'build.envd'. (default: current directory)"
        )
):
    """
    🗑️  !!!DANGER!!! Destroy an environment.
    """
    if path:
        path = f"--path {path}"
    destroy_command = f"envd destroy --name {name} {path}"
    logger.debug(f"Fiat Envd Destroy command: {destroy_command}")

    print(":wastebasket:  Trying to destroy target Envd environment.")

    progress_execution_with_system(
        cmd=destroy_command,
        error_msg="Cannot destroy target environment! Aborting."
    )

    print(":yum: [bold green]Done! Envd environment destroyed.[/]")
