# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Utilities function for finetuning module """

import torch

from azureml.acft.common_components.utils.logging_utils import get_logger_app


logger = get_logger_app(__name__)


def get_current_device() -> torch.device:
    """Get current cuda device
    :return: current device
    :rtype: torch.device
    """

    # check if GPU is available
    if torch.cuda.is_available():
        try:
            # get the current device index
            device_idx = torch.distributed.get_rank()
        except RuntimeError as ex:
            if 'Default process group has not been initialized'.lower() in str(ex).lower():
                device_idx = 0
            else:
                logger.error(str(ex))
                raise ex
        return torch.device(type="cuda", index=device_idx)
    else:
        return torch.device(type="cpu")
