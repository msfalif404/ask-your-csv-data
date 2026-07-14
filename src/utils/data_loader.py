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
        if 'ship_date' in df.columns:
            df['ship_date'] = pd.to_datetime(df['ship_date'], errors='coerce')
            
        # Materialize derived metrics
        if 'profit' in df.columns and 'gmv' in df.columns:
            df['profit_margin'] = (df['profit'] / df['gmv']) * 100
            df['profit_margin'] = df['profit_margin'].fillna(0)
            df['is_profitable'] = df['profit'].apply(lambda x: 'Untung' if x > 0 else 'Rugi')
            
        if 'gmv' in df.columns and 'quantity' in df.columns:
            df['unit_price'] = df['gmv'] / df['quantity']
            
        if 'order_date' in df.columns and 'ship_date' in df.columns:
            df['shipping_days'] = (df['ship_date'] - df['order_date']).dt.days
            
        if 'order_date' in df.columns:
            df['order_year'] = df['order_date'].dt.year
            df['order_month'] = df['order_date'].dt.month_name()
            
        return df
    except Exception as error:
        print(f"Error loading data from {file_path}: {error}")
        return None
