import ovito.io
from ..data import DataCollection
import abc
import traits.api
from typing import Any

class FileReaderInterface(traits.api.HasStrictTraits):

    # Method that must be implemented by all sub-classes:
    @abc.abstractmethod
    def parse(self, data: DataCollection, **kwargs: Any) -> None:
        raise NotImplementedError

    # Optional methods that may be implemented by sub-classes:
    #
    #if TYPE_CHECKING:
    #    def detect(self, filename: str) -> bool:
    #        ...
    #    def scan(self, filename: str, register_frame: Callable[..., None]) -> None:
    #        ...

ovito.io.FileReaderInterface = FileReaderInterface
