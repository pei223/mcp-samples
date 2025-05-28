# mcp_server.
from fastmcp import FastMCP

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
        }
    ]

@mcp.tool(name="enc", description="暗号化")
async def encrypt(enc_key: str, text: str) -> str:
    # でたらめな暗号化
    return enc_key[::-1]+text[::-1]
    

if __name__ == "__main__":
    mcp.run(transport="sse")
