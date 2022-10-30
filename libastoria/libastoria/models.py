from typing import List, TypeVar

from pydantic import BaseModel


class DataModel(BaseModel):
    pass


class DisksDomain(DataModel):

    disks: List[str] = ["bees"]

class ProcessDomain(DataModel):

    running: bool = False


class LogMessage(DataModel):

    message: str = "yeet"


DataT = TypeVar('DataT', bound=DataModel)
