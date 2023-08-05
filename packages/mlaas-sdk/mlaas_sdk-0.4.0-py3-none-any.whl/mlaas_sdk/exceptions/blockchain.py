from .MLaaSException import MLaaSException


class BlockchainException(MLaaSException):
    """Base exception for Blockchain client."""

    pass


class ContractException(BlockchainException):
    """Base exception for smart contract interactions."""

    pass


class ContractNotFoundException(ContractException):
    def __init__(self, address):
        message = (
            "Smart contract was not found in the blockchain instance.\n"
            f"Contract address: {address}"
        )
        self.address = address
        super().__init__(message)


class ContractVerificationException(ContractException):
    def __init__(self, address):
        message = (
            "Exception occurred when trying to veify the smart contract (may have already been verified).\n"
            f"Contract address: {address}"
        )
        self.address = address
        super().__init__(message)


class ContractDeploymentException(ContractException):
    def __init__(self, payload):
        message = (
            "Exception occurred when trying to deploy smart contract.\n"
            f"Contract payload: {payload}"
        )
        self.payload = payload
        super().__init__(message)
