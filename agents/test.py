import csv
from pathlib import Path

path = Path("data/processed/transaction.csv")

with path.open(newline="") as f:
    reader = csv.reader(f)
    rows = list(reader)

num_rows = len(rows) - 1 if rows else 0  # subtract header row
num_columns = len(rows[0]) if rows else 0

print("rows:", num_rows)
print("columns:", num_columns)