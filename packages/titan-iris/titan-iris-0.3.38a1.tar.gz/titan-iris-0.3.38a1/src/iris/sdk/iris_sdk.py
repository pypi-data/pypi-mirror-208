"""This module will contain all the sdk functions for the iris command sdk, including login, logout, get, post, pull."""
import ast
import hashlib
import json
import logging
import os
from datetime import datetime
from importlib import util
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import urljoin

# for iris infer
import numpy as np

# for iris pull
import requests
import tritonclient.http
from rich import print

# internal imports
from .auth_utils import auth, handle_bad_response
from .conf_manager import conf_mgr
from .exception import (
    ArtefactNotFoundError,
    ArtefactTypeInferError,
    ArtefactTypeNotAFolderError,
    BadRequestError,
    InvalidCommandError,
    InvalidDatasetFormatError,
    JobStillRunningError,
    MissingTokenizerError,
    UnknownFamilyError,
    UnsafeTensorsError,
    UploadOnPostError,
)
from .utils import (
    download_model,
    dump,
    exception_to_json_error,
    make_targz,
    pull_image,
    telemetry_decorator,
    upload_from_file,
)

# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #


# Whether to use tqdm for progress bars
TQDM = True

# ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                                  IRIS USERS SDK                                                     #
# ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #


# ------------------------------------      Setup Logger      ------------------------------------ #
# Logger config
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(conf_mgr.LOG_LEVEL)


# --------------------------------------      iris login    -------------------------------------- #
@auth
def login():
    """Login to Iris."""
    logger.debug("logging in")
    return conf_mgr.current_user["name"]


# --------------------------------------     iris logout    -------------------------------------- #


def logout():
    """Logout from iris.

    Just deletes the keyfile.
    """
    logger.info("logging out")
    path = Path.home() / Path(conf_mgr.config.keyfile_name)
    if path.exists():
        path.unlink()
    if not path.exists():
        return True
    else:
        return False


# --------------------------------------      iris post     -------------------------------------- #


@telemetry_decorator
@auth
def post(headers: dict = {}, **flags) -> None:
    """Dispatch a job to iris.

    Args:
        headers (dict, optional): Additional headers to add. Defaults to {}.
        **flags (dict): The flags to send to the server. These must conform to the API specification.

    Raises:
        UploadOnPostError: If there's an error uploading the artefact.
        handle_bad_response(...): If there's a bad response from the server.
    """
    endpoint = "experiment"
    # detype the flags, so we can send them
    payload = {k: str(val) if val is not None else None for k, val in flags.items()}
    logger.debug(f"Dispatching job with payload {payload}")
    url = urljoin(conf_mgr.runner_url, f"{endpoint}/")

    for local_artefact_field in ["model", "dataset"]:
        local_artefact = payload[local_artefact_field]
        if os.path.exists(local_artefact):
            print(
                f"Local {local_artefact_field} found. \
                If you intended to use a huggingface module then rename the local file."
            )  # todo
            local_uuid = upload(
                name=local_artefact.split("/")[-1],
                src=local_artefact,
                description="Experiment model",
                internal_artefact_type=local_artefact_field,
            )  # todo add more data to the uploaded model?
            if local_uuid:
                payload[local_artefact_field] = local_uuid
            else:
                raise UploadOnPostError

    headers.update({"Authorization": f"Bearer {conf_mgr.access_token}"})
    response = requests.post(url=url, headers=headers, data=payload)
    if not response.ok:
        raise handle_bad_response(response, endpoint)  # already returns json object
    else:
        print(dump(response))


# --------------------------------------       iris get     -------------------------------------- #


@telemetry_decorator
@auth
def get(
    object: str = "experiment",
    id: Optional[str] = None,
    query: Optional[str] = None,
    headers: dict = {},
    verbose: bool = True,
):
    """Get objects from the TitanML Store.

    Args:
        object (str, optional): The object to get. Defaults to "experiment".
        id (Optional[str], optional): The id of the object. Defaults to None.
        query (Optional[str], optional): A JMESPath query to run against the returned json.
                                         Defaults to None, i.e. return everything.
        headers (dict): Custom headers to send with the get request
        verbose (bool): Whether to print the response
    Returns:
        (str) A json response, formatted as: {"status": <http_response>, "response": <queried_json_response>}
    """
    logger.debug(f"Getting from ... {conf_mgr.base}, auth from {conf_mgr.AUTH0_DOMAIN}")
    logger.debug(f"Applying custom headers {headers}")
    endpoint = object + "/" + (str(id) if id is not None else "")
    url = urljoin(conf_mgr.runner_url, endpoint)
    headers.update({"Authorization": f"Bearer {conf_mgr.access_token}"})

    try:
        response = requests.get(url=url, headers=headers)
    except requests.exceptions.ConnectionError:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "message": f"Connection error: Error reaching {url}",
                },
                indent=4,
            )
        )
        raise Exception("Connection error")
    except requests.exceptions.MissingSchema:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "message": f"Scheme error: iris target specified improperly. base={conf_mgr.base}, \
                        runner_url: {conf_mgr.runner_url}, endpoint={endpoint} result={url} ",
                },
                indent=4,
            )
        )
        raise Exception("Scheme error")
    except Exception as e:
        json_error = exception_to_json_error(e)
        print(json_error)
        raise e

    if not response.ok:
        raise handle_bad_response(response, url)
    else:
        dumped_response = dump(response, query)
        if verbose:
            print(dumped_response)
        return dumped_response


# --------------------------------------     iris delete    -------------------------------------- #


@telemetry_decorator
@auth
def delete(
    object: str,
    id: Optional[str],
    verbose: bool = True,
):
    """Get objects from the TitanML Store.

    Args:
        object (str, optional): The object to get. Defaults to "experiment".
        id (str): The id of the object to delete
        verbose (bool, optional): Whether to print the response. Defaults to True.

    Returns:
        (str) A json response, formatted as:
        {"status": <http_response>, "response": <queried_json_response>}
    """
    logger.debug(f"Getting from ... {conf_mgr.base}, auth from {conf_mgr.AUTH0_DOMAIN}")
    endpoint = object + "/" + (str(id) if id is not None else "")
    url = urljoin(conf_mgr.runner_url, endpoint)
    headers = {"Authorization": f"Bearer {conf_mgr.access_token}"}

    response = requests.delete(url=url, headers=headers)
    if not response.ok:
        raise handle_bad_response(response, endpoint)
    else:
        if response.status_code == 204:
            return {"status": "success"}

        dumped_response = dump(response)
        if verbose:
            print(dumped_response)
        return dumped_response


# --------------------------------------     iris download  -------------------------------------- #


@telemetry_decorator
@auth
def download(experiment_cmd: str):
    """Downloading the models to local machine.

    Args:
        experiment_cmd (str): pulling command string. it should be formatted as <experiment_id>:<job_tag>

    Raises:
        InvalidCommandError: Invalid command error
        BadRequestError: Bad request error
        ArtefactNotFoundError: Artefact not found error

    Returns:
        model_name: name of the model
        task_name: name of the task
        baseline_model_name: name of the baseline model
        baseline: whether the model is baseline or not
    """
    # create a model_storage folder if it doesn't exist
    Path("model_storage").mkdir(parents=True, exist_ok=True)

    # parse the command string
    experiment_id_name, _, job_tag = experiment_cmd.rpartition(":")

    # check if the job tag is valid
    if job_tag not in {"baseline", "fp16", "XS", "S", "M"}:
        raise InvalidCommandError

    experiment_id, _, experiment_name = experiment_id_name.partition("-")

    # check if the experiment id is valid
    if experiment_id == "":
        raise InvalidCommandError

    # check if the experiment name is valid
    if experiment_name == "":
        print(f"Downloading model_id {experiment_id} with job tag {job_tag} ...")
    else:
        print(f"Downloading model {experiment_name} with job tag {job_tag} ...")

    # get the experiment info
    endpoint = "experiment"
    url = urljoin(conf_mgr.runner_url, f"{endpoint}/{experiment_id}")
    headers = {"Authorization": f"Bearer {conf_mgr.access_token}"}

    response = requests.get(url=url, headers=headers)
    response_json = response.json()

    # check if the request is successful
    if response_json["status"] != "success":
        raise BadRequestError

    jobs_list = response_json["experiment"]["jobs"]

    model_uuid = None
    baseline = False
    download_url, model_name, task_name, baseline_model_name = None, None, None, None
    # loop through the jobs list and find the job with the same tag
    for i in range(len(jobs_list)):
        if job_tag == jobs_list[i]["name"].split("_")[-1]:
            model_uuid = jobs_list[i]["out_art_id"]
            model_name = jobs_list[i]["name"]
            task_name = jobs_list[i]["flags"]["task"]
            baseline_model_name = jobs_list[i]["flags"]["model.teacher"]

            results = jobs_list[i]["results"]
            status = jobs_list[i]["status"]

            # check if the job is still running
            if results is None and status == "active":
                raise JobStillRunningError

            # check if the baseline model is available
            if baseline_model_name == "null":
                baseline_model_name = jobs_list[i]["flags"]["model.student"]
                baseline = True

            # check if text fields is valid in sequence classification task
            if task_name == "sequence_classification":
                text_fields = ast.literal_eval(jobs_list[i]["flags"]["data.text_fields"])  # convert string to list
                if len(text_fields) == 1:
                    task_name = "sequence_classification"
                elif len(text_fields) == 2:
                    task_name = "pair_classification"
                else:
                    raise ValueError("Invalid number of text fields")

            # check if dataset name is valid in glue task
            if task_name == "glue":
                dataset_name = jobs_list[i]["flags"]["data.dataset_config_name"]  # convert string to list
                if dataset_name in {"sst2", "cola"}:
                    task_name = "sequence_classification"  # cola and sst2 only has one sentence as input
                else:
                    task_name = "pair_classification"

            # check if artifact is available
            if model_uuid is None:
                raise ArtefactNotFoundError
            url = urljoin(
                conf_mgr.runner_url,
                f"artefact/link/{model_uuid}/download?refresh=true",
            )
            # get the download url
            response = requests.get(url=url, headers=headers)
            response_json = response.json()
            download_url = response_json["link"]["link"]
            break

    # download the model
    if download_url is not None:
        download_model(download_url, model_name)
    print(f"\nModel {model_name} downloaded successfully")
    return model_name, task_name, baseline_model_name, baseline


# --------------------------------------      iris pull     -------------------------------------- #


@telemetry_decorator
@auth
def pull(experiment_cmd: str):
    """Download the model and pull the hephaestus image from the server.

    Args:
        experiment_cmd (str): pulling command string. it should be formatted as <experiment_id>:<job_tag>

    """
    # parse the command string
    args = experiment_cmd.split(":")
    if len(args) != 2:
        raise InvalidCommandError
    experiment_id = args[0]
    job_tag = args[1]

    # download the model
    logger.info("***Executing pull command***")
    model_name, task_name, baseline_model_name, baseline = download.__wrapped__(
        experiment_cmd
    )  # this is a hack to get the function to work without the auth decorator

    # pull the image
    logger.info("Pulling image from the server")
    pull_image(
        model_folder_path=f"model_storage/{model_name}/models",
        container_name=f"iris-triton-{experiment_id}",
        job_tag=job_tag,
        task_name=task_name,
        baseline_model_name=baseline_model_name,
        baseline=baseline,
    )
    logger.info("All done!")


# --------------------------------------    iris upload     -------------------------------------- #


@telemetry_decorator
@auth
def upload(
    name: str,
    src: Union[str, Path],
    description: str,
    internal_artefact_type: Optional[str] = None,
):
    """Upload an artefact to the TitanML Store.

    Args:
        internal_artefact_type (Union[str, None]): One of ['model','dataset'] - the type of artefact purpotedly being
        uploaded when calling from iris post.
        name (str): The name of the artefact
        src (Union[str, Path]): The source of the artefact on disk
        description (str): A short description of the artefact.

    Raises:
        ArtefactNotFoundError: If the path to the artefact doesn't exist.
        UnsafeTensorsError: If the artefact is a model, and the model has not been saved in safetensors format.
    """
    # cast from path to str.
    src = str(src)

    metadata = {}

    endpoint = "artefact"
    url = urljoin(conf_mgr.runner_url, f"{endpoint}/")
    headers = {"Authorization": f"Bearer {conf_mgr.access_token}"}

    # Catches if you accidentally put a tilde in quotes:
    if src[0] == "~":
        src = os.path.expanduser(src)

    if not Path(src).is_dir():
        raise ArtefactNotFoundError(details=src)

    ext = ".tar.gz"

    namelist = os.listdir(src)

    # Set of checks to determine if the input files' format matches that expected for either a dataset or a model
    safetensors_check = tokenizer_check = val_file_check = train_file_check = False

    for x in namelist:
        # Check that safetensors are being used for the intended model
        if ".safetensors" in Path(x).suffixes:
            safetensors_check = True
            # Check the intended model has a tokenizer
        elif "tokenizer_config.json" in x:
            tokenizer_check = True
            # Check the intended dataset contains a validation and training file (csvs)
        elif "val" in x and x.endswith(".csv"):
            val_file_check = True
        elif "train" in x and x.endswith(".csv"):
            train_file_check = True

    # Check that the type of artefact being sent from iris post (for uploads originating from post rather than iris
    # upload itself) matches that of its content.
    if internal_artefact_type == "model" or safetensors_check or tokenizer_check:
        art_type = "model"
        if not safetensors_check:
            raise UnsafeTensorsError()

        if not tokenizer_check:
            raise MissingTokenizerError()

        # Family examples: DebertaV2, Albert, DistilBert, Roberta, Electra, Bert
        # Detect model family
        with open(os.path.join(src, "tokenizer_config.json"), "r") as f:
            tokenizer_class = json.load(f).get("tokenizer_class", None)
        if tokenizer_class:
            metadata["local_model_family"] = tokenizer_class.replace("Tokenizer", "").lower()
        else:
            raise UnknownFamilyError()

    elif internal_artefact_type == "dataset" or val_file_check or train_file_check:
        art_type = "dataset"
        if not val_file_check and train_file_check:
            raise InvalidDatasetFormatError()
    else:
        if os.path.isdir(src):
            raise ArtefactTypeInferError()
        else:
            raise ArtefactTypeNotAFolderError()

    logger.debug(f"Uploading {art_type} from {src} to {url}")
    # Make post request to seshat for instantiation of artefact object, and provision of presigned upload link.

    tarred = make_targz(src)
    tarred.seek(0)
    hashval = hashlib.md5(tarred.getbuffer()).hexdigest()

    post_req_data = {
        "name": name,
        "artefact_type": art_type,
        "description": description,
        "ext": ext,
        "src": src,
        "metadata": json.dumps(metadata),
        "hash": hashval,
    }

    logger.debug(f"posting {post_req_data} to {url}")
    post_req_response = requests.post(url=url, headers=headers, data=post_req_data)
    if not post_req_response.ok:
        logger.debug("post unsuccessful")
        raise handle_bad_response(post_req_response, endpoint)
    else:
        # On succesful response receipt:
        logger.debug("post successful")

        # Check if artefact-already-exists response has been received.
        if post_req_response.status_code == 202:
            existing_artefact = post_req_response.json()["artefact"]
            created_time = str(
                datetime.strptime(existing_artefact["time_created"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                    "%d-%m-%Y %H:%M:%S"
                )
            )
            # Return artefact data for found/existing artefact.
            if not internal_artefact_type:
                print(f"Artefact was already uploaded at {created_time} with ID: {existing_artefact['uuid']}")
            return existing_artefact["uuid"]

    data = post_req_response.json()["artefact"]
    art_uuid = data["uuid"]
    endpoint = "artefact/link/" + art_uuid + "/upload"
    url = urljoin(conf_mgr.runner_url, f"{endpoint}")
    logger.debug(f"Getting link from {url}")
    get_link_resp = requests.get(url=url, headers=headers)
    upl_link = get_link_resp.json()["link"]["link"]
    logger.debug(f"got link {upl_link}")

    print("Beginning upload...")

    # Upload file
    upload_response = upload_from_file(tarred, upl_link)

    # If Upload completes succesfully, send the hash to seshat in a patch request. Patch req confirms matching hash,
    # then returns the artefact ID for further use by user.
    if upload_response is not None and upload_response.status_code == 200:
        endpoint = "artefact"
        print(f"Upload Complete -  Validating {art_type} server-side")
        url = urljoin(conf_mgr.runner_url, f"{endpoint}/{art_uuid}")
        patch_req_response = requests.patch(url=url, headers=headers, data={"hashval": hashval})
        if not patch_req_response.ok:
            raise handle_bad_response(patch_req_response, endpoint)
        else:
            print(
                f"Upload validated. This {art_type} can now be used in experiments \
                    by referring to it by UUID: {art_uuid}"
            )
            print(f"Alternatively, you can continue to use the {art_type}'s filepath.")
            return art_uuid
    else:
        print("Upload failed")
        print(dump(upload_response))


# --------------------------------------      iris infer    -------------------------------------- #


@telemetry_decorator
def infer(
    url: str,
    task_name: str,
    use_cpu: bool,
    text: List[str],
    context: Optional[str] = None,
):
    """Infer the hosted tytn model using triton client.

    Args:
        port (int): port number of the triton server
        task_name (str): task name of the model (sequence_classification, question_answering)
        use_cpu (bool): whether to use cpu or not
        text (str): input text field used for inference
        context (Optional[str]): input context field used for inference. Only used in question_answering task.
                                    Defaults to None.
        url (str): The url of the triton server


    Returns:
        infer_res(dict): dictionary of the inference result
    """
    model_name = "transformer_onnx_inference" if use_cpu else "transformer_tensorrt_inference"
    model_version = "1"
    batch_size = 1

    triton_client = tritonclient.http.InferenceServerClient(url=url, verbose=False)

    triton_client.get_model_metadata(model_name=model_name, model_version=model_version)
    triton_client.get_model_config(model_name=model_name, model_version=model_version)
    text_1, text_2 = None, None
    if task_name == "sequence_classification":
        if len(text) == 1:
            # if only one text is provided, this is a single sentence classification task inference
            text_1 = tritonclient.http.InferInput(name="TEXT", shape=(batch_size,), datatype="BYTES")
            text_1.set_data_from_numpy(np.asarray([text[0]] * batch_size, dtype=object))
        elif len(text) == 2:
            # if two texts are provided, this is a pair sentence classification task inference
            text_1 = tritonclient.http.InferInput(name="TEXT_1", shape=(batch_size,), datatype="BYTES")
            text_2 = tritonclient.http.InferInput(name="TEXT_2", shape=(batch_size,), datatype="BYTES")
            text_1.set_data_from_numpy(np.asarray([text[0]] * batch_size, dtype=object))
            text_2.set_data_from_numpy(np.asarray([text[1]] * batch_size, dtype=object))
        else:
            raise ValueError("Invalid number of texts provided for sequence classification task")
    elif task_name == "question_answering":
        if context is None:
            raise ValueError("Context must be provided for question answering task")
        text_1 = tritonclient.http.InferInput(name="QUESTION", shape=(batch_size,), datatype="BYTES")
        text_2 = tritonclient.http.InferInput(name="CONTEXT", shape=(batch_size,), datatype="BYTES")
        text_1.set_data_from_numpy(np.asarray([text[0]] * batch_size, dtype=object))
        text_2.set_data_from_numpy(np.asarray([context] * batch_size, dtype=object))
    else:
        raise ValueError("Invalid task name provided")

    # bind outputs to the server
    outputs = tritonclient.http.InferRequestedOutput(name="outputs", binary_data=False)

    infer_res = triton_client.infer(
        model_name=model_name,
        model_version=model_version,
        inputs=[text_1, text_2] if text_2 is not None else [text_1],
        outputs=[outputs],
    )
    return json.loads(infer_res.as_numpy("outputs").item())


# --------------------------------------     iris makesafe    -------------------------------------- #


def makesafe(
    model: str,
):
    """Convert a model's weights to the safetensors format.

    Args:
        model (str): The path of the local model to be converted.
    """
    if not os.path.exists(model):
        print("Model not found at given location")
        return
    # else
    print("Checking for requirements...")
    failed_packages = list(filter(lambda x: not util.find_spec(x), ["torch", "safetensors", "transformers"]))
    if failed_packages:
        print(
            "To use the safetensors convert, you must have the following packages installed: ",
            failed_packages,
        )
        print("NB: These packages do not need to be installed with gpu support.")
        return
    # else
    from .safe_convert import do_convert

    do_convert(model)
