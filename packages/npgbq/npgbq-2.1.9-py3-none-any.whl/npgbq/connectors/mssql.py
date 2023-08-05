import pyodbc

def get_conn_mssql(
    db_hostname_or_ip,
    db_port_number,
    db_database_name,
    db_username,
    db_password,
):
    protocal = "tcp"
    driver = "ODBC Driver 17 for SQL Server"
    server_name = f"{protocal}:{db_hostname_or_ip},{db_port_number}"
    connection_string = f"DRIVER={driver};SERVER={server_name};DATABASE={db_database_name};UID={db_username};PWD={db_password};"
    conn = pyodbc.connect(connection_string)
    return conn