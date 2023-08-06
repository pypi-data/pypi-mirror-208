from simplechain.pipeline.module import module
from simplechain.stack.search_engines.base import SearchEngine


@module("Search")
def search(query: str, search_engine: SearchEngine):
    """
    Search the web using a search engine.
    :param query:
    :param search_engine:
    :return:
    """
    results = search_engine.search(query)
    return results
