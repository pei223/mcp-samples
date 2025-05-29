import asyncio
import os
import pprint
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


def format(t):
    return pprint.pformat(t, indent=2)


# resource/tool/promptといったmcpサーバー情報を出力
async def log_mcp_server_info(client: Client, exclude_prompt=False):
    tools = await client.list_tools()
    print(f"Available tools: {format(tools)}\n\n")

    static_resources = await client.list_resource_templates()
    print(f"Available static resources: {format(static_resources)}\n\n")

    dynamic_resources = await client.list_resource_templates()
    print(f"Available dynamic resources: {format(dynamic_resources)}\\n")

    if not exclude_prompt:
        static_prompts = await client.list_prompts()
        print(f"Available static prompts: {format(static_prompts)}\n\n")

        dynamic_prompts = await client.list_prompts()
        print(f"Available dynamic prompts: {format(dynamic_prompts)}\\n")


async def main():
    # http経由で自前のmcp-serverへの接続
    async with Client("http://localhost:8000/sse") as client:
        await log_mcp_server_info(client)

        folder_result = await client.call_tool(
            "enc", {"enc_key": "test", "text": "text"}
        )
        print(f"Result: {folder_result}\n")

    # github-mcp-serverを試す
    async with Client(
        StdioTransport(
            # github-mcp-serverへのパス.
            # 実行ファイルを直接指定で起動&接続してくれる.
            "../../github-mcp-server/dist/github-mcp-server",
            ["stdio"],
            {
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ[
                    "GITHUB_PERSONAL_ACCESS_TOKEN"
                ]
            },
        )
    ) as client:
        await log_mcp_server_info(client, exclude_prompt=True)
        # resourceを試しに実行してみる
        folder_result = await client.read_resource(
            "repo://pei223/clean-news/refs/heads/main/contents/batch"
        )
        print(f"\n\nResource result(folder): {folder_result}\n\n")
        folder_result = await client.read_resource(
            "repo://pei223/clean-news/refs/heads/main/contents/batch/Makefile"
        )
        print(f"Resource result(file): {folder_result}\n\n")

        # toolを試しに実行してみる
        tool_result = await client.call_tool(
            "list_issues", {"owner": "pei223", "repo": "clean-news"}
        )
        print(f"Tool result: {tool_result}\n\n")


if __name__ == "__main__":
    asyncio.run(main())
