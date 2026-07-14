import sys
from pathlib import Path

# Append root directory to sys.path to allow importing from src
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from src.utils.data_loader import get_data_path, load_data

def print_general_information(df):
    print("\n--- General Data Information ---")
    print(df.info())

def print_descriptive_statistics(df):
    print("\n--- Descriptive Statistics ---")
    print(df.describe())

def analyze_business_metrics(df):
    print("\n--- Business Analysis ---")
    
    total_gmv = df['gmv'].sum()
    total_profit = df['profit'].sum()
    print(f"Total GMV: ${total_gmv:,.2f}")
    print(f"Total Profit: ${total_profit:,.2f}")
    
    print("\nTop 3 Categories by GMV:")
    print(df.groupby('category')['gmv'].sum().nlargest(3))
    
    print("\nTop 5 Sub-Categories by Profit:")
    print(df.groupby('sub_category')['profit'].sum().nlargest(5))
    
    print("\nTop Regions by Transaction Quantity:")
    print(df.groupby('region')['quantity'].sum().nlargest(3))
    
    print("\nGMV Contribution by Customer Segment:")
    print(df.groupby('segment')['gmv'].sum().sort_values(ascending=False))

def run_eda():
    data_path = get_data_path()
    df = load_data(data_path)
    
    if df is not None and not df.empty:
        print_general_information(df)
        print_descriptive_statistics(df)
        analyze_business_metrics(df)
    else:
        print("Failed to run EDA due to data loading issues.")

if __name__ == "__main__":
    run_eda()
