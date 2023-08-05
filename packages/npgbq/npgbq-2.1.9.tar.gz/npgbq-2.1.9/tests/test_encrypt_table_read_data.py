# https://cloud.google.com/bigquery/docs/customer-managed-encryption#python
from google.cloud import bigquery

from npgbq import NPGBQ

client = bigquery.Client()

gbq_service_account_path = "./tests/nplearn_admin.json"
project_id = "nplearn"
gbq = NPGBQ(project_id=project_id, gcp_service_account_path=gbq_service_account_path)
data = gbq.get_data_from_gbq("SELECT * FROM `nplearn.test_cmek.cmek_test`")
print(data)

# ================================= query the table =================================
