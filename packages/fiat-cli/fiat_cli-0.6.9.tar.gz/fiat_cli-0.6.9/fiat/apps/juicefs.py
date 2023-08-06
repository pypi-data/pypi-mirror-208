import json
from enum import Enum
from typing import Annotated

import typer
import urllib3
from rich import print
from typer import Abort, Option, Argument

from .server import send_request_to_backend, FiatBackendRequest
from .utils import get_logger, app_conf_dir, progress_execution_with_subproc, simple_execution_with_system

app = typer.Typer()
logger = get_logger()


class StorageType(Enum):
    S3 = "s3"
    OSS = "oss"
    OBS = "obs"
    COS = "cos"
    SFTP = "sftp"


def get_fs_conf():
    path = f"{app_conf_dir}/application.json"
    try:
        with open(path, "r+", encoding='utf-8') as file_obj:
            conf = json.load(file_obj)
    except FileNotFoundError:
        logger.error(f"Config file - 'application.json' not found in {path}.")

        raise Abort()

    return conf


@app.command("format")
def format_new_fs(
        name: Annotated[str, Argument(
            default="my-jfs",
            help="Name of your DFS."
        )],
        storage_type: StorageType = Option(
            ...,
            "--store", "-s",
            help="Object Storage Type.", prompt="Please enter storage type"
        ),
        bucket: str = Option(
            ...,
            "--bucket", "-b",
            help="Object Storage URL - Typically this is your S3 domain.", prompt="Please enter object storage URL"
        ),
        metadata_engine: str = Option(
            ...,
            "--meta", "-m",
            help="Metadata Engine URL.", prompt="Please enter metadata engine URL"
        ),
        access_key: str = Option(
            ...,
            "--access-key",
            help="Bucket access key.", prompt="Please enter bucket access key"
        ),
        secret_key: str = Option(
            ...,
            "--secret-key",
            help="Bucket secret key.", prompt="Please enter bucket secret key"
        ),
        password: str = Option(
            ...,
            "--password", "-p",
            help="Your Fiat backend password", prompt="Please enter your Fiat password"
        )
):
    """
    💼 Format a new DFS with JuiceFS
    """
    command = f"juicefs format " \
              f"--storage {storage_type.value} " \
              f"--bucket {bucket} " \
              f"--access-key {access_key} " \
              f"--secret-key {secret_key} " \
              f"{metadata_engine} {name}"
    logger.debug(f"Formating INFO: {command}")

    print(":zap: Start formating DFS.")
    progress_execution_with_subproc(
        cmd=command,
        error_msg="Formatting DFS failed! Aborting."
    )

    print(":truck: Persist DFS Metadata into Fiat Metastore.")
    url_parsed = urllib3.util.parse_url(metadata_engine)
    dfs_meta_body = {
        "name": name,
        "metadata": {
            "engine": f"{url_parsed.scheme}://",
            "host_url": metadata_engine,
        },
        "object_store": {
            "provider": storage_type.value,
            "bucket_url": bucket,
            "access_key": access_key,
            "secret_key": secret_key
        },
    }
    send_request_to_backend(
        api=FiatBackendRequest.DFSCreate,
        payload=dfs_meta_body,
        password=password
    )
    print(":trumpet: Metadata persistence complete!")

    print(":yum: [bold green]Done! DFS formated.[/]")

    return


@app.command("status")
def get_dfs_info(
        metastore: str = Option(
            ...,
            "--meta", "-m",
            help="Metadata Engine URL.", prompt="Please enter metadata engine URL"
        ),
):
    """
    🤵 Get information of a pre-configured DFS.
    """
    command = f"juicefs status {metastore}"
    logger.debug(f"Status Command: {command}")

    print(":yawning_face: Get information from a DFS.")

    progress_execution_with_subproc(
        cmd=command,
        error_msg="Statusing DFS failed! Aborting."
    )

    print(":yum: [bold green]Done![/]")

    return


@app.command("mount")
def mount_fs(
        metastore: str = Option(
            ...,
            "--meta", "-m",
            help="Metadata Engine URL.", prompt="Please enter metadata engine URL"
        ),
        mounting_path: str = Option(
            ...,
            "--path", "-p",
            help="Path that you want to mount the DFS on.", prompt="Please enter target path to be mounted on"
        ),
):
    """
    🎒 Mount a pre-configured DFS on your computer or development environment.
    """
    command = f"juicefs mount --background {metastore} {mounting_path}"
    logger.debug(f"Mounting Command: {command}")

    print(":wrench: Mounting DFS.")

    progress_execution_with_subproc(
        cmd=command,
        error_msg="Mounting DFS failed! Aborting."
    )

    print(":yum: [bold green]Done! DFS Mounted.[/]")

    return


@app.command("unmount")
def unmount_fs(
        mounting_path: str = Option(
            ...,
            "--path", "-p",
            help="DFS mounting path", prompt="Please enter the mounted path"
        ),
        force: bool = Option(
            False,
            "--force", "-f",
            help="Forcebly unmount a mounted DFS."
        )
):
    """
    🛁 Unmount a pre-configured DFS from your computer or development environment.
    """
    command = f"juicefs umount "
    if force:
        command += "--force "
    command += mounting_path
    logger.debug(f"Unmounting Command: {command}")

    print(":wrench: Unmounting DFS.")

    progress_execution_with_subproc(
        cmd=command,
        error_msg="Unmounting DFS failed! Aborting."
    )

    print(":yum: [bold green]Done! DFS Unmounted.[/]")

    return


@app.command("delete")
def destroy_fs(
        metastore: str = Option(
            ...,
            "--meta", "-m",
            help="Metadata Engine URL.", prompt="Please enter metadata engine URL"
        ),
        fs_uuid: str = Option(
            ...,
            "--uuid", "-u",
            help="UUID of your target DFS", prompt="Please enter DFS's uuid"
        ),
        metastore_id: str = Option(
            ...,
            "--id", "-r",
            help="Record ID of your DFS in Fiat Metastore", prompt="Please enter DFS's record ID in Metastore"
        )
):
    """
    🤯 !!!DANGER!!! - Destroy an existing DFS with Metaengine URL and its UUID
    """
    command = f"juicefs destroy {metastore} {fs_uuid}"
    logger.debug(f"Unmounting Command: {command}")

    print(":hammer_and_wrench: Destroying DFS.")
    simple_execution_with_system(
        cmd=command,
        error_msg="Destroying DFS failed! Aborting."
    )
    print(":two-hump_camel: Delete DFS Metadata from Fiat Metastore.")
    send_request_to_backend(
        api=FiatBackendRequest.DFSDelete,
        query={
            "juicefs-id": metastore_id
        }
    )
    print(":vulcan_salute: DFS Metadata deleted!")

    print(":yum: [bold green]Done! DFS Destroyed.[/]")

    return
