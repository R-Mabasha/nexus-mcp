import asyncio
import logging
from src.server import server
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions

logging.basicConfig(
    level=logging.INFO, 
    filename="mcp-swarm.log", 
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="lightning-crew",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
