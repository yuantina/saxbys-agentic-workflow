from preprocess_agent import preprocess
from dashboard_agent import create_dashboard
import subprocess

RAW_FILE = "data/raw/raw_transactions.csv"

def run_workflow():
    outputs = preprocess(RAW_FILE)
    print("Preprocessing outputs:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")

    dashboard_path = create_dashboard("app/dashboard.py")
    print(f"Dashboard created at: {dashboard_path}")

    print("Launching Streamlit...")
    subprocess.run(["streamlit", "run", dashboard_path])

if __name__ == "__main__":
    run_workflow()

