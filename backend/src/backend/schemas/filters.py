from abc import ABC, abstractmethod

from sqlalchemy import Select


class BaseFilter(ABC):

    @abstractmethod
    def filter(self, stmt: Select) -> Select:
        pass
