
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "ai4i2020.csv"

df = pd.read_csv(DATA_PATH)

print("\n--- Dataset Preview ---")
print(df.head())

print("\n--- Dataset Shape ---")
print(df.shape)

print("\n--- Column Names ---")
print(df.columns.tolist())

print("\n--- Missing Values ---")
print(df.isnull().sum())

print("\n--- Machine Failure Distribution ---")
print(df["Machine failure"].value_counts())
