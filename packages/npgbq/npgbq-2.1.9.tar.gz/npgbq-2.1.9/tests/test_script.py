from npgbq import NPGBQ
import pandas as pd


if __name__ == "__main__":
    gbq_service_account_path = r"D:\np\npgbq\scbpt_bq_admin.json"

    # ====================================== create instance ======================================
    gbq = NPGBQ(gbq_service_account_path=gbq_service_account_path)

    # ====================================== 0. create log table and insert some log ======================================
    gbq.create_log_table()
    gbq.log2bq(message="hello test")

    # ====================================== 1. load from dataframe ======================================
    dataset_name = "zz_test"
    table_name = "from_dataframe"
    loading_mode = "truncate"
    data = [
        {"firstname": "nopporn1", "lastname": "phantawee", "age": 33},
        {"firstname": "nopporn2", "lastname": "phantawee2", "age": 34},
    ]
    df = pd.DataFrame(data)
    schema_dict = {
        "firstname": "STRING",
        "lastname": "STRING",
        "age": "INT64",
    }
    schema = gbq.generate_bq_schema_from_dict(schema_dict)
    gbq.create_bq_dataset(dataset_name)
    gbq.create_bq_table(dataset_name, table_id=table_name, schema=schema)

    # insert data
    gbq.insert_dataframe_to_bq_table(
        df, dataset_name, table_name, schema, mode=loading_mode
    )
