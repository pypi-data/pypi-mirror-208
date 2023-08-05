# https://cloud.google.com/bigquery/docs/customer-managed-encryption#python
import pandas as pd
from google.cloud import bigquery
from npgbq import NPGBQ
client = bigquery.Client()

# ================================= create table encrypt =================================
# TODO(dev): Change table_id to the full name of the table you want to create.
table_id = "nplearn.test_cmek.cmek_test"

# Set the encryption key to use for the table.
# TODO: Replace this key with a key you have created in Cloud KMS.
kms_key_name = (
    "projects/nplearn/locations/asia-southeast1/keyRings/npkeyring/cryptoKeys/npkey"
)

table = bigquery.Table(table_id)
table.encryption_configuration = bigquery.EncryptionConfiguration(
    kms_key_name=kms_key_name
)
table = client.create_table(table)  # API request

print(f"Created {table_id}.")
print(f"Key: {table.encryption_configuration.kms_key_name}.") # type: ignore

# ================================= insert data to the table =================================
schema = []
schema.append(bigquery.SchemaField("username", "STRING", mode="REQUIRED"))
schema.append(bigquery.SchemaField("userage", "INTEGER", mode="REQUIRED"))
data = [('dew',34)]
df = pd.DataFrame(data, columns=['username','userage'])
gbq_service_account_path = './tests/nplearn_admin.json'
project_id = 'nplearn'
gbq = NPGBQ(project_id=project_id,gcp_service_account_path=gbq_service_account_path)
gbq.create_log_table()
gbq.insert_dataframe_to_bq_table(
    df, 'test_cmek', 'cmek_test', schema, mode='truncate'
)

# ================================= query the table =================================
