import os
from pathlib import Path
from sidetrek.constants import USER_REPO_DATA_DIRNAME


def get_project_dir(repo_full_name: str) -> str:
    """
    Look for __project_root__.py inside repo dir to get the project dir
    - `__project_root__.py` is created inside generated repo during wf version deployment to denote project root dir

    Defaults to local repo path
    - WHY? `__project_root__.py` is only created after deploy, so if it doesn't exist, default to local repo path to avoid syntax error in wf graph

    """
    local_repo_path = "/" + ("workspace" / "source" / "project" / wf_id_id).as_posix()
    files = [str(p) for p in list(Path(local_repo_path).glob("**/__project_root__.py"))]
    print(f"files in get_project_dir={files}")
    if len(files) > 0:
        return files[0].replace("/__project_root__.py", "")
    else:
        return local_repo_path
