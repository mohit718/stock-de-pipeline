import os
from dotenv import load_dotenv
import snowflake.connector

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

merge_sql = """
MERGE INTO marts.fct_daily_prices AS target
USING public.stg_daily_prices AS source
ON target.symbol = source.symbol
    AND target.trade_date = source.trade_date
WHEN NOT MATCHED THEN
    INSERT (symbol, trade_date, open, high, low, close, volume)
    VALUES (source.symbol, source.trade_date, source.open, source.high, source.low, source.close, source.volume)
WHEN MATCHED 
AND (target.close != source.close or target.volume != source.volume)
THEN
    UPDATE SET
        target.open = source.open,
        target.high = source.high,
        target.low = source.low,
        target.close = source.close,
        target.volume = source.volume,
        loaded_at = CURRENT_TIMESTAMP();
"""

def run_merge():
    cur = conn.cursor()
    try:
        cur.execute(merge_sql)
        print(f"Merge complete: {cur.rowcount} rows affected")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_merge()
