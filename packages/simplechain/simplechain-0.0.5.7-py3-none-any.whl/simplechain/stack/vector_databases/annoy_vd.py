import json
import os
from typing import Tuple, List, Any, Literal, Dict

import numpy as np
from annoy import AnnoyIndex

from simplechain.stack.vector_databases.base import VectorDatabase


def get_index(path_to_file: str, embed_size: int,
              metric: Literal["angular", "euclidean", "manhattan", "hamming", "dot"]) -> AnnoyIndex:
    index = AnnoyIndex(embed_size, metric)
    if os.path.isfile(path_to_file):
        index.load(path_to_file)

    return index


def get_metadata(path_to_metadata_file: str) -> List[Any]:
    # Create metadata file if it doesn't exist
    if not os.path.isfile(path_to_metadata_file):
        # write an empty list to the file
        with open(path_to_metadata_file, "a") as f:
            json.dump([], f)
            f.close()
        return []

    # Load json from file
    metadata = json.loads(open(path_to_metadata_file, 'r').read())
    return metadata


class Annoy(VectorDatabase):
    def __init__(self, embed_size: int, path_to_index_file: str, path_to_metadata_file: str,
                 metric: Literal["angular", "euclidean", "manhattan", "hamming", "dot"] = "angular", n_trees: int = 10):
        """
        Annoy vector database
        :param metric: Distance metric to use
        :param n_trees: Number of trees to use
        """
        super().__init__()
        self.n_trees = n_trees

        self.path_to_index_file = path_to_index_file
        self.index = get_index(path_to_index_file, embed_size, metric)
        self.i = 0

        self.path_to_metadata_file = path_to_metadata_file
        self.metadata = get_metadata(path_to_metadata_file)

    def add(self, embed: List[float], metadata: Any):
        """
        Add an embed and its metadata to the database
        :param embed:
        :param metadata:
        :return:
        """
        self.index.add_item(self.i, embed)
        self.i += 1
        self.metadata.append(metadata)

    def add_all(self, embeds: List[List[float]], metadatas: List[Any]):
        """
        Add a list of embeds and their metadatas to the database
        :param embeds:
        :param metadatas:
        :return:
        """
        for embed, metadata in zip(embeds, metadatas):
            self.add(embed, metadata)

    def save(self):
        """Save the data"""
        # Save the index
        self.index.build(self.n_trees)
        self.index.save(self.path_to_index_file)

        # Save metadata to json
        metadata_json = json.dumps(self.metadata)
        with open(self.path_to_metadata_file, "w") as f:
            f.write(metadata_json)

    def get_nearest_neighbors(self, query_embed: List[float], k: int = 1, include_distances: Literal[True, False] = False) -> Dict:
        """
        Given a query embed, get the k nearest neighbors with their distances
        :param include_distances:
        :param query_embed:
        :param k:
        :return: k nearest neighbors with their distances
        """

        results = {}
        nearest_neighbors = self.index.get_nns_by_vector(query_embed, k, search_k=-1, include_distances=include_distances)
        results["ids"] = nearest_neighbors[0]
        if include_distances:
            results["distances"] = nearest_neighbors[1]
        results["metadata"] = [self.metadata[i] for i in results["ids"]]  # Get metadata for each id

        return results

    def get_item_given_index(self, index: int, include_embeds: bool = True, include_metadata: bool = True) -> Dict:
        """
        Given an index, get the name and embed of the item
        :param index:
        :return:
        """
        results = {}
        if include_embeds:
            results["embed"] = self.index.get_item_vector(index)
        if include_metadata:
            results["metadata"] = self.metadata[index]
        return results

