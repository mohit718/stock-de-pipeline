from dotenv import load_dotenv
import os
import requests
import boto3
from datetime import date
import json
import time

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

def fetch_ticker(symbol: str) -> dict:
    url = "https://www.alphavantage.co/query"
    params = {
        'function':'TIME_SERIES_DAILY',
        'symbol':symbol,
        'apikey':API_KEY
    }
    response = requests.get(url, params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Unexpected response for {symbol}: {data}")

    return data

def upload_raw(symbol: str, data: dict):
    s3 = boto3.client('s3')
    today = date.today().isoformat()
    key = f"raw/stocks/dt={today}/{symbol}.json"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(data, indent=2)
    )
    print(f"Uploaded {symbol} -> s3://{BUCKET_NAME}/{key}")

def save_local(symbol: str, data: dict):
    today = date.today().isoformat()
    path = f'data/raw/stocks/dt={today}'
    filename = f"{path}/{symbol}.json"
    
    os.makedirs(path, exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    for symbol in TICKERS:
        try:
            data = fetch_ticker(symbol)
            upload_raw(symbol, data)
            save_local(symbol, data)
        except Exception as ex:
            print(f'Unable to process {symbol}:{ex}')
        finally:
            time.sleep(3)
    
if __name__ == '__main__':
    main()