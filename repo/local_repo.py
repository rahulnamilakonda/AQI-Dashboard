from logging import DEBUG
import sqlite3
from datetime import datetime

import pandas as pd


class LocalRepo:

    def __init__(self):
        self._conn = sqlite3.connect("sql.db")
        self._cursor = self._conn.cursor()
        self._create_table()

    def __del__(self):
        self._conn.close()

    def _create_table(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS AIR_QUALITY_DATA (
            value REAL,
            flagInfo_hasFlags BOOLEAN,
            parameter_id INTEGER,
            parameter_name TEXT,
            parameter_units TEXT,
            parameter_displayName TEXT,
            period_label TEXT,
            period_interval TEXT,
            period_datetimeFrom_utc TIMESTAMP,
            period_datetimeFrom_local TIMESTAMP,
            period_datetimeTo_utc TIMESTAMP,
            period_datetimeTo_local TIMESTAMP,
            coordinates TEXT,
            summary_min REAL,
            summary_q02 REAL,
            summary_q25 REAL,
            summary_median REAL,
            summary_q75 REAL,
            summary_q98 REAL,
            summary_max REAL,
            summary_avg REAL,
            summary_sd REAL,
            coverage_expectedCount INTEGER,
            coverage_expectedInterval TEXT,
            coverage_observedCount INTEGER,
            coverage_observedInterval TEXT,
            coverage_percentComplete REAL,
            coverage_percentCoverage REAL,
            coverage_datetimeFrom_utc TIMESTAMP,
            coverage_datetimeFrom_local TIMESTAMP,
            coverage_datetimeTo_utc TIMESTAMP,
            coverage_datetimeTo_local TIMESTAMP,
            sensor_id INTEGER
        );
        """
        )
        self._conn.commit()

    def get_measurement_histroy(
        self,
        from_year: int,
        to_year: int,
        sensor_id: int,
    ):
        dnow = False
        if to_year == datetime.now().year:
            dnow = True
        return pd.read_sql_query(
            "SELECT * FROM AIR_QUALITY_DATA WHERE period_datetimeFrom_utc>=? AND period_datetimeTo_utc<=? AND sensor_id=? ",
            con=self._conn,
            params=(
                datetime(year=from_year, month=1, day=1),
                datetime.now() if dnow else datetime(year=to_year, month=1, day=1),
                sensor_id,
            ),
        )

    def put_sql(self, df: pd.DataFrame, table_name: str):

        df.to_sql(name=f"{table_name}", con=self._conn, if_exists="append", index=False)
        self._conn.commit()

    def _select(self):
        self._cursor.execute("SELECT * FROM AIR_QUALITY_DATA LIMIT 10; ")
        print(self._cursor.fetchall())

    def _drop(self):
        self._cursor.execute("DROP TABLE AIR_QUALITY_DATA;")
        self._conn.commit()


if __name__ == "__main__":
    if DEBUG:
        lr = LocalRepo()
        # lr._drop()
        # lr._select()
