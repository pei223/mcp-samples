import asyncio
from fastmcp import Client

async def log_mcp_server_info(client: Client):
    tools = await client.list_tools()
    print(f"Available tools: {tools}\n")
    
    static_resources = await client.list_resource_templates()
    print(f"Available static resources: {static_resources}\n")
    
    dynamic_resources = await client.list_resource_templates()
    print(f"Available dynamic resources: {dynamic_resources}\n")

    static_prompts = await client.list_prompts()
    print(f"Available static prompts: {static_prompts}\n")

    dynamic_prompts = await client.list_prompts()
    print(f"Available dynamic prompts: {dynamic_prompts}\n")


async def main():
    # Connect via stdio to a local script
    async with Client("http://localhost:8000/sse") as client:
        await log_mcp_server_info(client)

        result = await client.call_tool("enc", {"enc_key": "test", "text": "text"})
        print(f"Result: {result}\n")

if __name__ == "__main__":
    asyncio.run(main())
