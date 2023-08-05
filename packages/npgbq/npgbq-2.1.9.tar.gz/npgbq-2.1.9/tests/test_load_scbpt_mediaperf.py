from npgbq import NPGBQ
import pandas as pd


if __name__ == "__main__":
    gbq_service_account_path = r"D:\np\npgbq\scbpt_bq_admin.json"

    # ====================================== create instance ======================================
    gbq = NPGBQ(gbq_service_account_path=gbq_service_account_path)

    # ====================================== 0. create log table and insert some log ======================================
    # gbq.create_log_table()
    # gbq.log2bq(message="hello test")

    # ====================================== 1. sale order ======================================
    dataset_name = "scbpt_dataset"
    table_name = "media_performance"
    loading_mode = "truncate"

    fp = "./data/media_performance_by_months.xlsx"
    df = pd.read_excel(fp, engine="openpyxl", dtype=str)

    schema_dict = {
        "as_of": "DATE",
        "media_type": "STRING",
        "mediachannel": "STRING",
        "budgetspent": "FLOAT",
        "impressions": "FLOAT",
        "ctr": "FLOAT",
        "linkclick": "FLOAT",
        "cpm": "FLOAT",
        "costperlinkclick": "FLOAT",
        "purchase": "FLOAT",
        "droplead": "FLOAT",
    }
    rename_dict = {}

    dtype_config = gbq.generate_dtype_from_schema(schema_dict)
    df = gbq.convert_dtype(df, dtype_config)
    schema = gbq.generate_bq_schema_from_dict(schema_dict)
    gbq.create_bq_dataset(dataset_name)
    # gbq.delete_bq_table(dataset_name, table_name)
    gbq.create_bq_table(dataset_name, table_id=table_name, schema=schema)
    gbq.insert_dataframe_to_bq_table(
        df, dataset_name, table_name, schema, mode=loading_mode
    )
