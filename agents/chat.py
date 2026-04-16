import asyncio
from dotenv import load_dotenv
from agents import Runner

from conversational_agent import supervisor_agent

load_dotenv()


async def main():
    print("Saxbys conversational agent")
    print("Type 'exit' to quit.\n")

    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        if not history:
            run_input = user_input
        else:
            run_input = history + [{"role": "user", "content": user_input}]

        result = await Runner.run(supervisor_agent, run_input)

        history = result.to_input_list()

        print(f"\nAgent: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(main())