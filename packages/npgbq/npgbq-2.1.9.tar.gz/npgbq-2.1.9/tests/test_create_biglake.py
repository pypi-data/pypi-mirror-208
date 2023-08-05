from npgbq import NPGBQ

project_id = "nplearn"
bucket_name = "np_sample_bucket"
table_name = "create_from_python"
table_id = f"nplearn.test_lab.{table_name}"
gcs_uri = f"gs://{bucket_name}/good_parquet/*.parquet"
connection_id = "nplearn.asia-southeast1.npsample"

gbq = NPGBQ(project_id)

gbq.create_external_table_from_gcs(
    table_id=table_id,
    gcs_uri=gcs_uri,
    file_type="parquet",
    is_hive_partition=False,
    connection_id=connection_id,
)
