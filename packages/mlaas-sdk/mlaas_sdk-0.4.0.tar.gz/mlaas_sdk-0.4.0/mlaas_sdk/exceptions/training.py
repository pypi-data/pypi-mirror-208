from .MLaaSException import MLaaSException


class TrainingException(MLaaSException):
    """Base exception Model Training client."""


class TrainingSchedulingException(TrainingException):
    def __init__(self, id):
        message = (
            "Exception occurred when trying to schedule the model training job.\n"
            f"Model UUID: {id}"
        )
        self.id = id
        super().__init__(message)


class TrainingNotFoundException(TrainingException):
    def __init__(self, id):
        message = (
            "A model training job for the model was not found in the platform.\n"
            f"Model UUID: {id}"
        )
        self.id = id
        super().__init__(message)
