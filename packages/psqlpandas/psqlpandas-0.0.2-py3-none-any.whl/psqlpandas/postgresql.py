from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any
import logging

import pandas as pd
import numpy as np
import psycopg2
import psycopg2.extras as pgex
from sqlalchemy import create_engine, text


class DatabaseConnector(ABC):
    """
    This class act as a wrapper for the connector chosen.
    """

    def __init__(self, dbname: str):
        """
        Constructor

        Args:
            dbname (str): database name
        """
        self._dbname = dbname

    @abstractmethod
    def connect(self):
        """
        Returns connection
        """
        pass

    @abstractmethod
    def get_sqlalchemy_connection(self):
        pass


class PostgresqlDatabaseConnector(DatabaseConnector):
    def __init__(self, dbname: str, user: str, host: str, port: str, password: str):
        super().__init__(dbname)
        self._user = user
        self._host = host
        self._port = port
        self._password = password

    def connect(self):
        return psycopg2.connect(
            user=self._user,
            password=self._password,
            host=self._host,
            port=self._port,
            database=self._dbname,
        )

    def get_sqlalchemy_connection(self):
        engine = create_engine(
            f"postgresql+psycopg2://{self._user}:{self._password}@{self._host}:{self._port}/{self._dbname}"
        )
        return engine

    @staticmethod
    def execute_values(cursor, query, tuples):
        return pgex.execute_values(cursor, query, tuples)

    def read_from_db(
        self, query: str, parse_dates: List[str] | str | None = None
    ) -> pd.DataFrame:
        """
        Reads data from postgres db.

        Args:
            query (str): query
            parse_dates (List[str] | str | None, optional): list of columns to be parsed as dates. Defaults to None.

        Returns:
            pd.DataFrame: dataframe of the read data
        """
        if isinstance(parse_dates, str):
            parse_dates = [parse_dates]
        try:
            engine = self.get_sqlalchemy_connection()
            with engine.begin() as connection:
                table = pd.read_sql_query(
                    text(query), con=connection, parse_dates=parse_dates
                )
            engine.dispose()
        except Exception as e:
            logging.error(f"Error while executing query: {query}")
            logging.error(e)
            raise
        if parse_dates is not None:
            for col in parse_dates:
                table[col] = pd.to_datetime(table[col])

        return table

    def execute_sql_query(self, query, row=None):
        conn = self.connect()
        cur = conn.cursor()

        try:
            if row is None:
                cur.execute(query)
            else:
                cur.execute(query, row)
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error while executing query: {query}")
            logging.error(e)
            cur.close()
            conn.close()
            raise

    def execute_sql_query_values(self, query: str, tuples: Tuple[Any]):
        conn = self.connect()
        cur = conn.cursor()

        try:
            self.execute_values(cur, query, tuples)
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error while executing query: {query}")
            logging.error(e)
            cur.close()
            conn.close()
            raise

    def update_db_row(
        self,
        df_dict: Dict[str, object],
        tablename: str,
        sql_where_condition: str | None = None,
    ) -> bool:

        # If you have more than one columns to update
        if len(df_dict.keys()) > 1:
            sql = "UPDATE {} SET ({}) = ({}) ".format(
                tablename,
                ",".join([column for column in df_dict.keys()]),
                ",".join(
                    [
                        f"'{element}'" if element not in [None, []] else "NULL"
                        for element in df_dict.values()
                    ]
                ),
            )
        # If you have only 1 column to modify need to configure a different query
        elif len(df_dict.keys()) == 1:
            sql = f"UPDATE {tablename} SET {list(df_dict.keys())[0]} = {list(df_dict.values())[0]} "
        else:
            raise ValueError(
                "Impossible to generate the update query since data are empty"
            )

        if sql_where_condition is not None:
            sql += sql_where_condition

        return self.execute_sql_query(sql)

    def delete_db_row(
        self,
        tablename: str,
        sql_where_condition: str,
        direct_delete: bool = False,
        update_field: str = "available",
    ) -> bool:
        """
        Delete a database data composing a SQL String with tablename and row id you want to remove

        Args:
            tablename (str): Name of the table
            sql_where_condition (str): SQL Where condition to attach to the query (it's important because you want to delete only a single row).
                Impossible to use the delete without a where setting: for policy and safety purpose.
            direct_delete (bool): If you want to direct delete a row, or just want to update a flag
            update_field (str): Flag field for the deletion (available field column)

        Returns:
            bool: query execution result (True or False)
        """
        # Delete directly the row or bulk of rows
        if direct_delete:
            sql = f"DELETE FROM {tablename} "
        # Just update the flag: available to False
        else:
            sql = f"UPDATE {tablename} SET {update_field} = False "

        # Compose the where condition (it's mandatory to avoid unwanted deletion)
        sql += sql_where_condition

        return self.execute_sql_query(sql)

    def insert_from_df(
        self, tablename: str, df: pd.DataFrame, replace: bool = False
    ) -> bool:
        """
        Inserts data from a pandas dataframe to postgres db.

        Args:
            tablename (str): target tablename
            df (pd.DataFrame): dataframe with data
            replace (bool, optional): whether to replace or not already present data. Defaults to False.

        Returns:
            bool: True if successful without errors
        """

        # duplicate the object because it's required to manipulate some columns
        df_columns = list(set(df.columns) - {"id"})

        # Setting null (and inf) values to None for postgres
        tuples = [
            tuple(x)
            for x in df.astype(object)
            .where(pd.notnull(df) & ~df.isin([np.inf, -np.inf]), None)[df_columns]
            .to_numpy()
        ]

        insertsql = "INSERT INTO {} ({}) VALUES %s".format(
            tablename, ",".join(df_columns)
        )

        # Update if there are data already
        if replace:
            # Query from https://wiki.postgresql.org/wiki/Retrieve_primary_key_columns
            primary_keys_sql = (
                f"SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND "
                f"a.attnum = ANY(i.indkey) WHERE i.indrelid = '{tablename}'::regclass AND i.indisprimary;"
            )
            primary_keys = list(self.read_from_db(primary_keys_sql))
            columns_to_update = [x for x in df_columns if x not in primary_keys]
            insertsql = (
                insertsql
                + " ON CONFLICT ON CONSTRAINT "
                + tablename
                + "_pkey DO UPDATE SET ("
                + ",".join([column for column in columns_to_update])
                + ") = ("
                + ",".join(["EXCLUDED." + column for column in columns_to_update])
                + ")"
            )

        return self.execute_sql_query_values(insertsql, tuples)
