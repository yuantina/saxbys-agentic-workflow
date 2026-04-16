import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from agents import Agent, Runner, function_tool

from preprocess_agent import preprocess
from dashboard_agent import create_dashboard

load_dotenv()

print(os.getenv("OPENAI_API_KEY"))

RAW_FILE = "data/raw/raw_transactions.csv"
PROCESSED_DIR = "data/processed"
DASHBOARD_FILE = "app/dashboard.py"


@function_tool
def preprocess_tool(raw_file: str) -> str:
    """Run preprocessing on the raw transaction file and return a summary string."""
    outputs = preprocess(raw_file, output_dir=PROCESSED_DIR)
    return (
        "Preprocessing complete.\n"
        f"transaction={outputs['transaction']}\n"
        f"food={outputs['food']}\n"
        f"drink={outputs['drink']}\n"
        f"bakery={outputs['bakery']}"
    )


@function_tool
def validate_processed_tool() -> str:
    """Check that processed files exist and report status."""
    required = [
        Path(f"{PROCESSED_DIR}/transaction.csv"),
        Path(f"{PROCESSED_DIR}/food.csv"),
        Path(f"{PROCESSED_DIR}/drink.csv"),
        Path(f"{PROCESSED_DIR}/bakery.csv"),
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        return "Validation failed. Missing files: " + ", ".join(missing)
    return "Validation passed. All processed files exist."


@function_tool
def create_dashboard_tool() -> str:
    """Create the Streamlit dashboard file from processed data."""
    path = create_dashboard(DASHBOARD_FILE)
    return f"Dashboard created at {path}"


@function_tool
def validate_dashboard_tool() -> str:
    """Check that the dashboard file exists and looks like Streamlit code."""
    p = Path(DASHBOARD_FILE)
    if not p.exists():
        return f"Validation failed. Missing dashboard file: {DASHBOARD_FILE}"
    text = p.read_text(encoding="utf-8")
    if "streamlit" not in text.lower():
        return "Validation failed. dashboard.py does not appear to contain Streamlit code."
    return "Validation passed. dashboard.py exists and looks valid."


preprocess_agent = Agent(
    name="Preprocessing Agent",
    model="gpt-5.4",
    instructions=(
        "You are responsible for raw transaction preprocessing. "
        "Use the available tools to preprocess the raw file and validate the outputs. "
        "Report clear status."
    ),
    tools=[preprocess_tool, validate_processed_tool],
)

dashboard_agent = Agent(
    name="Dashboard Agent",
    model="gpt-5.4",
    instructions=(
        "You are responsible for dashboard generation. "
        "Use the available tools to create and validate the Streamlit dashboard. "
        "Report clear status."
    ),
    tools=[create_dashboard_tool, validate_dashboard_tool],
)

supervisor_agent = Agent(
    name="Workflow Supervisor",
    model="gpt-5.4",
    instructions=(
        "You supervise a two-agent workflow.\n"
        "Step 1: ask the preprocessing agent to preprocess the raw transaction file.\n"
        "Step 2: ensure processed file validation passes.\n"
        "Step 3: ask the dashboard agent to generate the dashboard.\n"
        "Step 4: ensure dashboard validation passes.\n"
        "If validation fails, explain what failed.\n"
        "Do not invent files; rely on tool results."
    ),
    handoffs=[preprocess_agent, dashboard_agent],
)


async def main():
    prompt = (
        f"Run the full workflow on raw file: {RAW_FILE}. "
        "Preprocess the data, validate the processed files, generate the dashboard, "
        "validate the dashboard, and summarize the final status."
    )
    result = await Runner.run(supervisor_agent, prompt)
    print(result.final_output)
    print("\nIf successful, run:\n  streamlit run app/dashboard.py")


if __name__ == "__main__":
    asyncio.run(main())