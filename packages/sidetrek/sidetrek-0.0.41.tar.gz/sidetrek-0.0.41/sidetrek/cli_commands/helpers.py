import json
import time
import threading
from pathlib import Path
import shutil
import urllib.parse
import io
from zipfile import ZipFile
import typer
from rich import print
import requests
from cli_commands.constants import NODE_ENV, APP_NAME, GENERATED_LOCAL_SIDETREK_DIRNAME, GENERATED_PROJECT_DIRNAME


def print_timer(seconds: int = 1):
    start_time = time.time()

    def loop():
        while True:
            time.sleep(seconds)
            current_time = time.time()
            elapsed_time = current_time - start_time
            print(f"\r{elapsed_time} seconds...")

    threading.Thread(target=loop).start()


def get_auth_api_base_url():
    return f"http://localhost:4002/api/v1" if NODE_ENV == "development" else f"https://auth.sidetrek.com/api/v1"


def get_user_machine_node_api_base_url(user_id):
    return f"http://localhost:4008/p/api/v1" if NODE_ENV == "development" else f"https://user-machines.sidetrek.com/{user_id}/node/p/api/v1"


def get_webapp_api_base_url():
    return f"http://localhost:4001/p/app/api/v1" if NODE_ENV == "development" else f"https://app.sidetrek.com/p/app/api/v1"


def get_generated_local_sidetrek_dir_path() -> Path:
    app_dir = typer.get_app_dir(APP_NAME)
    generated_local_sidetrek_dir_path = Path(app_dir) / GENERATED_LOCAL_SIDETREK_DIRNAME
    Path(generated_local_sidetrek_dir_path).mkdir(parents=True, exist_ok=True)
    return generated_local_sidetrek_dir_path


def get_generated_project_dir_path() -> Path:
    generated_local_sidetrek_dir_path = get_generated_local_sidetrek_dir_path()
    generated_project_dir_path = Path(generated_local_sidetrek_dir_path) / GENERATED_PROJECT_DIRNAME
    Path(generated_project_dir_path).mkdir(parents=True, exist_ok=True)
    return generated_project_dir_path


def get_generated_workflow_dir_path(workflow_id: int, workflow_version_id: int) -> Path:
    generated_project_dir_path = get_generated_project_dir_path()
    generated_wf_dir_path = Path(generated_project_dir_path) / f"wf_{workflow_id}_{workflow_version_id}"
    Path(generated_wf_dir_path).mkdir(parents=True, exist_ok=True)
    return generated_wf_dir_path


def get_generated_workflow_name(workflow_id: str) -> str:
    """
    This is the name of the workflow function (i.e. fn def under @workflow)
    """
    return f"wf_{workflow_id}"


def get_workflow_file_path(workflow_id: int, workflow_version_id: int) -> Path:
    generated_wf_dir_path = get_generated_workflow_dir_path(workflow_id, workflow_version_id)
    return Path(f"{generated_wf_dir_path}/wf_{workflow_id}.py")


def raise_fail_to_authenticate():
    print("[red]Failed to authenticate.[/red]")
    print("Please login first - run: '[blue]sidetrek login[/blue]'\n")
    raise typer.Exit()


def get_credentials() -> dict | None:
    """
    Get credentials from the saved file (from login)

    If credentials don't exist, raise an except with error message asking to login first
    """
    app_dir = typer.get_app_dir(APP_NAME)
    creds_path: Path = Path(app_dir) / ".credentials"

    creds_exists = Path(creds_path).is_file()

    if not creds_exists:
        raise_fail_to_authenticate()

    with open(creds_path, "r") as f:
        creds = json.load(f)
        return creds


def get_credentials_header_str() -> str:
    creds = get_credentials()
    creds_header_str = "; ".join([str(x) + "=" + str(y) for x, y in creds.items()])
    return creds_header_str


def get_token() -> str:
    try:
        creds_header_str = get_credentials_header_str()
        auth_api_base_url = get_auth_api_base_url()
        refresh_session_res = requests.get(f"{auth_api_base_url}/auth/refresh-session", headers={"Cookie": creds_header_str})
        refresh_session = refresh_session_res.json()
        id_token = refresh_session["idToken"]
        return id_token
    except requests.exceptions.HTTPError as errh:
        print(f"{errh.response.status_code} {errh.response.text}")
        raise typer.Exit()
    except requests.exceptions.RequestException as err:
        print("Something went wrong: ", err)
        raise typer.Exit()


def get_headers() -> dict:
    token = get_token()
    return {"content-type": "application/json", "authorization": f"Bearer {token}"}


def get_current_user() -> dict | None:
    try:
        # Retrieve the currently authenticated user from Cognito by using saved refresh token
        creds_header_str = get_credentials_header_str()
        auth_api_base_url = get_auth_api_base_url()
        auth_user_res = requests.get(f"{auth_api_base_url}/auth/current-user", headers={"Cookie": creds_header_str})
        auth_user_res.raise_for_status()
        auth_user = auth_user_res.json()

        # Retrieve user from webapp db
        webapp_api_base_url = get_webapp_api_base_url()
        current_user_res = requests.get(f"{webapp_api_base_url}/users", params={"email": auth_user["email"]}, headers=get_headers())
        current_user = current_user_res.json()
        return current_user["data"]
    except requests.exceptions.HTTPError as errh:
        print(f"{errh.response.status_code} {errh.response.text}")
        raise typer.Exit()
    except requests.exceptions.RequestException as err:
        print("Something went wrong: ", err)
        raise typer.Exit()


def get_workflow_draft_version(workflow_id: int) -> dict | None:
    try:
        webapp_api_base_url = get_webapp_api_base_url()
        include = {"organization": True, "project": True, "domain": True, "workflow": True}
        include_json_str = json.dumps(include)
        workflow_version_res = requests.get(f"{webapp_api_base_url}/workflow-versions?isDraft=true&workflowId={workflow_id}&include={include_json_str}", headers=get_headers())
        workflow_version_res.raise_for_status()
        workflow_version = workflow_version_res.json()
        return workflow_version["data"]
    except requests.exceptions.HTTPError as errh:
        print(f"{errh.response.status_code} {errh.response.text}")
        raise typer.Exit()
    except requests.exceptions.RequestException as err:
        print("Something went wrong: ", err)
        raise typer.Exit()


def download_generated_flyte_workflow(user_id: str, workflow_version: dict) -> Path:
    """
    Gets the generated flyte workflow from pycodegen in the user machine and download it to a local dir

    Returns the path to the generated wf file
    """
    # First generate the flyte workflow in user machine and save it
    workflow = workflow_version["workflow"]
    generate_flyte_workflow(user_id, workflow_version)

    # Download the generated wf dir as a zip and unzip it to a local generated project dir
    try:
        user_machine_api_base_url = get_user_machine_node_api_base_url(user_id)
        encoded_repo_full_name = urllib.parse.quote(workflow["repoFullName"], safe="")
        repo_res = requests.get(f"{user_machine_api_base_url}/repos/download/{encoded_repo_full_name}", headers=get_headers())
        repo_res.raise_for_status()
        zip_file = ZipFile(io.BytesIO(repo_res.content))

        # First delete the generated project dir to reset...
        shutil.rmtree(get_generated_project_dir_path())

        # ...and then recreate the project dir and then unzip
        generated_project_dir_path = get_generated_project_dir_path()
        unzip_path = generated_project_dir_path
        zip_file.extractall(unzip_path)

        # Return the generated wf file path
        generated_wf_file_path = get_workflow_file_path(workflow["id"], workflow_version["id"])
        return generated_wf_file_path
    except requests.exceptions.HTTPError as errh:
        print(f"{errh.response.status_code} {errh.response.text}")
        raise typer.Exit()
    except requests.exceptions.RequestException as err:
        print("Something went wrong: ", err)
        raise typer.Exit()


def generate_flyte_workflow(user_id: str, workflow_version: dict) -> None:
    workflow = workflow_version["workflow"]
    ui_obj = json.loads(workflow_version["ui"])

    payload = json.dumps(
        {
            "organizationId": workflow_version["organizationId"],
            "projectId": workflow_version["projectId"],
            "workflow": {
                "id": workflow["id"],
                "versionId": workflow_version["id"],
                "repoFullName": workflow["repoFullName"],
                # "decoratorArgs": ""
            },
            "nodes": ui_obj["nodes"],
            "edges": ui_obj["edges"],
            # "mlflow": {
            #     "experiment_id": "",
            #     "tags": "",
            # }
        }
    )

    try:
        user_machine_api_base_url = get_user_machine_node_api_base_url(user_id)
        flyte_workflow_file_res = requests.post(f"{user_machine_api_base_url}/python/flyte-workflow-file/save", data=payload, headers=get_headers())
        flyte_workflow_file_res.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(f"{errh.response.status_code} {errh.response.text}")
        raise typer.Exit()
    except requests.exceptions.RequestException as err:
        print("Something went wrong: ", err)
        raise typer.Exit()


def parse_pylint_errors(pylint_res: str, error_code: str):
    # Split into lines and filter out headers, footers, etc
    lines = [line for line in pylint_res.split("\n") if ".py" in line]
    print(f"lines={lines}")
    error_code_to_filter = error_code if error_code else "E"
    print(f"error_code_to_filter={error_code_to_filter}")
    # Ignore "E0401", which are import errors since this relates to relative paths :(
    errors = [{"code": line.split(": ")[1], "target": line.split("'")[1]} for line in lines if error_code_to_filter in line["code"] and line["code"] != "E0401"]
    return errors


def prepend_missing_imports(code: str, missing_imports: list[str]):
    if not missing_imports:
        return

    modules_to_add = [f"import {module_name}\n" for module_name in missing_imports]
    return "".join(modules_to_add) + code
