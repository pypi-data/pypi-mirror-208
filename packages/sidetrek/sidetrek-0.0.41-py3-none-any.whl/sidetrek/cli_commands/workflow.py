import sys
import time
import threading
from pathlib import Path
import typer
import subprocess
from time import sleep
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from cli_commands.helpers import (
    get_current_user,
    get_generated_local_sidetrek_dir_path,
    get_generated_workflow_name,
    download_generated_flyte_workflow,
    get_workflow_draft_version,
    print_timer,
)

app = typer.Typer()


@app.command()
def run(workflow_id: int = typer.Option(...), workflow_args: str = "{}"):
    """
    Execute the workflow locally (e.g. for testing).

    You can retrieve the --workflow-id (e.g. 42) from Sidetrek app.
    --workflow-args is a stringified JSON of your workflow arguments (e.g. '{"learning_rate"=0.1, "epochs"=5}').
    """

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        print("generated_local_sidetrek_dir_path", get_generated_local_sidetrek_dir_path())
        
        # # Add a timer
        # print_timer()
        
        # Get current user
        auth_step = progress.add_task(description="Authenticating...", total=None)
        current_user = get_current_user()
        progress.remove_task(auth_step)
        print(f"[green]✔️ [white]Authenticated")

        # Always use the draft version for testing
        wf_generation_step = progress.add_task(description="Generating the workflow...", total=None)
        workflow_version = get_workflow_draft_version(workflow_id=workflow_id)
        # print(f"workflow_version={workflow_version}")

        # Generate the workflow file
        wf_file_path = download_generated_flyte_workflow(user_id=current_user["id"], workflow_version=workflow_version)
        generated_wf_name = get_generated_workflow_name(workflow_id)
        progress.remove_task(wf_generation_step)
        print(f"[green]✔️ [white]Workflow generated")

        wf_execution_step = progress.add_task(description="Executing the workflow...", total=None)
        with subprocess.Popen(
            # ["pyflyte", "--pkgs", "project", "package", "--output", "flyte-workflow-package.tgz", "--image", "gcr.io/sidetrek/tylo-birch1-development/wf-22:0.0.39", "--force"],
            ["pyflyte", "run", wf_file_path, generated_wf_name, "--_wf_args", workflow_args],
            cwd=get_generated_local_sidetrek_dir_path(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            output, error = process.communicate()
            
            if process.returncode != 0: 
                print(f"[light_coral]{error.decode('utf-8')}")
                print(f"[red]✕ [white]Workflow execution failed")
                raise typer.Exit()
            
            print(f"[green]{output.decode('utf-8')}")
            
            progress.remove_task(wf_execution_step)
            print(f"[green]✔️ [white]Workflow execution completed 🎉")
            # while process.poll() == None:
            #     print(f"{process.stdout.read1().decode('utf-8')}")

