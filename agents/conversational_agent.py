from pathlib import Path
from agents import Agent, function_tool

from preprocess_agent import preprocess
from dashboard_agent import create_dashboard

RAW_FILE = "data/raw/raw_transactions.csv"
PROCESSED_DIR = "data/processed"
DASHBOARD_FILE = "app/dashboard.py"


@function_tool
def preprocess_data(raw_file: str = RAW_FILE) -> str:
    """Preprocess the raw transaction CSV and create processed files."""
    outputs = preprocess(raw_file, output_dir=PROCESSED_DIR)
    return (
        "Preprocessing complete.\n"
        f"transaction={outputs['transaction']}\n"
        f"food={outputs['food']}\n"
        f"drink={outputs['drink']}\n"
        f"bakery={outputs['bakery']}"
    )


@function_tool
def validate_processed_files() -> str:
    """Validate that the processed CSV files exist."""
    required = [
        Path(f"{PROCESSED_DIR}/transaction.csv"),
        Path(f"{PROCESSED_DIR}/food.csv"),
        Path(f"{PROCESSED_DIR}/drink.csv"),
        Path(f"{PROCESSED_DIR}/bakery.csv"),
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        return "Processed file validation failed. Missing: " + ", ".join(missing)
    return "Processed file validation passed."


@function_tool
def build_dashboard() -> str:
    """Generate the Streamlit dashboard file."""
    path = create_dashboard(DASHBOARD_FILE)
    return f"Dashboard created at {path}"


@function_tool
def validate_dashboard() -> str:
    """Validate that the Streamlit dashboard file exists and looks correct."""
    p = Path(DASHBOARD_FILE)
    if not p.exists():
        return f"Dashboard validation failed. Missing file: {DASHBOARD_FILE}"
    text = p.read_text(encoding="utf-8")
    if "streamlit" not in text.lower():
        return "Dashboard validation failed. File does not appear to contain Streamlit code."
    return "Dashboard validation passed."


@function_tool
def workflow_status() -> str:
    """Report current workflow status."""
    processed = {
        "transaction": Path(f"{PROCESSED_DIR}/transaction.csv").exists(),
        "food": Path(f"{PROCESSED_DIR}/food.csv").exists(),
        "drink": Path(f"{PROCESSED_DIR}/drink.csv").exists(),
        "bakery": Path(f"{PROCESSED_DIR}/bakery.csv").exists(),
    }
    dashboard_exists = Path(DASHBOARD_FILE).exists()

    return (
        "Current workflow status:\n"
        f"processed_files={processed}\n"
        f"dashboard_exists={dashboard_exists}\n"
        f"raw_file={RAW_FILE}"
    )


preprocess_specialist = Agent(
    name="Preprocessing Specialist",
    model="gpt-5.4",
    instructions=(
        "You handle data preprocessing tasks only. "
        "Use preprocessing and validation tools when the user asks about raw data, "
        "processed files, or preparing the dataset."
    ),
    tools=[preprocess_data, validate_processed_files],
)

dashboard_specialist = Agent(
    name="Dashboard Specialist",
    model="gpt-5.4",
    instructions=(
        "You handle dashboard generation tasks only. "
        "Use dashboard build and validation tools when the user asks to create or inspect the dashboard."
    ),
    tools=[build_dashboard, validate_dashboard],
)

# Manager-style orchestrator: keeps control of the conversation
supervisor_agent = Agent(
    name="Saxbys Workflow Assistant",
    model="gpt-5.4",
    instructions=(
        "You are a conversational workflow assistant for the Saxbys teaching repo. "
        "Help the user preprocess transaction data, generate the dashboard, validate outputs, "
        "and explain what happened. "
        "Be explicit about file paths and next steps. "
        "If the user asks to run the full pipeline, first preprocess and validate the processed files, "
        "then build and validate the dashboard."
    ),
    tools=[
        workflow_status,
        preprocess_specialist.as_tool(
            tool_name="run_preprocessing_specialist",
            tool_description="Use the preprocessing specialist for raw-data preparation and processed-file validation.",
        ),
        dashboard_specialist.as_tool(
            tool_name="run_dashboard_specialist",
            tool_description="Use the dashboard specialist for dashboard creation and dashboard validation.",
        ),
    ],
)