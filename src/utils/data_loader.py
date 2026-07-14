import functools
from pathlib import Path
import pandas as pd

def get_data_path():
    root_dir = Path(__file__).resolve().parent.parent.parent
    return str(root_dir / "data" / "raw" / "ASK DATA - superstore_data.csv")

@functools.lru_cache(maxsize=1)
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        return df
    except Exception as error:
        print(f"Error loading data from {file_path}: {error}")
        return None
