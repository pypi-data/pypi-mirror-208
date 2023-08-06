from simplechain.pipeline.module import module


@module("SQL Template")
def sql_template(question: str, dialect: str, table_info: str, top_k=10) -> str:
    """SQL template for prompt templates."""
    _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer. Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
    Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Use the following format:
    Question: "Question here"
    SQLQuery: "SQL Query to run"
    SQLResult: "Result of the SQLQuery"
    Answer: "Final answer here"
    Only use the tables listed below.
    {table_info}
    Question: {question}"""
    return _DEFAULT_TEMPLATE.format(dialect=dialect, top_k=top_k, table_info=table_info, question=question)


@module("SQL Table Decider Template")
def sql_table_decider_template(question: str, table_names: List[str]) -> str:
    """SQL table decider template for prompt templates."""
    _DECIDER_TEMPLATE = """Given the below input question and list of potential tables, output a comma separated list of the table names that may be necessary to answer this question.
    Question: {question}
    Table Names: {table_names}
    Relevant Table Names:"""

    return _DECIDER_TEMPLATE.format(question=question, table_names=", ".join(table_names))

