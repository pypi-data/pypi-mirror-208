from .MLaaSException import MLaaSException


class SharingException(MLaaSException):
    """Base exception for Model Sharing client."""

    pass


class ModelException(SharingException):
    """Base exception for ML model instances."""

    pass


class DatasetException(SharingException):
    """Base exception for dataset instances."""

    pass


class ModelNotFoundException(ModelException):
    def __init__(self, id):
        message = "Model was not found in the platform.\n" f"Model UUID: {id}"
        self.id = id
        super().__init__(message)


class DatasetNotFoundException(DatasetException):
    def __init__(self, id):
        message = "Dataset was not found in the platform.\n" f"Dataset UUID: {id}"
        self.id = id
        super().__init__(message)


class ModelRegistrationException(ModelException):
    def __init__(self):
        message = "Exception occurred when trying to register model."
        super().__init__(message)


class DatasetRegistrationException(DatasetException):
    def __init__(self):
        message = "Exception occurred when trying to register dataset."
        super().__init__(message)


class ModelUpdateException(ModelException):
    def __init__(self, id):
        message = (
            "Exception occurred when trying to update model with training results.\n"
            f"Model UUID: {id}"
        )
        self.id = id
        super().__init__(message)
