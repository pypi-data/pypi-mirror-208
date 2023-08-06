import datetime
import os
import random
import string
import time
from typing import Dict, Optional

import pandas as pd
import psycopg2
import psycopg2.pool

from . import queries
from wf_data_monitor.log import logger


class HoneycombDBHandle:
    __instance = None

    def __new__(cls, pg_uri: Optional[str] = None):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, pg_uri: Optional[str] = None):
        if pg_uri is None:
            pg_uri = os.getenv("PG_HONEYCOMB_URI", None)

        if pg_uri is None:
            raise ConnectionError(
                "Unable to connect to Honeycomb Postgres DB, no connection uri provided. Set using PG_HONEYCOMB_URI."
            )

        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(minconn=5, maxconn=20, dsn=pg_uri)

    def get_connection(self):
        return self.connection_pool.getconn()

    def _query(self, sql: str, params: Optional[Dict] = None, query_name: str = "UNKNOWN"):
        query_id = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        logger.info(f"({query_id}) Executing DB query '{query_name}'...")
        start = time.time()

        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SET search_path TO honeycomb")
            cursor.execute(sql, params)

            column_names = [d[0] for d in cursor.description]
            rows = cursor.fetchall()

            return pd.DataFrame(rows, columns=column_names)
        except (Exception, psycopg2.DatabaseError) as e:
            logger.info(
                f"({query_id}) Failed executing DB query '{query_name}'. Elapsed time: {(time.time() - start):0.2f}: {e}"
            )
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.connection_pool.putconn(connection)

            logger.info(
                f"({query_id}) Finished executing DB query '{query_name}'. Elapsed time: {(time.time() - start):0.2f}"
            )

    def query_positions(self, environment_name: str, start_time: datetime.datetime, end_time: datetime.datetime):
        return self._query(
            sql=queries.SELECT_POSITIONS_FOR_ENVIRONMENT,
            params={
                "environment_name": environment_name,
                "classroom_start_time": start_time,
                "classroom_end_time": end_time,
            },
            query_name="query_positions",
        )

    def query_environments(self):
        return self._query(sql="SELECT * from environments", query_name="query_environments")
