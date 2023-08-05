from .base import BaseClient
from ..exceptions.sharing import *
from ..models import DatasetContract, ModelContract, ModelContractUnverified

import requests


class SharingClient(BaseClient):
    def __init__(self, sharing_endpoint: str, secure: bool = False):
        super().__init__(sharing_endpoint, secure)

    def get_model(self, model_id: str) -> requests.Response:
        try:
            return requests.get(self.build_url("model", model_id), stream=True)
        except requests.exceptions.RequestException as e:
            raise ModelNotFoundException(model_id)

    def get_dataset(self, dataset_id: str) -> requests.Response:
        try:
            return requests.get(self.build_url("dataset", dataset_id), stream=True)
        except requests.exceptions.RequestException as e:
            raise DatasetNotFoundException(dataset_id)

    def get_model_metadata(self, model_id: str) -> ModelContract:
        try:
            return ModelContract.parse_raw(
                requests.get(self.build_url("model", model_id, "metadata")).content
            )
        except requests.exceptions.RequestException as e:
            raise ModelException(model_id)

    def add_model(self, model: ModelContract) -> str:
        try:
            return requests.post(
                self.build_url("model"),
                json=model.dict(exclude_none=True),
            ).json()["model_id"]
        except requests.exceptions.RequestException as e:
            raise ModelRegistrationException()

    def add_model_unverified(self, model: ModelContractUnverified) -> str:
        try:
            return requests.post(
                self.build_url("model", "unverified"),
                json=model.dict(exclude_none=True),
            ).json()["model_id"]
        except requests.exceptions.RequestException as e:
            raise ModelRegistrationException()

    def add_dataset(self, dataset: DatasetContract) -> str:
        try:
            return requests.post(
                self.build_url("dataset"),
                json=dataset.dict(exclude_none=True),
            ).json()["dataset_id"]
        except requests.exceptions.RequestException as e:
            raise DatasetRegistrationException()

    def update_model(self, model_id: str, model: str) -> None:
        try:
            requests.put(
                self.build_url("model", model_id),
                files={
                    "model": (model.split("/")[-1], open(model, "rb")),
                },
            )
        except requests.exceptions.RequestException as e:
            raise ModelUpdateException(model_id)
