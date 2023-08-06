from simplechain.pipeline.module import module
from simplechain.stack import TextGenerator
from simplechain.stack.databases.base import Database


@module("Database Query")
def query_database(command: str, database: Database):
    """Execute a SQL command and return a string representing the results.
    If the statement returns rows, a string of the results is returned.
    If the statement returns no rows, an empty string is returned.
    """
    results = database.run(command, fetch="all")
    return results


