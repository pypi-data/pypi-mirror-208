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
    table_name = "order_campaign"
    loading_mode = "truncate"

    fp = "./data/sale_order_province_url.xlsx"
    df = pd.read_excel(fp, engine="openpyxl", dtype=str)

    schema_dict = {
        "applicationformid": "STRING",
        "paymentmethod": "STRING",
        "insurer": "STRING",
        "producttype": "STRING",
        "producttemplatename": "STRING",
        "packagename": "STRING",
        "packagepackagecode": "STRING",
        "paymentmode": "STRING",
        "maintotalpremium": "FLOAT",
        "mainvatpremium": "FLOAT",
        "mainnetpremium": "FLOAT",
        "mainstamppremium": "FLOAT",
        "addontotalpremium": "FLOAT",
        "addonnetpremium": "FLOAT",
        "addonvatpremium": "FLOAT",
        "addonstamppremium": "FLOAT",
        "coupondiscount": "FLOAT",
        "discount": "FLOAT",
        "status": "STRING",
        "status1": "STRING",
        "upfrontdiscount": "FLOAT",
        "totalpremium": "FLOAT",
        "discountcode": "STRING",
        "absorbinterest": "STRING",
        "installmentperiod": "INTEGER",
        "installmenttype": "STRING",
        "installmentrate": "FLOAT",
        "age": "INTEGER",
        "applicationformcode": "STRING",
        "province": "STRING",
        "district": "STRING",
        "subdistrict": "STRING",
        "addresstype": "STRING",
        "payment_year": "INTEGER",
        "payment_month": "INTEGER",
        "payment_day": "INTEGER",
        "payment_timestamp": "TIMESTAMP",
        "payment_yearmonth": "STRING",
        "payment_hour": "INTEGER",
        "payment_weekday": "STRING",
        "campaign_name": "STRING",
        "campaign_start_date_sitecore": "DATE",
        "campaign_end_date_sitecore": "DATE",
        "facet1_medium": "STRING",
        "facet2_traffic_src": "STRING",
        "facet4_product_type": "STRING",
        "facet5_objectives": "STRING",
        "campaign_channel": "STRING",
        "campaign_group": "STRING",
        "campaign_id_from_sitecore": "STRING",
        "lat": "FLOAT",
        "long": "FLOAT",
        "province_eng": "STRING",
        "payment_date": "DATE",
        "producttype_group": "INTEGER",
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
