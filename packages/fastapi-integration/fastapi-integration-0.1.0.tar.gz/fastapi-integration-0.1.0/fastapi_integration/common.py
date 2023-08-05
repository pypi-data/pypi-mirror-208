from pydantic.main import BaseModel


class Status(BaseModel):
    """
    Represents the status information.

    Attributes:
        message: The message associated with the status.
        status: The status code or description.
    """
    message: str
    status: str
