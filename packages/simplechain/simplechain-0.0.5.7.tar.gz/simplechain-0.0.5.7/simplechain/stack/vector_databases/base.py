from abc import ABC, abstractmethod
from typing import Tuple, List, Any, Dict

import numpy as np


class VectorDatabase(ABC):
    @abstractmethod
    def add(self, embed: List[float], metadata: Any):
        """
        Add a name and its embed to the database
        :param metadata:
        :param embed:
        :return:
        """
        pass

    @abstractmethod
    def add_all(self, embeds: List[List[float]], metadatas: List[Any]):
        """
        Add a list of names and their embeds to the database
        :param metadatas:
        :param embeds:
        :return:
        """
        pass

    @abstractmethod
    def save(self):
        """
        Build the database
        :return:
        """
        pass

    @abstractmethod
    def get_nearest_neighbors(self, query_embed: List[float], k: int = 1, include_distances: bool = False) -> Dict:
        """
        Given a query embed, get the k nearest neighbors with their distances
        :param query_embed:
        :param k:
        :return: a list of k nearest neighbours with their payloads and distances
        """
        pass

    @abstractmethod
    def get_item_given_index(self, index: int, include_embeds: bool = True, include_metadata: bool = True) -> Dict:
        """
        Given an index, get the name and embed of the item
        :param include_metadata:
        :param include_embeds:
        :param return_embed:
        :param index:
        :return:
        """
        pass
