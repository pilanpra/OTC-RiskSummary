import pandas as pd
import json

# === Step 1: Load the trade data ===
trades_path = "simulated_otc_trades.csv"  # Update if your file path is different
df_trades = pd.read_csv('/Users/prasadpilankar/Documents/BAN/DE2025/OTC-Citi/simulated_otc_trades.csv')

# === Step 2: Load the scenario JSON ===
scenarios_path = "/Users/prasadpilankar/Documents/BAN/DE2025/OTC-Citi/scenarios.json"  # Update if your file path is different
with open(scenarios_path, 'r') as f:
    scenario_data = json.load(f)

# === Step 3: Define the PSE calculation function ===
def calculate_pse(row, factor):
    return row['notional'] * row['rate'] * (1 + row['volatility']) * factor

# === Step 4: Apply the function for each scenario and create new columns ===
for scenario_name, scenario_info in scenario_data["scenarios"].items():
    factor = scenario_info["factor"]
    col_name = f'pse_{scenario_name.replace(" ", "_").lower()}'
    df_trades[col_name] = df_trades.apply(lambda row: calculate_pse(row, factor), axis=1)

# === Step 5: Save the updated DataFrame ===
output_path = "simulated_otc_trades_with_pse.csv"
df_trades.to_csv(output_path, index=False)

print("✅ PSE calculations complete! File saved as:", output_path)
