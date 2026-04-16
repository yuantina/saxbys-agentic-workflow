# agents/preprocess_agent.py

import pandas as pd
from pathlib import Path


def extract_unique_items(series):
    items = set()

    for val in series.dropna():
        parts = str(val).split(";")
        for p in parts:
            clean = p.strip()

            # Remove unwanted values
            if clean and clean.lower() != "none for today":
                items.add(clean)

    return sorted(items)


def preprocess(raw_path, output_dir="data/processed"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_path)

    # --- Create category files ---
    food_items = extract_unique_items(df["Food"])
    drink_items = extract_unique_items(df["Drink"])
    bakery_items = extract_unique_items(df["Bakery"])

    pd.DataFrame({"Item": food_items}).to_csv(out / "food.csv", index=False)
    pd.DataFrame({"Item": drink_items}).to_csv(out / "drink.csv", index=False)
    pd.DataFrame({"Item": bakery_items}).to_csv(out / "bakery.csv", index=False)

    # --- Convert to binary transaction format ---
    all_items = sorted(set(food_items + drink_items + bakery_items))

    rows = []

    for _, row in df.iterrows():
        transaction = {
            "Year": row["Year"],
            "Weekday": row["Weekday"],
            "Customer": row["Customer"],
        }

        # initialize all items as 0
        for item in all_items:
            transaction[item] = 0

        # fill purchased items
        for col in ["Food", "Drink", "Bakery"]:
            if pd.notna(row[col]):
                for item in str(row[col]).split(";"):
                    item = item.strip()

                    if item and item.lower() != "none for today":
                        transaction[item] = 1

        rows.append(transaction)

    transaction_df = pd.DataFrame(rows)
    transaction_df.to_csv(out / "transaction.csv", index=False)

    return {
        "transaction": str(out / "transaction.csv"),
        "food": str(out / "food.csv"),
        "drink": str(out / "drink.csv"),
        "bakery": str(out / "bakery.csv"),
    }


if __name__ == "__main__":
    paths = preprocess("data/raw/raw_transactions.csv")
    print(paths)