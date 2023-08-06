# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MMDetection trainer arguments"""

from typing import Any, Dict

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    SettingParameters,
)

from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlFinetuneInterface,
)
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionDatasetLiterals,
)

logger = get_logger_app(__name__)


class DetectionTrainerArguments(AzmlFinetuneInterface):
    """MM Detection trainer arguments."""
    def __init__(self, params: Dict[str, Any]) -> None:
        """
        :param params: parameters used for training
        :type params: dict
        """
        super().__init__()
        self.params = params

    def get_finetune_args(self) -> Dict[str, Any]:
        """custom args for MM detection tasks (OD and IS)

        :return: dictionary of custom args which are not supported by core
                 and needed for image models
        :rtype: Dict[str, Any]
        """
        custom_args_dict = {
            SettingLiterals.REMOVE_UNUSED_COLUMNS: SettingParameters.REMOVE_UNUSED_COLUMNS,
            SettingLiterals.LABEL_NAMES: [MmDetectionDatasetLiterals.GT_LABELS],
        }
        return custom_args_dict

    def get_custom_trainer_functions(self) -> Dict[str, Any]:
        """Customizable methods for trainer class

        :return: dictionary of custom trainer methods needed for image models
        :rtype: Dict[str, Any]
        """
        return {}
