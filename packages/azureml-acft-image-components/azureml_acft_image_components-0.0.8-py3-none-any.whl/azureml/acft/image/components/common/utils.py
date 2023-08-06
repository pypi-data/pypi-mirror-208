# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Common utils."""

from azureml.core import Workspace
from azureml.core.run import Run


def get_workspace() -> Workspace:
    """Get current workspace either from Run or Config.

    :return: Current workspace
    :rtype: Workspace
    """
    try:
        ws = Run.get_context().experiment.workspace
        return ws
    except Exception:
        return Workspace.from_config()
