import psycopg2


def get_conn_pg(
    db_hostname_or_ip,
    db_port_number,
    db_database_name,
    db_username,
    db_password,
):
    conn = psycopg2.connect(
        database=db_database_name,
        user=db_username,
        password=db_password,
        host=db_hostname_or_ip,
        port=db_port_number,
        connect_timeout=5,
    )
    return conn
