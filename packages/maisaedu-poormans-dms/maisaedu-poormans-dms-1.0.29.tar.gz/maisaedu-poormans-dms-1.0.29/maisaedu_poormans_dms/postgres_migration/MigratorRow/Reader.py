from maisaedu_utilities_prefect.database.postgres import select
from ..Contracts.MigratorRowReaderInterface import MigratorRowReaderInterface
from dataclasses import dataclass


@dataclass
class MigratorReader(MigratorRowReaderInterface):
    source_conn: object
    target_conn: object
    target_table_name: str
    source_table_name: str
    incremental_column: str
    read_batch_size: int

    def __init__(
        self,
        source_conn: object,
        target_conn: object,
        source_table_name: str,
        target_table_name: str,
        incremental_column: str,
        read_batch_size: int,
    ):
        self.source_conn = source_conn
        self.target_conn = target_conn
        self.source_table_name = source_table_name
        self.target_table_name = target_table_name
        self.incremental_column = incremental_column
        self.read_batch_size = read_batch_size

    def get_source_query_with_incremental_column(self) -> str:
        target_query = (
            f"select max({self.incremental_column}) from {self.target_table_name}"
        )
        result = select(self.target_conn, target_query)

        if result[0][0] is None:
            source_query = f"select * from {self.source_table_name} order by {self.incremental_column}"
        else:
            max_incremental_data = result[0][0]
            if (
                type(max_incremental_data) == "int"
                or type(max_incremental_data) == "float"
            ):
                source_query = f"select * from {self.source_table_name} where {self.incremental_column} > {max_incremental_data} order by {self.incremental_column}"
            else:
                source_query = f"select * from {self.source_table_name} where {self.incremental_column} > '{max_incremental_data}' order by {self.incremental_column}"
        return source_query

    def get_source_query_without_incremental_column(self) -> str:
        source_query = f"select * from {self.source_table_name} order by 1"
        return source_query

    def get_columns_names(self, function_get_source_query: object) -> list:
        source_query = function_get_source_query()
        cursor = self.source_conn.cursor()
        cursor.execute(f"{source_query} limit 1")
        cursor.close()
        columns_names = [desc[0] for desc in cursor.description]
        return columns_names

    def get_source_data(self, function_get_source_query: object, type: str) -> list:
        source_query = function_get_source_query()

        cursor = self.source_conn.cursor()

        index = 0
        offset = 0
        batch_size = self.read_batch_size
        cursor.execute(f"{source_query} offset {offset} limit {batch_size}")
        rows = cursor.fetchall()

        while len(rows) > 0:
            yield rows

            offset += len(rows)
            index += 1
            if (
                type == "incremental" and index >= 20
            ):  # this part reset query when it has more than 20 pages, because when incremental flow is used, it can be very slow
                source_query = function_get_source_query()
                index = 0
                offset = 0

            cursor.execute(f"{source_query} offset {offset} limit {batch_size}")
            rows = cursor.fetchall()

        cursor.close()
