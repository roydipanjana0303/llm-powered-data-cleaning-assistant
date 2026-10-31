
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "backend" / "mcp_server" / "server.py"


async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER)]
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("MCP CONNECTED")
            print("Registered tools:", [tool.name for tool in tools.tools])

            tests = [
                ("detect_missing_values", {}),
                ("detect_duplicates", {}),
                ("summarize_column", {"column_name": "MonthlyCharges"}),
            ]

            for tool_name, arguments in tests:
                print(f"\n--- Testing {tool_name} ---")
                result = await session.call_tool(tool_name, arguments)

                for item in result.content:
                    if hasattr(item, "text"):
                        print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
