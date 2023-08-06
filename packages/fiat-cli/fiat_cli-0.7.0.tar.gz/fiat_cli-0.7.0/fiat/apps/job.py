import time

import typer
from ray.job_submission import JobSubmissionClient, JobStatus
from rich import print
from typer import Abort, Option

from .utils import get_logger

app = typer.Typer()
logger = get_logger()


def wait_until_status(
        client: JobSubmissionClient,
        job_id: str,
        timeout_seconds=10
):
    start = time.time()
    status = "PENDING"
    status_to_wait_for = {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED}
    while time.time() - start <= timeout_seconds:
        status = client.get_job_status(job_id)
        logger.debug(f"status: {status}")
        if status in status_to_wait_for:
            break
        time.sleep(1)
    print(":direct_hit: Job submission complete.")
    return status


@app.command("submit")
def submit_ray_job(
        cluster: str = Option(
            ...,
            "--cluster", "-c",
            help="Target Fiat Computing cluster URL", prompt="Please enter cluster URL"
        ),
        description_file: str = Option(
            ...,
            "--file", "-f",
            help="Descrption file of your project, please make sure it is available", prompt=True,
        ),
        timeout: int = Option(
            10, "--timeout", "-t", help="Timeout to submit the job before forcely abortion."
        )
):
    """
    📤 Job Submission Handler
    """
    # Read the description file
    with open(description_file, 'r+', encoding='utf-8') as file_obj:
        import json
        description = json.load(file_obj)
    # If using a remote cluster, replace 127.0.0.1 with the head node's IP address.
    try:
        client: JobSubmissionClient = JobSubmissionClient(f"http://{cluster}")
        job_id = client.submit_job(
            # Entrypoint bash command to execute
            entrypoint=description['entrypoint'],
            # Path to the local directory that contains the script.py file
            runtime_env=description['runtime_env']
        )
        logger.debug(f"Job submission with id: {job_id}")
    except RuntimeError:
        logger.error(f":stop: Job submission failed.", extra={"markup": True})
        raise Abort()
    except KeyError:
        logger.error(
            f":stop: Job submission failed. Please check whether you correctly define your description file.",
            extra={"markup": True}
        )
        raise Abort()

    final_status = wait_until_status(
        client=client,
        job_id=job_id,
        timeout_seconds=timeout
    )

    job_info = {
        "cluster": cluster,
        "job-id": job_id,
        "status": final_status
    }
    print(f":crab: Job metadata {job_info}")
    print(":diving_mask: You can check your job status through the Cluster URL and job id.")


@app.command("status")
def submit_ray_job(
        cluster: str = Option(
            ...,
            "--cluster", "-c",
            help="Target Fiat Computing cluster URL", prompt="Please enter cluster URL"
        ),
        job_id: str = Option(
            None,
            "--id",
            help="Target job id. Leave None to list all job details of the target cluster",
        ),
):
    """
    📑 Job Status Checker
    """
    print(":cricket_game: Fetching job details.")
    try:
        client: JobSubmissionClient = JobSubmissionClient(f"http://{cluster}")
        if not job_id:
            job_details = client.list_jobs()
            for elem in job_details:
                if elem:
                    print(elem.dict())
        else:
            job_detail = client.get_job_info(job_id)
            print(job_detail.dict())
    except RuntimeError:
        logger.error(f":stop: Cannot fetch cluster job information.", extra={"markup": True})
        raise Abort()
    print(":croissant: Done and abort.")


@app.command("log")
def get_ray_job_logs(
        cluster: str = Option(
            ...,
            "--cluster", "-c",
            help="Target Fiat Computing cluster URL", prompt="Please enter cluster URL"
        ),
        job_id: str = Option(
            ...,
            "--id",
            help="Target job id. Leave None to list all job details of the target cluster",
            prompt="Please enter the job id"
        ),
):
    """
    🖨️  Job Logging
    """
    print(":tangerine: Fetching job logs.")
    try:
        client: JobSubmissionClient = JobSubmissionClient(f"http://{cluster}")
        ret = client.get_job_logs(job_id)
        print(ret)
    except RuntimeError:
        logger.error(f":stop: Cannot fetch cluster job logs.", extra={"markup": True})
        raise Abort()
    print(":thumbs_up: Done and abort.")


@app.command("terminate")
def forcely_terminate_ray_job(
        cluster: str = Option(
            ...,
            "--cluster", "-c",
            help="Target Fiat Computing cluster URL", prompt="Please enter cluster URL"
        ),
        job_id: str = Option(
            ...,
            "--id",
            help="Target job id.",
            prompt="Please enter the job id"
        ),
):
    """
    🚫️ Job Termination
    """
    print(":stop_sign: Terminate an existing job.")
    try:
        client: JobSubmissionClient = JobSubmissionClient(f"http://{cluster}")
        ret = client.stop_job(job_id)
        print("Success!~") if ret else print("Failed...Please check your cluster url and job id!")
    except RuntimeError:
        logger.error(f":stop: Cannot fetch cluster job logs.", extra={"markup": True})
        raise Abort()
    print(":thumbs_up: Done and abort.")
