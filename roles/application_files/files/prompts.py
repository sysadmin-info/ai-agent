from typing import Dict

class Prompts:
    @staticmethod
    def tools_instruction() -> Dict[str, str]:
        return {
            "get_html_contents": (
                'Required payload: {"url": "URL that needs to be downloaded"} '
                'Response format: HTML content of the page.'
            ),
            "game_submit_form": (
                'Required payload: {"url": "URL to a file that will be passed to the game"}. '
                'Response format: The game\'s response after submitting the form.'
            ),
            "upload_text_file": (
                'Required payload: {"content": "Text content of the file", '
                '"file_name": "Name of the file (e.g., document.md)"} '
                'Response format: URL of the uploaded file.'
            ),
            "final_answer": (
                'Required payload: {"answer": "Your final answer"}. '
                'Response format: A direct response to the user.'
            ),
            "play_music": (
                'Required payload: JSON object with Spotify API details for actions like search, play, or playlist creation.'
            )
        }

    @staticmethod
    def available_tools() -> Dict[str, str]:
        return {
            "get_html_contents": "Fetch HTML content of a URL.",
            "upload_text_file": "Create and upload a text file.",
            "game_submit_form": "Submit a URL to the game.",
            "final_answer": "Provide the final response to the user.",
            "play_music": "Generate Spotify API JSON for playing or managing music."
        }

    @staticmethod
    def extract_user_query(state) -> str:
        try:
            return next(
                (msg["content"] for msg in state.get("messages", []) if msg.get("role") == "user"),
                "No specific query provided."
            )
        except Exception:
            return "No specific query provided."

    @staticmethod
    def plan_prompt(state) -> str:
        user_query = Prompts.extract_user_query(state)

        return f"""
<main_objective>
Analyze the user's query and decide whether to provide an immediate answer or develop a detailed plan.
</main_objective>

<rules>
- If the query is straightforward (e.g., "How far is the Moon from Earth?"), prioritize addressing it directly.
- If the query requires multiple steps, use available tools to create an actionable plan.
- Always respond with clarity and avoid unnecessary complexity.
</rules>

<user_query>
{user_query}
</user_query>

<available_tools>
{Prompts.tools_instruction()}
</available_tools>
"""

    @staticmethod
    def decide_prompt(state) -> str:
        user_query = Prompts.extract_user_query(state)

        return f"""
<main_objective>
Determine the next step based on the user's query and current context. Either select the appropriate tool to proceed or decide to provide the final answer.
</main_objective>

<rules>
- Be concise and provide a JSON response with the selected tool and reasoning.
- If the question is straightforward, move directly to the final answer.
- Always return a valid JSON string with the tool name.
- The JSON structure must include:
  {{
    "_thoughts": "Your internal reasoning",
    "tool": "precise name of the tool"
  }}
</rules>

<user_query>
{user_query}
</user_query>

<available_tools>
{Prompts.available_tools()}
</available_tools>

<current_plan>
Plan: {state['plan'] if state.get('plan') else 'No plan yet.'}
</current_plan>

<actions_taken>
{state['actionsTaken']}
</actions_taken>
"""

    @staticmethod
    def describe_prompt(state) -> str:
        if "activeTool" not in state or not state["activeTool"].get("tool"):
            raise ValueError("Active tool is not defined or missing the 'tool' property.")

        return f"""
<main_objective>
Provide the required details to execute the tool "{state['activeTool']['tool']}" based on the current state.
</main_objective>

<tool_details>
Tool Name: {state['activeTool']['tool']}
Tool Instructions: {state['activeTool'].get('instruction', 'No instructions available')}
</tool_details>

<actions_taken>
{state['actionsTaken']}
</actions_taken>
"""

    @staticmethod
    def reflection_prompt(state) -> str:
        return f"""
<main_objective>
Reflect on the last action performed and suggest improvements or adjustments to the plan if needed.
</main_objective>

<actions_taken>
{state['actionsTaken']}
</actions_taken>
"""

    @staticmethod
    def final_answer_prompt(state) -> str:
        user_query = Prompts.extract_user_query(state)

        return f"""
<main_objective>
Provide the final answer to the user's query: "{user_query}".
</main_objective>

<rules>
- Directly answer the user's question in a clear and actionable manner.
- If the query is unclear, ask for clarification.
- Summarize key findings and insights.
</rules>

<current_plan>
{state['plan'] if state.get('plan') else 'No plan created.'}
</current_plan>

<actions_taken>
{state['actionsTaken']}
</actions_taken>
"""

