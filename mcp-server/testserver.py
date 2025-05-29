# mcp_server.
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("demo")


# static resource
@mcp.resource("config://version")
def get_version():
    return "2.0.1"


# dynamic resource (dummy)
@mcp.resource("accountbanks://date/{date}")
def get_profile(date: str) -> list[dict]:
    return [
        {
            "date": "2025/05/28",
            "category": "food",
            "detail": "supermarket",
            "price": 2000,
        },
        {
            "date": "2025/05/21",
            "category": "food",
            "detail": "subscripion food service",
            "price": 15000,
        },
    ]


@mcp.tool(name="get_events_from_calender", description="レンダーから予定を取得する")
async def get_events_from_calender(
    from_date: Annotated[str, Field(description="取得したい予定の開始日")],
    to_date: Annotated[str, Field(description="取得したい予定の終了日")],
):
    # ダミーデータ
    return [
        {"date": "2025/05/25", "title": "打合せ"},
        {"date": "2025/05/28", "title": "歯医者"},
        {"date": "2025/05/30", "title": "一人で買い物"},
        {"date": "2025/05/31", "title": "飲み会"},
    ]


@mcp.tool(name="write_text_file", description="ファイルをテキストに保存")
async def write_text_file(
    file_name: Annotated[str, Field(description="保存ファイル名")],
    text: Annotated[str, Field(description="保存したいテキスト")],
):
    with open(file_name, mode="w", encoding="utf-8") as file:
        file.write(text)


@mcp.tool(name="enc", description="暗号化")
async def encrypt(enc_key: str, text: str) -> str:
    # でたらめな暗号化
    return enc_key[::-1] + text[::-1]


if __name__ == "__main__":
    mcp.run(transport="sse")
