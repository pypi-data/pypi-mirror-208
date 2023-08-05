from typing import Union

from pydantic import BaseModel


class ModelContractUnverified(BaseModel):
    developer_id: str
    organization_id: str
    hash: Union[str, None]
