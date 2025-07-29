import pandas as pd
from src.utilities import customlogger
import teradatasql
import os
import pytest
import threading
import teradata

logger = customlogger.custom_logger()

class TeradataHelper:

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.connection = None
        self.jenkins_run = bool(os.getenv("JENKINS_RUN"))

    def connect(self):
        if self.jenkins_run:
            udaExec = teradata.UdaExec(
                appName="TDWallet_Connection", version="1.0", logConsole=False
            )
            self.connection = udaExec.connect(
                method="odbc",
                system=os.getenv("TERADATA_HOST"),
                username=os.getenv("TDWALLET_USERNAME"),
                password=os.getenv("TDWALLET_PASSWORD"),
                driver="Teradata",
                transactionMode="TMODE",
                charset="UTF16",
            )
            logger.info(
                f"Connection to {self.host} established for user {os.getenv('TDWALLET_USERNAME')}"
            )
        else:
            con_str = f"""{{
                "host": "{self.host}",
                "user": "{self.user}",
                "password": "{self.password}",
                "logmech": "LDAP"
                }}"""
            self.connection = teradatasql.connect(con_str)
            logger.info(f"Connection to {self.host} established for user {self.user}")

    def execute_query(self, query, timeout=1800):
        if self.connection is None:
            logger.info(f"No active connection to {self.host}")
            return None

        def run_query():
            with self.connection.cursor() as cur:
                try:
                    cur.execute(query)
                    self.result = pd.DataFrame(
                        cur.fetchall(), columns=[desc[0] for desc in cur.description]
                    )
                    logger.info("Query Executed Successfully")
                except Exception as ex:
                    self.result = ex
                    logger.info(ex)

        self.result = None
        query_thread = threading.Thread(target=run_query)
        query_thread.start()
        query_thread.join(timeout)
        if query_thread.is_alive():
            logger.info("Query timed out")
            pytest.skip("Query timed out")
        return self.result

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            logger.info("Connection closed")
