import csv
import io
from datetime import datetime
import pytz
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
import oracledb
from msteams_alert import msteams_task_failure_alert  # import callback

# INIT Oracle client
oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_8")

# ----------------- CONFIG: ตารางที่ต้องการโหลด -----------------
TABLE_CONFIGS = [
    {
        "source_sql": "SELECT * FROM eis.PERSONEL_P_MAJOR_SPEC",
        "target_table": "staff.PERSONEL_P_MAJOR_SPEC",
        "mode": "replace"  # หรือ "append"
    },
    {
        "source_sql": "SELECT * FROM eis.PERSONEL_P_MAJOR_SPEC_GROUP",
        "target_table": "staff.PERSONEL_P_MAJOR_SPEC_GROUP",
        "mode": "replace"  # หรือ "append"
    },
    {
        "source_sql": "SELECT * FROM eis.PERSONEL_P_MAJOR_SPEC_SUB",
        "target_table": "staff.PERSONEL_P_MAJOR_SPEC_SUB",
        "mode": "replace"  # หรือ "append"
    },
    # เพิ่มตารางอื่นได้ที่นี่...
]
# ---------------------------------------------------------------

def remove_null_bytes(value):
    return value.replace('\x00', '') if isinstance(value, str) else value

def map_oracle_to_postgres_type(oracle_type):
    t = oracle_type.upper()
    if "CHAR" in t: return "TEXT"
    if "DATE" in t or "TIMESTAMP" in t: return "TIMESTAMP"
    if "NUMBER" in t or "DECIMAL" in t: return "NUMERIC"
    if "FLOAT" in t: return "FLOAT"
    if "LONG" in t: return "BIGINT"
    return "TEXT"

def create_postgres_table_if_not_exists(pg_hook, table_name, cursor_description):
    column_defs = []
    for col in cursor_description:
        col_name = col[0]
        ora_type = str(col[1])
        pg_type = map_oracle_to_postgres_type(ora_type)
        column_defs.append(f'"{col_name}" {pg_type}')
    column_defs.append('"date&time" TIMESTAMP')

    schema, table = table_name.split('.', 1)
    create_sql = f'CREATE TABLE IF NOT EXISTS "{schema}"."{table}" ({", ".join(column_defs)})'

    conn = pg_hook.get_conn()
    with conn.cursor() as cur:
        cur.execute(create_sql)
        conn.commit()

def extract_and_load_table(source_sql, target_table, mode='replace'):
    oracle_hook = OracleHook(oracle_conn_id='oracle_conn')
    postgres_hook = PostgresHook(postgres_conn_id='Postgres_HR')
    
    tz = pytz.timezone('Asia/Bangkok')
    load_time = datetime.now(tz)

    ora_conn = oracle_hook.get_conn()
    ora_cursor = ora_conn.cursor()
    ora_cursor.execute(source_sql)
    column_names = [desc[0] for desc in ora_cursor.description]
    column_names.append('date&time')

    # สร้างตารางปลายทาง
    create_postgres_table_if_not_exists(postgres_hook, target_table, ora_cursor.description)

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    row_count = 0
    for row in ora_cursor:
        cleaned = [remove_null_bytes(v) for v in row]
        cleaned.append(load_time)
        writer.writerow(cleaned)
        row_count += 1
    output.seek(0)

    pg_conn = postgres_hook.get_conn()
    pg_cursor = pg_conn.cursor()

    if mode == 'replace':
        schema, table = target_table.split('.', 1)
        pg_cursor.execute(f'TRUNCATE TABLE "{schema}"."{table}"')

    quoted_columns = ', '.join(f'"{col}"' for col in column_names)
    copy_sql = f'COPY "{schema}"."{table}" ({quoted_columns}) FROM STDIN WITH CSV'
    pg_cursor.copy_expert(sql=copy_sql, file=output)
    pg_conn.commit()

    ora_cursor.close()
    ora_conn.close()
    pg_cursor.close()
    pg_conn.close()

    print(f"[{target_table}] ✅ Loaded {row_count} rows at {load_time}, mode={mode}")


tz = pytz.timezone('Asia/Bangkok')
# ------------- Airflow DAG -------------
default_args = {
    'owner': 'nattapon',
    'start_date': datetime(2025, 7, 3, tzinfo=tz),  # เวลาเริ่มแบบไทย
    'depends_on_past': False,
}

with DAG(
    dag_id='ETL_or2pg_PERSONEL_P_MAJOR_SPEC',
    default_args=default_args,
    schedule_interval='0 2 1 * *',  # ✅ รันทุกวันที่ 1 ของเดือน ตี 2 (02:00)
    catchup=False,
    tags=['HR', 'oracle', 'postgres', 'etl'],
    on_failure_callback=msteams_task_failure_alert,  # ใช้งาน callback
) as dag:
    dag.doc_md = """
        # ---------------------------------------------------------------
        # 📦 ETL Script: Oracle → PostgreSQL with Airflow (PythonOperator)
        # ---------------------------------------------------------------
        # -✅ ทำหน้าที่ extract ข้อมูลจาก Oracle (ผ่าน OracleHook)
        # -✅ โหลดลง PostgreSQL (ผ่าน PostgresHook)
        # -✅ รองรับหลายตาราง: กำหนดได้ใน TABLE_CONFIGS
        # -✅ แปลงชนิดข้อมูล Oracle → PostgreSQL อัตโนมัติ
        # -✅ เพิ่มคอลัมน์ "date&time" สำหรับบันทึกเวลาโหลด
        # -✅ รองรับ mode: 'replace' (truncate ก่อนโหลดใหม่) หรือ 'append'
        # -✅ สร้างตารางปลายทางอัตโนมัติถ้ายังไม่มี
        # -✅ รันทุกวันที่ 1 ของเดือน ตี 2 (02:00) (Asia/Bangkok)
        # ---------------------------------------------------------------
    """


    for config in TABLE_CONFIGS:
        task = PythonOperator(
            task_id=f"load_{config['target_table'].replace('.', '_')}",
            python_callable=extract_and_load_table,
            op_args=[config['source_sql'], config['target_table'], config['mode']],
        )
        
