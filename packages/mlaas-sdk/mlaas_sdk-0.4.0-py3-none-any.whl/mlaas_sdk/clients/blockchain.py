from typing import Union

from .base import BaseClient
from ..exceptions.blockchain import *
from ..models import DatasetContract, ModelContract, ModelContractUnverified

import requests


class BlockchainClient(BaseClient):
    def __init__(self, blockchain_endpoint: str, secure: bool = False):
        super().__init__(blockchain_endpoint, secure)

    def read_contract(
        self, contract_address: str
    ) -> Union[DatasetContract, ModelContract, ModelContractUnverified]:
        try:
            res = requests.get(self.build_url("contract", contract_address)).content
            try:
                return DatasetContract.parse_raw(res)
            except ValueError:
                pass
            try:
                return ModelContract.parse_raw(res)
            except ValueError:
                pass
            try:
                return ModelContractUnverified.parse_raw(res)
            except ValueError:
                raise ContractNotFoundException(contract_address)
        except requests.exceptions.RequestException as e:
            raise ContractNotFoundException(contract_address)

    def verify_contract(self, contract_address: str, res_hash: str) -> None:
        try:
            requests.post(
                self.build_url("contract", contract_address, "verify"),
                params={"res_hash": res_hash},
            )
        except requests.exceptions.RequestException as e:
            raise ContractVerificationException(contract_address)

    def deploy_contract(
        self, payload: Union[DatasetContract, ModelContract, ModelContractUnverified]
    ) -> str:
        try:
            return requests.post(
                self.build_url("contract"),
                json=payload.dict(exclude_none=True),
            ).json()["contract_address"]
        except requests.exceptions.RequestException as e:
            raise ContractDeploymentException(payload)
