from .base import BaseClient
from ..exceptions.training import *

import requests


class TrainingClient(BaseClient):
    def __init__(self, training_endpoint: str, secure: bool = False):
        super().__init__(training_endpoint, secure)

    def train_model(self, model_id) -> None:
        try:
            requests.post(self.build_url("train", model_id), stream=True)
        except requests.exceptions.RequestException as e:
            raise TrainingSchedulingException(model_id)
