import json
import logging
from pathlib import Path

import pandas as pd
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
if __name__ == "__main__":
    project_id = "cto-crv-dev"
    bucket_name = "crv_gold"
    dataset_id = "gold"
    table_id = "EXCEL_DATA"
    gbq = NPGBQ(project_id=project_id)

    gbq.create_log_table()
    filepath = "./Integration supplier list.xlsx"
    df = pd.read_excel(filepath, engine="openpyxl", skiprows=1)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    fp_schema = "./gbq_table_schema.json"
    # gbq.get_str_schema_from_list(df.columns, output_filename=fp_schema)

    with open(fp_schema) as f:
        schema_original = json.load(f)

    schema_dict_gbq = {}
    for k, v in schema_original.items():
        col_name = gbq.get_valid_colname(k)
        schema_dict_gbq[col_name] = v

    schema_gbq = gbq.generate_bq_schema_from_dict(schema_dict_gbq)
    rename_dict = gbq.get_col_rename_dict(schema_original, schema_dict_gbq)

    df = gbq.rename_columns(df, rename_dict)
    df = gbq.convert_dtype(df, schema_gbq)

    gbq.create_bq_table(dataset_id, table_id, schema_gbq)
    gbq.insert_dataframe_to_bq_table(
        df, dataset_id, table_id, schema_gbq, mode="append"
    )
