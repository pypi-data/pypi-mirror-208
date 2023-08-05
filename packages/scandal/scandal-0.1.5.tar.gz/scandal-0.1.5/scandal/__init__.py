import logging
import time
from typing import List, Optional, Tuple

from adbc_driver_flightsql import dbapi  # type:ignore

from scandal._auth import auth_user

logging.basicConfig(level=logging.INFO)


def connect(org: Optional[str] = None, project: Optional[str] = None, auth_token: Optional[str] = None):
    """Connect to Scandal.

    By default,
        - For interactive users we log in using an OAuth2 device code flow to the user's default organization.
        - For non-interactive users, we pick up creds from a credentials chain.
    """
    if not auth_token:
        auth_token = auth_user()

    # For now, we send the token as the Basic Auth password. This is because the response headers
    # aren't respected when using Bearer auth: https://github.com/apache/arrow-adbc/issues/584
    db_kwargs = {"username": "scandal", "password": auth_token}

    if project:
        # Connect directly to a project
        db_kwargs[_custom_header("x-fulcrum-project")] = project
    if org:
        db_kwargs[_custom_header("x-fulcrum-org")] = org

    return dbapi.connect("grpc://localhost:8443", db_kwargs)


def _custom_header(name: str):
    # Construct the name of a custom header to pass to the Flight SQL server
    return f"adbc.flight.sql.rpc.call_header.{name}"


if __name__ == "__main__":
    import pandas_gbq  # type:ignore
    from google.oauth2.service_account import Credentials  # type:ignore

    sql = "SELECT * from tpch.lineitem"

    credentials = Credentials.from_service_account_file(
        "../../crowbar/crowbar-server/src/test/resources/bigquery.creds.json"
    )
    conn = connect(org="my-org", project="my-source")

    times: List[Tuple[float, float, float]] = []
    for i in range(10):
        start = time.time()
        df = pandas_gbq.read_gbq(sql, credentials=credentials)
        # df = pandas_gbq.read_gbq("loyal-road-382017.tpch.lineitem", credentials=credentials)
        pdt = time.time() - start
        print("PandasBQ", pdt, "seconds")

        # start = time.time()
        # df = pd.read_sql_query(sql, conn)
        # sdt = time.time() - start
        # print("Scandal", sdt, "seconds")

        start = time.time()
        curr = conn.cursor()
        curr.execute(sql)
        table = curr.fetch_arrow_table()
        df = table.to_pandas()
        sat = time.time() - start
        print("Scandal Arrow", sat, "seconds")
        # print(table)

        # times.append((pdt, sdt, sat))

    print(times)
