import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

SNOWFLAKE_ACCOUNT_ID = os.getenv("SNOWFLAKE_ACCOUNT_ID")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PRIVATE_KEY_PATH = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")

conn = snowflake.connector.connect(
    account=SNOWFLAKE_ACCOUNT_ID,
    user=SNOWFLAKE_USER,
    private_key_file=SNOWFLAKE_PRIVATE_KEY_PATH,
    warehouse="compute_wh",
    database="stock_pipeline",
    schema="public"
)

copy_sql = """
COPY INTO raw_stock_prices (symbol, file_name, raw_json)
FROM (SELECT
        REGEXP_SUBSTR(METADATA$FILENAME, '([A-Z]+)\\\\.json', 1, 1, 'e', 1) AS symbol,
        METADATA$FILENAME AS file_name,
        $1 AS raw_json
    FROM @stock_stage
)
PATTERN = '.*\\\\.json'
FILE_FORMAT = json_format
FORCE = TRUE;
"""

def run_copy():
    cur = conn.cursor()
    try:
        cur.execute(copy_sql)
        print(f"Copy complete: {cur.rowcount} rows affected")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_copy()