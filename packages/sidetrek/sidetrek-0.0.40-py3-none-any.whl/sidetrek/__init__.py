from sidetrek.loggers import logger
from sidetrek.global_fns import *


__all__ = ["dataset", "types", "flyte"]


__doc__ = """
sidetrek
================

Description
-----------
sidetrek is the official Python package that exposes both cli and python sdk

SDK Example
-------
>>> # Import library
>>> from sidetrek import logger
>>> logger.<any mlflow method>

>>> from sidetrek import get_project_dir
>>> project_dir = get_project_dir("owner/repo")

CLI Example
-------
>>> sidetrek workflow run --workflow-id 10 and --version 0.0.1 --workflow-args '{learning_rate=0.1, epochs=5}'

"""
