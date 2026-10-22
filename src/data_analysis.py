
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

project_root = Path(__file__).resolve().parent.parent
data_path = project_root / "data" / "ai4i2020.csv"

df = pd.read_csv(data_path)

print("--- Summary Statistics ---")
print(df.describe())

print("\n--- Machine Types ---")
print(df["Type"].value_counts())

print("\n--- Failure Rate ---")
print(df["Machine failure"].value_counts(normalize=True) * 100)

plt.figure(figsize=(7, 4))
sns.countplot(data=df, x="Machine failure")
plt.title("Machine Failure Distribution")
plt.xlabel("Machine Failure (0 = No, 1 = Yes)")
plt.ylabel("Number of Records")
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))
sns.histplot(
    data=df,
    x="Rotational speed [rpm]",
    hue="Machine failure",
    bins=30,
    element="step"
)
plt.title("Rotational Speed vs Machine Failure")
plt.tight_layout()
plt.show()
