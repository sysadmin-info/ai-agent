import json
from lib.tools import browse, upload_file, play_music
from lib.prompts import Prompts
from lib.ai import AnthropicCompletion  # Use the AnthropicCompletion class
from typing import Dict, Any

def log_to_markdown(type: str, header: str, content: str):
    """
    Logs content to a markdown file.

    Parameters:
    - type (str): The type of log entry (e.g., 'basic', 'action', 'result').
    - header (str): The header of the log entry.
    - content (str): The content to log.
    """
    formatted_content = f"## {header}\n\n{content}\n\n" if type == "basic" else \
                        f"### {header}\n\n{content}\n\n" if type == "action" else \
                        f"#### {header}\n```\n{content}\n```\n\n"

    with open("log.md", "a") as f:
        f.write(formatted_content)

async def plan(state, anthropic_completion):
    """
    Generates a plan based on the current state.
    """
    state["currentStage"] = "plan"
    state["systemPrompt"] = Prompts.plan_prompt(state)
    state["plan"] = await anthropic_completion.completion(state["systemPrompt"])
    log_to_markdown("basic", "Planning", f"Current plan: {state['plan']}")

async def decide(state, anthropic_completion):
    """
    Decides the next tool to use based on the current state.
    """
    state["currentStage"] = "decide"
    state["systemPrompt"] = Prompts.decide_prompt(state)
    next_step = await anthropic_completion.completion(state["systemPrompt"])
    state["activeTool"] = {
        "name": next_step["tool"],
        "description": Prompts.available_tools().get(next_step["tool"]),
        "instruction": Prompts.tools_instruction().get(next_step["tool"])
    }
    log_to_markdown("action", "Decision", f"Next move: {json.dumps(next_step)}")

async def describe(state, anthropic_completion):
    """
    Generates a payload description for the active tool.
    """
    state["currentStage"] = "describe"
    state["systemPrompt"] = Prompts.describe_prompt(state)
    next_step = await anthropic_completion.completion(state["systemPrompt"])
    state["activeToolPayload"] = next_step
    log_to_markdown("action", "Description", f"Next step description: {json.dumps(next_step)}")

async def execute(state):
    """
    Asynchronously executes the active tool with the generated payload.
    """
    state["currentStage"] = "execute"
    if not state.get("activeTool"):
        raise ValueError("No active tool to execute")

    tool_name = state["activeTool"]["name"]
    payload = state.get("activeToolPayload", {})

    if tool_name == "get_html_contents":
        result = await browse(payload["url"])  # Async call to browse
    elif tool_name == "upload_text_file":
        result = await upload_file(payload)  # Async call to upload_file
    elif tool_name == "play_music":
        result = await play_music(payload)  # Async call to play_music
    else:
        result = f"Tool '{tool_name}' execution not defined."

    log_to_markdown("result", "Execution", f"Action result: {json.dumps(result)}")
    state["actionsTaken"].append({
        "name": tool_name,
        "payload": json.dumps(payload),
        "result": result,
        "reflection": ""
    })

async def reflect(state, anthropic_completion):
    """
    Reflects on the results of the last action.
    """
    state["currentStage"] = "reflect"
    state["systemPrompt"] = Prompts.reflection_prompt(state)
    reflection = await anthropic_completion.completion(state["systemPrompt"])
    state["actionsTaken"][-1]["reflection"] = reflection
    log_to_markdown("basic", "Reflection", reflection)

class AIAgent:
    def __init__(self, api_key: str):
        self.completion_client = AnthropicCompletion(api_key)
        self.state = {
            "currentStage": "init",
            "currentStep": 1,
            "maxSteps": 15,
            "messages": [],
            "systemPrompt": "",
            "plan": "",
            "actionsTaken": []
        }

    async def final_answer(self) -> str:
        """
        Generates the final answer based on the entire process.
        """
        self.state["systemPrompt"] = Prompts.final_answer_prompt(self.state)
        answer = await self.completion_client.completion(self.state["systemPrompt"])
        log_to_markdown("result", "Final Answer", json.dumps(answer))
        return answer

    async def run(self, initial_message: Dict[str, Any]) -> str:
        """
        Executes the agent's full process from planning to providing the final answer.

        Parameters:
        - initial_message (Dict[str, Any]): The initial message or prompt for the agent.

        Returns:
        - str: The final answer.
        """
        self.state["messages"] = [initial_message]

        while self.state["currentStep"] <= self.state["maxSteps"]:
            await plan(self.state, self.completion_client)
            await decide(self.state, self.completion_client)

            if self.state.get("activeTool", {}).get("name") == "final_answer":
                break

            await describe(self.state, self.completion_client)
            await execute(self.state)
            await reflect(self.state, self.completion_client)
            self.state["currentStep"] += 1

        return await self.final_answer()

