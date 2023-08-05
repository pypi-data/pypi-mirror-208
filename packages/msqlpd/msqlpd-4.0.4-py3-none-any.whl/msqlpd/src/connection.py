"""
This module manages accessing mariadb and read/write data
The module provides features like:
 - read tables into pandas
 - write dataframes into tables
 - convert sql queries to pandas format
 - execute queries
Why this module exists?
Because Pandas itself has poor tools to interact with sql databases,
Examples that Pandas fails to perform:
- You table already exists in the database, you need to push a dataframe into the table.
  but some rows in dataframe has same primary key in the table and pandas fails to update the rows in the table given rows in the dataframe.
  it can not performe REPLACE statements on the table for duplicated primary keys. 

- Read/write data from/to the database through pandas is not parallelized and in case you need to push fairly big data to the database, it takes too much time
  and you may face problems like time_out error.
  
- MySQL dtypes are not fully mapped with right Pandas dtypes. For example, if you have DATE dtype in mariadb, pandas will read that as object dtype.
  or if you have INT dtype in mariadb, pandas will read that as float when null value exists. Because Pandas does not support int (any primitive type) column with null values.
"""

import os
from collections import OrderedDict
from sqlalchemy import create_engine
from mysql import connector
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

DEFAULT_HOST = "127.0.0.1"
DEFAULT_DATABASE_PORT = 3306
PARALLEL_CONNECTIONS_NUMBER = os.cpu_count()


def refactor_query(table_name:str, conditions:list[str]=None, usecols:list[str]=None) -> str:
    """It gives a table_name, add conditions to the sql query that reads the tables and pick fields from usecols

    Args:
        table_name (str): table name
        condition (str, optional): list of conditions. e.g. ['progw > 10', 'SKU_code > 0']. Defaults to None.
        usecols (list[str], optional): list of fields to load. e.g. ['VND', 'GI', 'progw', 'SKU_code']. Defaults to None.

    Returns:
        str: sql query
    """
    
    if conditions is None and usecols is None:
        query = "SELECT * FROM " + table_name + ";"
    elif conditions is not None and usecols is None:
        query = "SELECT * FROM " + table_name + " WHERE " + " and ".join(conditions) + ";"
    elif conditions is None and usecols is not None:
        query = "SELECT {} FROM ".format(",".join(usecols)) + table_name + ";"
    else:
        query = (
            "SELECT {} FROM ".format(",".join(usecols))
            + table_name
            + " WHERE "
            + " and ".join(conditions)
            + ";"
        )
    return query


def convert_dtype_mariadb_to_pandas(dtype: str) -> str:
    """It converts mariadb dtype to corresponding pandas dtype
    pandas dtype all return as str and later have to process dataframe based on returned dtype and take right action

    Args:
        dtype (str): mariadb dtype

    Raises:
        Exception: if mariadb dtype is not already identified

    Returns:
        str: pandas dtype as str
    """
    dtype = dtype.lower()
    if "int" in dtype:
        return "integer"
    if "char" in dtype:
        return "string"
    if "date" in dtype:
        return "datetime"
    if "binary" in dtype:
        return "integer"
    if "float" in dtype:
        return "float"
    if "double" in dtype:
        return "float"
    if "text" in dtype:
        return "string"
    if "decimal" in dtype:
        return "float"
    raise Exception(f"dtype {dtype} is not implemented yet.")

class DataBase:
    def __init__(
        self,
        username: str,
        password: str,
        database: str = None,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_DATABASE_PORT,
        n_jobs: int = PARALLEL_CONNECTIONS_NUMBER,
    ):
        """_summary_

        Args:
            username (str): mariadb username
            password (str): mariadb password
            database (str, optional): mariadb database name
            host (str, optional): host IP. Defaults to DEFAULT_HOST.
            port (int, optional): host port. Defaults to DEFAULT_DATABASE_PORT.
        """        
        self.database = database  # database name
        self.username = username  # database username
        self.password = password  # database password
        self.host = host  # database host IP
        self.port = port  # database port (e.g. 3306)
        self.n_jobs = n_jobs # number of jobs

    def get_engine(self):
        """It generates engine of the corresponding connection

        Returns:
            _type_: _description_
        """        
        engine = create_engine(self.get_engine_url())
        return engine

    def get_engine_url(self):
        engine_url = (
            "mysql+pymysql://"
            + self.username
            + ":"
            + self.password
            + "@"
            + f"{self.host}:{str(self.port)}"
        )
        if self.database is not None:
            engine_url += "/" + self.database
        # print(engine_url)
        return engine_url

    def execute_query(self, *args):
        self.cursor.execute(*args)
        self.connection.commit()

    def enter(self):
        return self.__enter__()

    def __enter__(self):
        self.connection = connector.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.database,
            use_pure=True,
        )
        self.cursor = self.connection.cursor()
        self.util = DataBase.Functions(
            self.connection, self.cursor, self.get_engine_url(), self.execute_query, self.n_jobs
        )
        return self

    def exit(self, exc_type, exc_value, exc_tb):
        self.__exit__(exc_type, exc_value, exc_tb)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.cursor.close()
        self.connection.close()

    class Functions:
        def __init__(self, db, cursor, engine, execute, n_jobs) -> None:
            self.cursor = cursor
            self.db = db
            self.engine = engine
            self.execute = execute
            self.n_jobs = n_jobs

        def get_table_schema(self, table_name):
            self.cursor.execute(f"DESCRIBE {table_name};")
            schema = self.cursor.fetchall()
            schema_df = pd.DataFrame(
                schema, columns=["Field", "Type", "Null", "Key", "Default", "Extra"]
            )
            schema_df["pandas_type"] = schema_df["Type"].map(
                convert_dtype_mariadb_to_pandas
            )
            schema = OrderedDict()
            for _, row in schema_df.iterrows():
                schema[row["Field"]] = row["pandas_type"]
            return schema

        def refine_column(self, df_column, dtype):
            if dtype == "integer":
                if any(df_column.isna()):
                    df_column = df_column.astype(np.float64)
                else:
                    df_column = df_column.astype(int)
                return df_column
            if dtype == "float":
                df_column = df_column.astype(np.float64)
                return df_column
            if dtype == "string":
                df_column = df_column.astype(str)
                df_column = df_column.replace("None", np.nan)
                return df_column
            if dtype == "datetime":
                df_column = pd.to_datetime(df_column, format="%Y-%m-%d %H:%M:%S")
                return df_column
            raise Exception(f"can not convert to dtype {dtype}")

        def refine_dtype(self, df, schema):
            for column, dtype in schema.items():
                if column in df.columns:
                    df[column] = self.refine_column(df[column], dtype)
            return df

        def __read_table(self, table_name, conditions=None, usecols=None):
            query = refactor_query(table_name, conditions, usecols)
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            df = pd.DataFrame(data)
            return df

        def read_table(self, table_name, conditions=None, usecols=None):
            schema = self.get_table_schema(table_name)
            df = self.__read_table(table_name, conditions=conditions, usecols=usecols)
            if usecols is None:
                columns = schema.keys()
            else:
                columns = usecols
            if len(df) == 0:
                for col in columns:
                    df[col] = None
            else:
                df.columns = columns
            df = self.refine_dtype(df, schema)
            return df
        
        def __push_into_table(self, table_name, df, chunk_size = 5000, in_parallel=True):
            l_df = len(df)
            col_num = len(df.columns)
            if col_num < 10:
                n_jobs = self.n_jobs*4
            elif col_num < 20:
                n_jobs = self.n_jobs*2
            else:
                n_jobs = self.n_jobs
            is_first_chunk = True
            jobs = []
            for chunk_index in range(0, l_df, chunk_size):
                d = df.iloc[chunk_index : (chunk_index + chunk_size)]
                if is_first_chunk:
                    is_first_chunk = False
                    if not self.exists(table_name):
                        d.to_sql(
                            name=table_name, con=self.engine, if_exists="replace", index=False
                        )
                    else:
                        jobs.append(
                                    delayed(d.to_sql)(
                                        name=table_name,
                                        con=self.engine,
                                        if_exists="append",
                                        index=False,
                                    ))
                else:
                    jobs.append(
                        delayed(d.to_sql)(
                            name=table_name,
                            con=self.engine,
                            if_exists="append",
                            index=False,
                        )
                    )
            if len(jobs) > 0:
                if in_parallel:
                    print("number of jobs", len(jobs))
                    Parallel(n_jobs=n_jobs, batch_size=n_jobs, verbose=10)(jobs)
                else:
                    Parallel(n_jobs=1)(jobs)


        def __modify_table(self, table_name, df, method, in_parallel=True):
            if method == "create":
                self.__push_into_table(table_name, df, in_parallel=in_parallel)
                return
            table_schema = self.get_table_schema(table_name)
            for column in df.columns:
                if column not in table_schema.keys():
                    raise Exception(
                        f"column {column} does not exist in table {table_name}"
                    )
            for column in table_schema.keys():
                if column not in df.columns:
                    df[column] = np.nan
            df = df[table_schema.keys()]
            for col, dtype in df.dtypes.items():
                if dtype == object:
                    df[col] = df[col].replace("None", np.nan)
            table_name_tmp = table_name + "_tmp"
            if method == "insert":
                REPLACE_QUERY = (
                    f"INSERT INTO {table_name} SELECT * FROM {table_name_tmp}"
                )
            if method == "replace":
                REPLACE_QUERY = (
                    f"REPLACE INTO {table_name} SELECT * FROM {table_name_tmp}"
                )
            if method == "truncate":
                TRUNCATE_QUERT = f"TRUNCATE TABLE {table_name}"
                self.execute(TRUNCATE_QUERT)
                self.__modify_table(table_name, df, "insert")
                return
            DROP_QUERY = f"DROP TABLE IF EXISTS {table_name_tmp}"
            
            if method == 'insert':
                self.__push_into_table(table_name=table_name, df=df, in_parallel=in_parallel)
                return
            else:
                self.execute(DROP_QUERY)
                self.__push_into_table(table_name=table_name_tmp, df=df, in_parallel=in_parallel)
                self.execute(REPLACE_QUERY)
                self.execute(DROP_QUERY)
                return
        def __raise_table_not_exists_exception(self, table_name):
            if not self.exists(table_name):
                raise Exception(f"table {table_name} does not exist")
        def __raise_table_exists_exception(self, table_name):
            if self.exists(table_name):
                raise Exception(f"table {table_name} already exists")
        
        def update_table(self, table_name, df):
            self.__raise_table_not_exists_exception(table_name)
            self.__modify_table(table_name, df, method="replace")

        def append_table(self, table_name, df, in_parallel=True):
            self.__raise_table_not_exists_exception(table_name)
            self.__modify_table(table_name, df, method="insert", in_parallel=in_parallel)

        def replace_table(self, table_name, df):
            self.__raise_table_not_exists_exception(table_name)
            self.__modify_table(table_name, df, method="truncate")
            
        def create_table(self, table_name, df):
            self.__raise_table_exists_exception(table_name)
            self.__modify_table(table_name, df, method="create")
            
        def read_sql(self, query):
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            return data
        
        def exists(self, table_name):
            query = "SHOW TABLES"
            for row in self.read_sql(query):
                if row[0] == table_name:
                    return True
            return False
