"""
The implementation of YourNewModel for the partially-observed time-series imputation task.

Refer to the paper "Your paper citation".

"""

# Created by Your Name <Your contact email> TODO: modify the author information.
# License: GLP-v3

from typing import Union, Optional

import numpy as np
import torch
import torch.nn as nn

# TODO: import the base class from the imputation package in PyPOTS.
#  Here I suppose this is a neural-network imputation model.
#  You should make your model inherent BaseImputer if it is not a NN.
# from pypots.imputation.base import BaseImputer
from pypots.imputation.base import BaseNNImputer

from pypots.optim.adam import Adam
from pypots.optim.base import Optimizer


# TODO: define your new model here.
#  It could be a neural network model or a non-neural network algorithm (e.g. written in numpy).
#  Your model should be implemented with PyTorch and subclass torch.nn.Module if it is a neural network.
#  Note that your main algorithm is defined in this class, and this class usually won't be exposed to users.
class _YourNewModel(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, inputs: dict) -> dict:
        # TODO: define your model's forward propagation process here.
        #  The input is a dict, and the output `results` should also be a dict.
        #  `results` must contains the key `loss` which is will be used for backward propagation to update the model.

        loss = None
        results = {
            "loss": loss,
        }
        return results


# TODO: define your new model's wrapper here.
#  It should be a subclass of a base class defined in PyPOTS task packages (e.g.
#  BaseNNImputer of PyPOTS imputation task package), and it has to implement all abstract methods of the base class.
#  Note that this class is a wrapper of your new model and will be directly exposed to users.
class YourNewModel(BaseNNImputer):
    def __init__(
        self,
        # TODO: add your model's hyper-parameters here
        batch_size: int,
        epochs: int,
        patience: int,
        num_workers: int = 0,
        optimizer: Optional[Optimizer] = Adam(),
        device: Optional[Union[str, torch.device]] = None,
        saving_path: str = None,
        model_saving_strategy: Optional[str] = "best",
    ):
        super().__init__(
            batch_size,
            epochs,
            patience,
            num_workers,
            device,
            saving_path,
            model_saving_strategy,
        )
        # set up the hyper-parameters
        # TODO: set up your model's hyper-parameters here

        # set up the model
        self.model = _YourNewModel()
        self.model = self.model.to(self.device)
        self._print_model_size()

        # set up the optimizer
        self.optimizer = optimizer
        self.optimizer.init_optimizer(self.model.parameters())

    def _assemble_input_for_training(self, data: list) -> dict:
        raise NotImplementedError

    def _assemble_input_for_validating(self, data: list) -> dict:
        raise NotImplementedError

    def _assemble_input_for_testing(self, data: list) -> dict:
        raise NotImplementedError

    def fit(
        self,
        train_set: Union[dict, str],
        val_set: Optional[Union[dict, str]] = None,
        file_type: str = "h5py",
    ) -> None:
        raise NotImplementedError

    def impute(self, X: Union[dict, str], file_type: str = "h5py") -> np.ndarray:
        raise NotImplementedError
