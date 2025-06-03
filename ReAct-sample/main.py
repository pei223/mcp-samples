import asyncio
import json
import os
from typing import Literal
from openai import OpenAI
from fastmcp import Client
from fastmcp.tools import Tool

_ACTION_ERROR_TYPE = Literal["action_not_found", "invalid_action"]


class InvalidActionError(RuntimeError):
    def __init__(self, message, err_type: _ACTION_ERROR_TYPE):
        super().__init__(message)
        self.err_type = err_type


introduction_prompt_template = """
以下の質問にできるだけ正確に答えてください。
質問:
{question}

---
以下のツールの使用ができます。

{tools}

以下の形式でやり取りします。
以下の形式を厳守してください。

Question: 回答してほしい質問
Thought: 次に何をするべきか考える。
Action: アクション実行を要求する。いずれかのツール名を指定。
Action Input: アクションに指定するパラメータをjson形式で指定する。
Observation: ツールの実行を待機。
...(Though/Action/Observationを最終回答ができるまで繰り返します)
Thought: 最終回答ができるようになった。
Final Answer: 元の質問に対する最終回答を出力します。
"""


def arrange_for_prompt(tools: list[Tool]) -> str:
    result = []
    for tool in tools:
        result.append(
            f"""
ツール名: {tool.name}
説明: {tool.description}
入力スキーマ: {tool.model_dump()["inputSchema"]}
"""
        )
    return "\n".join(result)


def send(openai_client: OpenAI, messages: list) -> str:
    print(
        f"""input messages: 
-----------------------------------------------------------------------------------------
{json.dumps(messages, indent=2, ensure_ascii=False)}
-----------------------------------------------------------------------------------------


"""
    )
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    output = completion.choices[0].message.content
    print(
        f"""output: 
-----------------------------------------------------------------------------------------
{output}
-----------------------------------------------------------------------------------------


"""
    )
    return output  # type: ignore


def parse_action(content: str) -> tuple[str, dict]:
    action_name = None
    params = {}
    for line in content.split("\n"):
        if line.startswith("Action:"):
            action_name = line[len("Action:") :].strip()
            continue
        if line.startswith("Action Input:"):
            params = json.loads(line[len("Action Input:") :].strip())
            continue
    if action_name is None:
        raise InvalidActionError("action name is none", "action_not_found")
    print(
        f"""selected action
-----------------------------------------------------------------------------------------
name: {action_name}
params: 
{json.dumps(params, indent=2, ensure_ascii=False)}
-----------------------------------------------------------------------------------------

"""
    )
    return action_name, params


def parse_final_answer(content: str) -> str | None:
    for line in content.split("\n"):
        if line.startswith("Final Answer:"):
            print(
                f"""final answer detected
-----------------------------------------------------------------------------------------
{line}
-----------------------------------------------------------------------------------------

"""
            )
            return line[len("Final Answer:") :]
    return None


async def main():
    question = "5/20から5/31までの相手に連絡が必要そうな予定だけを要約して、テキストファイルに保存して"
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    async with Client("http://localhost:8000/sse") as client:
        tools = await client.list_tools()
        tools_description = arrange_for_prompt(tools)  # type: ignore

        introduction_prompt = introduction_prompt_template.format(
            question=question, tools=tools_description
        )
        messages = [
            {
                "role": "system",
                "content": introduction_prompt,
            }
        ]
        max_step = 3
        step = 0
        while True:
            content = send(
                openai_client,
                messages,
            )
            final_answer = parse_final_answer(content)
            if final_answer:
                print(f"\n\n\n最終出力: {final_answer}\n\n\n")
                break

            messages.append(
                {
                    "role": "assistant",
                    "content": content,
                }
            )
            action, params = parse_action(content)
            if next((t for t in tools if t.name == action), None) is None:
                raise InvalidActionError(
                    f"{action} is invalid tool name", "invalid_action"
                )
            tool_result = await client.call_tool(action, params)
            messages.append(
                {
                    "role": "system",
                    "content": f"{action}({params})の結果: {tool_result}",
                }
            )
            step += 1
            if max_step < step:
                break


if __name__ == "__main__":
    asyncio.run(main())
