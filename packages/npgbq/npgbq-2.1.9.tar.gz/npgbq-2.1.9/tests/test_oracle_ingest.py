import logging
import os
import platform
from io import BytesIO
from pathlib import Path

import cx_Oracle
import pandas as pd
from npgcs import NPGCS

from npgbq import NPGBQ

log_dir = "./log"
Path(log_dir).mkdir(exist_ok=True, parents=True)
log_path = str(Path(log_dir).joinpath(Path(__file__).stem)) + ".log"

logger = logging.getLogger(__name__)
logger.propagate = False  # remove duplicated log
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler(
    log_path, mode="a", encoding="utf-8", delay=False
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# ================================= Oracle settings =================================
# provide the path contain Oracle client manually
LOCATION = r"D:\np\central-crv\oracle_client\instantclient_19_5"
LOCATION = "./oracle_client/instantclient_21_7"
print("ARCH:", platform.architecture())
files_at_location = []
for name in os.listdir(LOCATION):
    files_at_location.append(name)
os.environ["PATH"] = LOCATION + ";" + os.environ["PATH"]

# credentails
username = "pocmigration"
password = "RaQ7075RI6"
dsn = "GOLD"

# create DNS_TNS with particular users
dsn_tns = cx_Oracle.makedsn("192.168.200.130", "1521", service_name="GOLD")
conn = cx_Oracle.connect(
    user="pocmigration",
    password="RaQ7075RI6",
    dsn=dsn_tns,
    encoding="US-ASCII",
    nencoding="utf-8",
)


tables = [
    "REPLACEME_LOL",
    # "HUONGNGUYEN.SC_STR_SUP_062022_CURRENT_VIZ",
]

table_completed = [
    # "HUONGNGUYEN.SC_WH_SUP_102021_052022_VIZ",
    # "QUYENNGUYEN.SC_STORE_WH_SKU",
]

# ================================= Functions =================================
def get_columns_info(conn, schema_name=None, table_name=None) -> pd.DataFrame:
    if schema_name is not None:
        sql = f"SELECT * FROM all_tab_cols where OWNER='{schema_name}' and TABLE_NAME='{table_name}'"
        sql = f"""
        SELECT * 
        FROM all_tab_cols 
        where OWNER='{schema_name}' 
        and TABLE_NAME='{table_name}'
        and COLUMN_ID is not null order by OWNER, TABLE_NAME,COLUMN_ID
        """
    else:
        sql = f"SELECT * FROM all_tab_cols WHERE COLUMN_ID is not null order by OWNER, TABLE_NAME,COLUMN_ID"
    return pd.read_sql(sql, conn)


def get_schema_dict(df: pd.DataFrame):
    schema_dict = {}
    for index, row in df.iterrows():
        schema_dict[row["object_name"]] = row["schema_name"]
    return schema_dict


def get_schema_org_dict(df: pd.DataFrame) -> dict:
    output = {}
    for index, row in df[["COLUMN_NAME", "DATA_TYPE"]].iterrows():
        output[row["COLUMN_NAME"]] = row["DATA_TYPE"]
    return output


if __name__ == "__main__":
    # chunksize = 100000
    CHUNK_SIZE = 100000
    # gcs
    project_id = "cto-crv-dev"
    bucket_name = "crv_gold"
    dataset_id = "gold"
    gcs = NPGCS(project_id=project_id)
    gbq = NPGBQ(project_id=project_id)

    # filter only the table that not completed
    tables = [table for table in tables if table not in table_completed]

    # loop over tables
    for table in tables:
        logger.info(f"Start {table}")
        # count number of rows
        sql = f"SELECT COUNT(*) FROM {table}"
        df_count = pd.read_sql(sql, conn)
        logger.info(f"Total number of rows {table}: {df_count.iloc[0,0]:,}")

        # get schema and table name from the table
        schema_name, table_name = table.split(".")

        # in each table get the information schema from oracle
        _df = get_columns_info(conn, schema_name, table_name)
        schema_original = get_schema_org_dict(_df)
        logger.info(f"Schema original {schema_original}")

        # generate schema_dict from the information schema
        schema_dict = gbq.get_schema_dict_from_db(_df, db_engine="oracle")
        schema_bq = gbq.generate_bq_schema_from_dict(schema_dict)
        rename_dict = gbq.get_col_rename_dict(schema_original, schema_dict)
        logger.info(f"Schema_dict {schema_dict}")

        # iterate over the table with chunksize
        file_count, n_recs = 0, 0
        blob_path = None
        logger.info(f"Extracting from table {table}")
        sql_table = f"""
        SELECT * FROM {table}
        """
        for df in pd.read_sql(
            sql_table,
            conn,
            chunksize=CHUNK_SIZE,
        ):
            # convert the data type to the correct type
            logger.info(f"Converting data type {df.shape}")
            df = gbq.rename_columns(df, rename_dict)
            df = gbq.convert_dtype(df, schema_bq)

            # upload to gcs
            logger.info(f"Saving as byte")
            fo = BytesIO()
            df.to_parquet(fo, engine="pyarrow", compression="gzip")
            fo.seek(0)
            blob_path = f"{schema_name}/{table_name}"
            blob_name = f"{blob_path}/{schema_name}_{table_name}_part_{file_count:09d}.parquet"
            logger.info(f"Uploading to GCS {blob_name}")
            gcs.upload_blob_from_stream(
                bucket_name, file_obj=fo, destination_blob_name=blob_name
            )

            # update file_count
            file_count += 1
            n_recs += df.shape[0]
            logger.info(f"Part done {file_count} : {n_recs} records")
        logger.info(
            f"Extracted data from {table} to GCS, Total {file_count} files, {n_recs} records"
        )
        # create external table in BigQuery
        if blob_path is not None:
            table_id = f"{project_id}.{dataset_id}.{schema_name}_{table_name}"
            logger.info(f"Creating table {table_id}")
            gcs_uri = f"gs://{bucket_name}/{blob_path}/*.parquet"
            gbq.create_external_table_from_gcs(table_id, schema_bq, gcs_uri)
        logger.info(f"Completed {table}")
