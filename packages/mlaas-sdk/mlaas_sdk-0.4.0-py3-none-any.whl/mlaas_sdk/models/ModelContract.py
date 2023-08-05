from typing import Union

from pydantic import BaseModel


class ModelContract(BaseModel):
    class ModelParams(BaseModel):
        developer_id: str
        organization_id: str
        train_image_hash: Union[str, None]
        res_hash: Union[str, None]

    class ModelDataParams(BaseModel):
        dataset_id: str

    model_params: ModelParams
    data_params: ModelDataParams
