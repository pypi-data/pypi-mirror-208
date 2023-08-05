from abc import ABC, abstractmethod
from typing import Any, Iterator, Union, Generator, AsyncGenerator, AsyncIterator


class AbstractDataSource(ABC):
    """
    Abstract class for wrapping Generators and Iterators
    """

    def __init__(self):
        self.iterable: Union[Generator, Iterator] = self.initialize()

    @abstractmethod
    def initialize(self) -> Union[Generator, Iterator]:
        """
        Method that creates the generator or iterator used to produce data
        """
        pass

    @abstractmethod
    def teardown(self):
        """
        Clean up method for the wrapper iterator or generator
        """
        pass

    def process_data(self, data: Any) -> Any:
        """
        Method for processing the data source's outputted data

        Args:
            data: Data from the data source

        Returns:
            The processed data
        """
        return data

    def __iter__(self):
        return self

    def __next__(self):
        nxt = next(self.iterable)
        data = self.process_data(nxt)
        return data


class AbstractAsyncDataSource(ABC):
    def __init__(self):
        self.iterable: Union[AsyncGenerator, AsyncIterator] = self.initialize()

    @abstractmethod
    def initialize(self) -> Union[AsyncGenerator, AsyncIterator]:
        """
        Method that creates the generator or iterator used to produce data
        """
        pass

    @abstractmethod
    async def teardown(self):
        """
        Asynchronous clean up method for the iterator/generator
        """
        pass

    async def process_data(self, data: Any) -> Any:
        """
        Method for asynchronously processing the data source's outputted data

        Args:
            data: Data from the data source

        Returns:
            The processed data
        """
        return data

    def __iter__(self):
        return self

    async def __anext__(self):
        nxt = await self.iterable.__anext__()
        data = await self.process_data(nxt)
        return data
