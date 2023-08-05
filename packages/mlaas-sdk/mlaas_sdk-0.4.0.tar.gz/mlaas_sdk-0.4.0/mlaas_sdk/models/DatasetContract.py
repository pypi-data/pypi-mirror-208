from typing import Union

from pydantic import BaseModel


class DatasetContract(BaseModel):
    organization_id: str
    samples_dimension: str
    size_bytes: Union[int, None]
    hash: Union[str, None]
