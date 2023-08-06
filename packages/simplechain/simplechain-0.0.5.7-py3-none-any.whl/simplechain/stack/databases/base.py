from abc import abstractmethod, ABC
from typing import List


class Database(ABC):
    @abstractmethod
    def run(self, command: str, fetch: str = "all") -> List:
        pass

    @property
    @abstractmethod
    def table_names(self):
        pass

    @property
    @abstractmethod
    def table_info(self):
        pass

    @property
    @abstractmethod
    def dialect(self):
        pass

    @abstractmethod
    def get_table_columns(self, table_name: str) -> List[str]:
        pass