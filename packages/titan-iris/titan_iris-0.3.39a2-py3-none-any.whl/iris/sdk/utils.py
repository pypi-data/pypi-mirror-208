"""This file contains the helper functions for the Iris package."""
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import functools
import gzip
import io
import json
import tarfile
from logging import getLogger
from pathlib import Path
from typing import Callable, Optional

import docker
import jmespath
import requests
import wget
from rich.progress import Progress
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from iris.sdk.exception import DownloadLinkNotFoundError

from .conf_manager import conf_mgr

logger = getLogger("iris.utils")

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                                         Utils                                                        #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #

# ------------------------------  Helper Function for Iris Pull, Upload and Download   ------------------------------ #


def make_targz(local_folder_path: str):
    """Create a tar.gz archive of the local folder - make this deterministic / exclude timestamp info from gz header.

    Args:
        local_folder_path: The folder to be converted to a tar.gz

    Returns: A buffer containing binary of the folder as a tar.gz file

    """
    tar_buffer = io.BytesIO()
    block_size = 4096
    # Add files to a tarfile, and then by-chunk to a tar.gz file.
    with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
        tar.add(
            local_folder_path,
            arcname=".",
            filter=lambda x: None if "pytorch_model.bin" in x.name else x,
        )
        # Exclude pytorch_model.bin if present, as safetensors should be uploaded instead.
        with gzip.GzipFile(
            filename="",  # do not emit filename into the output gzip file
            mode="wb",
            fileobj=tar_buffer,
            mtime=0,
        ) as myzip:
            for chunk in iter(lambda: tar_buffer.read(block_size), b""):
                myzip.write(chunk)

            return tar_buffer


def copy_local_folder_to_image(container, local_folder_path: str, image_folder_path: str) -> None:
    """Helper function to copy a local folder into a container."""
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
        tar.add(local_folder_path, arcname=".")
    tar_buffer.seek(0)

    # Copy the tar archive into the container
    container.put_archive(image_folder_path, tar_buffer)


def show_progress(line, progress, tasks):  # sourcery skip: avoid-builtin-shadow
    """Show task progress for docker pull command (red for download, green for extract)."""
    if line["status"] == "Downloading":
        id = f'[red][Download {line["id"]}]'
    elif line["status"] == "Extracting":
        id = f'[green][Extract  {line["id"]}]'
    else:
        # skip other statuses
        return

    if id not in tasks.keys():
        tasks[id] = progress.add_task(f"{id}", total=line["progressDetail"]["total"])
    else:
        progress.update(tasks[id], completed=line["progressDetail"]["current"])


def download_model(download_url: str, model_name: str, path: str = "model_storage"):
    """Helper function for iris download to download model to local machine giving download url.

    Args:
        download_url (str): url to download the model
        model_name (str): name of the model
        path (str, optional): path for model storage . Defaults to "model_storage".

    Raises:
        DownloadLinkNotFoundError: Download link expired error
    """
    # download the tar file
    try:
        tarfile_path = wget.download(download_url, path)  # response is the path to the downloaded file
    except Exception as e:
        raise DownloadLinkNotFoundError from e

    # Extract the tar file to a folder on the local file system
    with tarfile.open(tarfile_path) as tar:
        tar.extractall(path=f"model_storage/{model_name}/models")

    # delete the tar file
    Path(tarfile_path).unlink()


def pull_image(
    model_folder_path: str,
    container_name: str,
    job_tag: str,
    task_name: str,
    baseline_model_name: str,
    baseline: bool,
):
    """Pull image.

    This function handles the logic of pulling the base image and creating a new image with
    the model files copied into it.

    Args:
        model_folder_path: The path to the model folder
        container_name: The name of the container
        job_tag: The tag of the job
        task_name: The name of the task
        baseline_model_name: The name of the baseline model
        baseline: Whether the model is the baseline model

    """
    temp_container_name = f"temp-{container_name}"

    env_var = {
        "TASK_NAME": task_name,
        "BASELINE_MODEL_NAME": baseline_model_name,
        "BASELINE": str(baseline),
    }

    tasks = {}
    with Progress() as progress:
        # docker pull the base image
        client = docker.from_env()
        resp = client.api.pull(conf_mgr.BASE_IMAGE, stream=True, decode=True)
        for line in resp:
            show_progress(line, progress, tasks)

    # Create a new temp container
    container = client.containers.create(image=conf_mgr.BASE_IMAGE, name=temp_container_name, environment=env_var)

    copy_local_folder_to_image(container, model_folder_path, "/usr/local/triton/models/")

    # Commit the container to a new image
    container.commit(repository=container_name)

    client.images.get(container_name).tag(f"{container_name}:{job_tag}")

    # Remove the original tag
    client.images.remove(container_name)
    # Remove the temp container
    container.remove()


def dump(response, query: Optional[str] = None):
    """load, a response, optionally apply a query to its returned json, and then pretty print the result."""
    content = json.loads(response.text)
    if query:
        try:
            content = jmespath.search(query, content)
        except jmespath.exceptions.ParseError as e:
            print("Error parsing response")
            raise e

    return json.dumps(
        {"status": response.status_code, "response": content},
        indent=4,
    )


def upload_from_file(tarred: io.BytesIO, dst: str):
    """Upload a file from src (a path on the filesystm) to dst.

    Args:
        tarred (io.BytesIO): The file to upload. (e.g. a tarred file).
        dst (str): The url of the destination.
        Must be a url to which we have permission to send the src, via PUT.

    Returns:
        Tuple[str, requests.Response]: A hash of the file, and the response from the put request.
    """
    with tqdm(
        desc="Uploading",
        total=tarred.getbuffer().nbytes,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as t:
        tarred.seek(0)
        reader_wrapper = CallbackIOWrapper(t.update, tarred, "read")
        response = requests.put(dst, data=reader_wrapper)
        response.raise_for_status()
        return response


def exception_to_json_error(e: Exception):
    """Convert an exception to a json string with the error message and type."""
    logger.exception(e)
    error_dict = {"status": "failed", "error": str(e), "type": type(e).__name__}
    if hasattr(e, "status_code"):
        error_dict["status_code"] = e.status_code
    return json.dumps(error_dict, indent=4)


def telemetry_decorator(function: Callable):
    """Decorator to send telemetry data to the metrics server."""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        # Nickname is only present if the user is logged in, and
        # if the user is _a user_ i.e. not a client credentials flow machine.
        nickname = (
            conf_mgr.current_user["nickname"]
            if conf_mgr.current_user is not None and "nickname" in conf_mgr.current_user
            else None
        )

        try:
            func = function(*args, **kwargs)

            headers = {"Content-Type": "application/json"}
            headers.update({"Authorization": f"Bearer {conf_mgr.access_token}"})
            url = conf_mgr.metrics_url
            payload = {
                "username": nickname,
                "method": function.__name__,
                "args": tuple(str(i) for i in args),
                "kwargs": kwargs,
                "error": None,
            }
            requests.post(url=url, headers=headers, data=json.dumps(payload))

            return func
        except Exception as e:
            try:
                headers = {"Content-Type": "application/json"}
                headers.update({"Authorization": f"Bearer {conf_mgr.access_token}"})
                url = conf_mgr.metrics_url

                payload = {
                    "username": nickname,
                    "method": function.__name__,
                    "args": tuple(str(i) for i in args),
                    "kwargs": kwargs,
                    "error": str(e),
                }
                requests.post(url=url, headers=headers, data=json.dumps(payload))
            except Exception as e:
                pass
            finally:
                raise

    @functools.wraps(function)
    def dummy_wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper if conf_mgr.TELEMETRY else dummy_wrapper
