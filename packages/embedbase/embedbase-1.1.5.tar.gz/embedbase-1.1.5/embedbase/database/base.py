from abc import ABC, abstractmethod
from typing import Coroutine, List, Optional, Union
from pandas import DataFrame
from pydantic import BaseModel


# TODO use pydantic validation
class Dataset(BaseModel):
    dataset_id: str
    documents_count: int


class SearchResponse(BaseModel):
    score: float
    id: str
    # data-privacy aware setup avoid storing data on the database
    # and rather store it on the client side
    data: Optional[str]
    hash: str
    # HACK supabase pgvector returns a string of float '[0.1, 0.2, ...]' not sure its
    # any inconvenience for now. Let's see if we can fix this later
    embedding: Union[List[float], str]
    metadata: Optional[dict]


class SelectResponse(BaseModel):
    id: str
    # data-privacy aware setup avoid storing data on the database
    # and rather store it on the client side
    data: Optional[str]
    hash: str
    embedding: Union[List[float], str]
    metadata: Optional[dict]


class VectorDatabase(ABC):
    """
    Base class for all vector databases
    """

    def __init__(self, dimensions: int = 1536):
        self._dimensions = dimensions

    @abstractmethod
    async def select(
        self,
        ids: List[str] = [],
        hashes: List[str] = [],
        dataset_id: Optional[str] = None,
        user_id: Optional[str] = None,
        distinct: bool = True,
    ) -> List[SelectResponse]:
        """
        :param ids: list of ids
        :param hashes: list of hashes
        :param dataset_id: dataset id
        :param user_id: user id
        :param distinct: distinct
        :return: list of documents
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        df: DataFrame,
        dataset_id: str,
        user_id: Optional[str] = None,
        batch_size: Optional[int] = 100,
        store_data: bool = True,
    ) -> Coroutine:
        """
        :param df: dataframe
        :param dataset_id: dataset id
        :param user_id: user id
        :param batch_size: batch size
        :param store_data: store data in database?
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self, ids: List[str], dataset_id: str, user_id: Optional[str] = None
    ) -> None:
        """
        :param ids: list of ids
        :param dataset_id: dataset id
        :param user_id: user id
        """
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        vector: List[float],
        top_k: Optional[int],
        dataset_ids: List[str],
        user_id: Optional[str] = None,
        where: Optional[Union[dict, List[dict]]] = None,
    ) -> List[SearchResponse]:
        """
        :param vector: vector the similarity is calculated against
        :param top_k: top k number of results returned
        :param dataset_id: dataset id
        :param user_id: user id
        :param where: where condition to filter results
        :return: list of documents
        """
        raise NotImplementedError

    @abstractmethod
    async def clear(self, dataset_id: str, user_id: Optional[str] = None) -> None:
        """
        :param dataset_id: dataset id
        :param user_id: user id
        """
        raise NotImplementedError

    @abstractmethod
    async def get_datasets(self, user_id: Optional[str] = None) -> List[Dataset]:
        """
        :param user_id: user id
        :return: list of datasets
        """
        raise NotImplementedError
