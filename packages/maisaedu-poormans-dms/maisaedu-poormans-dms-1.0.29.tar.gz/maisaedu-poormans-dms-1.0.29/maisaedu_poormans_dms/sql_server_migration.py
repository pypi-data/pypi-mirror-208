import pymssql
import psycopg2
import datetime

from maisaedu_utilities_prefect import get_dsn
from maisaedu_utilities_prefect.utils import build_prefect_logger

# https://www.sqlines.com/sql-server-to-postgresql


def data_type_treatment(value):
    if value is None:
        v = "null"
    elif type(value) is str:
        value = value.replace("'", "''")
        v = f"'{value}'"
    elif type(value) is datetime.datetime:
        v = f"'{str(value)}'"
    elif type(value) is datetime.date:
        v = f"'{str(value)}'"
    elif type(value) is bytes:
        v = str(psycopg2.Binary(value))
    else:
        v = str(value)
    return v


def build_columns_query(table_info, ignored_columns=[]):
    type_map = {
        "varbinary": "bytea",
        "image": "bytea",
        "datetime": "timestamp",
        "bit": "boolean",
        "nvarchar": "varchar",
        "tinyint": "smallint",
        "char": "varchar",
    }

    columns_to_select = list()
    columns_and_type = list()
    columns_pk = list()

    for i, column_info in enumerate(table_info):
        col = column_info["COLUMN_NAME"].lower().replace(" ", "")
        column = '"' + column_info["COLUMN_NAME"] + '"'

        # includes the columns without informing if it is PK
        columns_and_type.append(
            f'"{col}" {type_map.get(column_info["DATA_TYPE"],column_info["DATA_TYPE"])}'
        )

        # if it's PK include it in the PK list
        if column_info["pk"]:
            columns_pk.append(f'"{col}"')

        # if it's a ignored column treat it as null
        for ignored_column in ignored_columns:
            if col == ignored_column:
                column = "null as " + column
        columns_to_select.append(f"{column}")

    cols = ", ".join(columns_and_type)
    cols_pk = ", ".join(columns_pk)
    cols_to_select = ", ".join(columns_to_select)

    return cols, cols_pk, cols_to_select, columns_pk


def build_create_query(table, cols, cols_pk):
    if len(cols_pk) > 0:
        return f"CREATE TABLE IF NOT EXISTS {table}({cols}, PRIMARY KEY ({cols_pk}))"
    else:
        return f"CREATE TABLE IF NOT EXISTS {table}({cols})"


def get_table_info_query(origin_table):
    return f"""
            SELECT COLUMN_NAME, DATA_TYPE , CHARACTER_MAXIMUM_LENGTH, pk.col as pk
            FROM INFORMATION_SCHEMA.COLUMNS c
            left join
            (
                select col.[name] as col
                from sys.tables tab
                inner join sys.indexes pk
                    on tab.object_id = pk.object_id and pk.is_primary_key = 1
                inner join sys.index_columns ic
                    on ic.object_id = pk.object_id and ic.index_id = pk.index_id
                inner join sys.columns col
                    on pk.object_id = col.object_id and col.column_id = ic.column_id
                where tab.[name] = '{origin_table}'
            ) pk on pk.col = c.COLUMN_NAME
            WHERE TABLE_NAME = '{origin_table}'
            ORDER BY
                c.ordinal_position

            """


def insert_query_statement(
    dw_cursor, dest_table, data_values, on_conflict, total_inserted_rows, batch
):
    insert_statement = f'insert into {dest_table} values {",".join(data_values)}'
    dw_cursor.execute(f"{insert_statement} {on_conflict}")
    total_inserted_rows += len(batch)
    return total_inserted_rows


def iterate_rows(
    batch,
    dest_table,
    dw_cursor,
    update_column,
    columns_pk,
    position_pks,
    total_inserted_rows,
    insert_type,
    on_conflict,
    show_incremental_logs,
):
    columns = batch[0].keys()

    data_values = []
    data_values_pk = []
    for i, row in enumerate(batch):
        values = []
        values_pk = []
        for column in columns:
            value = row[column]
            values.append(data_type_treatment(value))
            for column_pk in columns_pk:
                if column.lower() == column_pk.lower().replace('"', ""):
                    values_pk.append(data_type_treatment(value))
        data_values.append(f'({",".join(values)})')
        data_values_pk.append(f'({",".join(values_pk)})')

    if update_column and insert_type == "incremental":
        if len(position_pks) >= 1:
            column_name = f'({",".join(columns_pk)})'
            column_value = f'({",".join(data_values_pk)})'
            delete_statement = (
                f"delete from {dest_table} where {column_name} in {column_value}"
            )
            dw_cursor.execute(delete_statement)
            total_inserted_rows = insert_query_statement(
                dw_cursor,
                dest_table,
                data_values,
                on_conflict,
                total_inserted_rows,
                batch,
            )
        else:
            total_inserted_rows = insert_query_statement(
                dw_cursor,
                dest_table,
                data_values,
                on_conflict,
                total_inserted_rows,
                batch,
            )
    else:
        total_inserted_rows = insert_query_statement(
            dw_cursor, dest_table, data_values, on_conflict, total_inserted_rows, batch
        )
        if show_incremental_logs:
            build_prefect_logger().info(total_inserted_rows)
    return total_inserted_rows


def iterate_batches(
    batches,
    dest_table,
    dw_cursor,
    update_column,
    columns_pk,
    insert_type,
    on_conflict,
    show_incremental_logs,
):
    position_pks = []
    total_inserted_rows = 0

    for index, batch in enumerate(batches):
        if index == 0:
            columns = batch[0].keys()
            for column_pk in columns_pk:
                for position, column in enumerate(columns):
                    if column.lower() == column_pk.lower().replace('"', ""):
                        position_pks.append(position)
                        break
        total_inserted_rows = iterate_rows(
            batch,
            dest_table,
            dw_cursor,
            update_column,
            columns_pk,
            position_pks,
            total_inserted_rows,
            insert_type,
            on_conflict,
            show_incremental_logs,
        )
    build_prefect_logger().info(f"Total inserted rows: {total_inserted_rows}")


def get_iter_batches(
    mssql_cursor,
    dest_table,
    dw_cursor,
    batch_size: int,
    origin_table,
    update_column,
    insert_type,
    exec_session,
    filter_origin,
    columns,
):
    if exec_session is None:
        exec_session = ""
    else:
        exec_session = f"exec user_session {exec_session}"

    if update_column and insert_type == "incremental":
        dw_cursor.execute(
            f"{exec_session} select max({update_column}) from {dest_table} "
        )
        row = dw_cursor.fetchone()
        if row[0] is not None:
            last_update = f"'{str(row[0])}'"
            mssql_cursor.execute(
                f"{exec_session} select {columns} from {origin_table} with(nolock) where {update_column} > left({last_update}, 23) "
            )
        else:
            mssql_cursor.execute(
                f"{exec_session} select {columns} from {origin_table} with(nolock) "
            )
    else:
        if filter_origin is None:
            filter_origin = ""
        else:
            filter_origin = f"where {filter_origin}"
        mssql_cursor.execute(
            f"{exec_session} select {columns} from {origin_table} with(nolock) {filter_origin}"
        )
    rows = mssql_cursor.fetchmany(batch_size)
    while len(rows) > 0:
        yield rows
        rows = mssql_cursor.fetchmany(batch_size)


def check_if_table_already_exist(dw_cursor, table):
    query = f"""
        select * from pg_tables as pt where pt.schemaname || '.' || pt.tablename = '{table}';
    """

    dw_cursor.execute(query)
    result = dw_cursor.fetchmany()

    if len(result) > 0:
        return True
    else:
        return False


def execute_sp(origin_secret, sp, variables):
    if variables is not None:
        param = []
        for var in variables:
            param.append(f"'{var}'")

        query = f"EXEC {sp} {','.join(param)}"

        with pymssql.connect(
            server=origin_secret["host"],
            port=origin_secret["port"],
            user=origin_secret["user"],
            password=origin_secret["password"],
            database=origin_secret["database"],
        ) as mssql_conn, mssql_conn.cursor(as_dict=True) as mssql_cursor:
            mssql_cursor.execute(query)
            data = mssql_cursor.fetchall()
            return data


def extract_load_data(origin_secret, info, insert_type="full", delete_type="truncate"):
    origin_table = info["origin_table"]
    dest_table = info["dest_table"]
    batch_size = info["batch_size"]

    if "filter_origin" in info:
        filter_origin = info["filter_origin"]
    else:
        filter_origin = None

    if "show_incremental_logs" in info:
        show_incremental_logs = True
    else:
        show_incremental_logs = False

    if "filter_destination" in info:
        filter_destination = info["filter_destination"]
    else:
        filter_destination = None

    if "exec_session" in info:
        exec_session = info["exec_session"]
    else:
        exec_session = None

    if "on_conflict" in info:
        on_conflict = info["on_conflict"]
    else:
        on_conflict = ""

    if "ignored_columns" in info:
        ignored_columns = info["ignored_columns"]
    else:
        ignored_columns = []
    if "update_column" in info:
        update_column = info["update_column"]
    else:
        update_column = ""

    if "port" not in origin_secret:
        origin_secret["port"] = 1433

    with pymssql.connect(
        server=origin_secret["host"],
        port=origin_secret["port"],
        user=origin_secret["user"],
        password=origin_secret["password"],
        database=origin_secret["database"],
    ) as mssql_conn, mssql_conn.cursor(as_dict=True) as mssql_cursor, psycopg2.connect(
        get_dsn()
    ) as dw_conn, dw_conn.cursor() as dw_cursor:
        # create table if not exists
        table_info_query = get_table_info_query(origin_table)

        mssql_cursor.execute(table_info_query)
        table_info = mssql_cursor.fetchall()

        cols, cols_pk, columns_to_select, columns_pk = build_columns_query(
            table_info, ignored_columns
        )

        table_exists = check_if_table_already_exist(dw_cursor, dest_table)

        if table_exists is False:
            create_table_query = build_create_query(f"{dest_table}", cols, cols_pk)
            dw_cursor.execute(create_table_query)
            dw_cursor.execute(f"alter table {dest_table} owner to prefect;")
            dw_conn.commit()

        if filter_destination is not None:
            build_prefect_logger().info(
                f"Running: delete from {dest_table} where {filter_destination}"
            )
            delete_statement = f"delete from {dest_table} where {filter_destination}"
            dw_cursor.execute(delete_statement)
        elif insert_type == "full":
            build_prefect_logger().info(
                f"Ensuring it will give the {dest_table} table owner to prefect role in the DW!"
            )
            if delete_type == "truncate":
                build_prefect_logger().info(f"Truncating {dest_table}")
                dw_cursor.execute(f"truncate table {dest_table};")
            elif delete_type == "delete":
                build_prefect_logger().info(f"Deleting data from {dest_table}")
                dw_cursor.execute(f"delete from {dest_table} where 1=1;")

        build_prefect_logger().info(f"Extracting in batches of {batch_size} rows")
        batches = get_iter_batches(
            mssql_cursor,
            dest_table,
            dw_cursor,
            batch_size,
            origin_table,
            update_column,
            insert_type,
            exec_session,
            filter_origin,
            columns_to_select,
        )

        iterate_batches(
            batches,
            dest_table,
            dw_cursor,
            update_column,
            columns_pk,
            insert_type,
            on_conflict,
            show_incremental_logs,
        )

        build_prefect_logger().info(f"Commiting changes to DW")
        dw_conn.commit()
