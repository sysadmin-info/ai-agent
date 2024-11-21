import logging
from quart import Quart, request, jsonify
from lib.prompts import Prompts
from lib.ai import AnthropicCompletion
from typing import Dict, Any
from dotenv import load_dotenv
import os
import json
import datetime

# Załaduj zmienne środowiskowe
load_dotenv()

# Inicjalizacja aplikacji Quart
app = Quart(__name__)

# Konfiguracja loggera
class SensitiveDataFilter(logging.Filter):
    """
    Filtr logowania do ukrywania danych wrażliwych, takich jak klucz API.
    """
    def filter(self, record):
        if record.msg and isinstance(record.msg, str):
            record.msg = record.msg.replace(os.getenv("ANTHROPIC_API_KEY", ""), "[REDACTED]")
        return True

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AIAgentLogger")
logger.addFilter(SensitiveDataFilter())


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
            "actionsTaken": [],
            "activeTool": {},
            "api_key": api_key
        }

    def _sanitize_state(self) -> Dict[str, Any]:
        """
        Usuwa wrażliwe dane (np. klucz API) przed logowaniem.
        """
        return {k: v for k, v in self.state.items() if k != "api_key"}

    async def final_answer(self) -> str:
        self.state["systemPrompt"] = Prompts.final_answer_prompt(self.state)
        messages = [{"role": "user", "content": self.state["systemPrompt"]}]
        logger.debug(f"Sending final_answer request: {messages}")
        answer = await self.completion_client.completion(messages)
        parsed_answer = self._parse_response(answer, step="final_answer")
        self._log_to_markdown("result", "Final Answer", json.dumps(parsed_answer))
        return parsed_answer

    async def run(self, initial_message: str) -> str:
        self.state["messages"] = [{"role": "user", "content": initial_message}]
        logger.debug(f"Initial state: {self._sanitize_state()}")

        while self.state["currentStep"] <= self.state["maxSteps"]:
            try:
                self._log_request_start("plan")
                await self._plan()
                self._log_request_end("plan")

                self._log_request_start("decide")
                await self._decide()
                self._log_request_end("decide")

                if not self.state.get("activeTool", {}).get("tool"):
                    raise ValueError("Active tool is not defined or missing the 'tool' property in state.")

                if self.state["activeTool"]["tool"] == "final_answer":
                    return await self.final_answer()

                self._log_request_start("describe")
                await self._describe()
                self._log_request_end("describe")

                self._log_request_start("execute")
                await self._execute()
                self._log_request_end("execute")

                self._log_request_start("reflect")
                await self._reflect()
                self._log_request_end("reflect")

                self.state["currentStep"] += 1
            except Exception as e:
                logger.error(f"Error during step {self.state['currentStage']}: {str(e)}")
                raise

    async def _plan(self):
        self.state["currentStage"] = "plan"
        self.state["systemPrompt"] = Prompts.plan_prompt(self.state)
        messages = [{"role": "user", "content": self.state["systemPrompt"]}]
        logger.debug(f"Plan request payload: {messages}")
        plan_response = await self.completion_client.completion(messages)
        self.state["plan"] = self._parse_response(plan_response, step="plan")

    async def _decide(self):
        self.state["currentStage"] = "decide"
        self.state["systemPrompt"] = Prompts.decide_prompt(self.state)
        messages = [{"role": "user", "content": self.state["systemPrompt"]}]
        logger.debug(f"Decide request payload: {messages}")
        decision_response = await self.completion_client.completion(messages)
        try:
            self.state["activeTool"] = json.loads(self._parse_response(decision_response, step="decide"))
            logger.debug(f"Active tool decided: {self.state['activeTool']}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse decision JSON: {decision_response}")
            raise ValueError(f"Error parsing decision JSON: {decision_response}") from e

    async def _describe(self):
        self.state["currentStage"] = "describe"
        if not self.state.get("activeTool", {}).get("tool"):
            raise ValueError("Active tool is not defined or missing the 'tool' property in state.")

        self.state["systemPrompt"] = Prompts.describe_prompt(self.state)
        messages = [{"role": "user", "content": self.state["systemPrompt"]}]
        logger.debug(f"Describe request payload: {messages}")
        describe_response = await self.completion_client.completion(messages)
        self.state["activeToolPayload"] = self._parse_response(describe_response, step="describe")

    async def _execute(self):
        self.state["currentStage"] = "execute"
        tool_name = self.state["activeTool"]["tool"]
        payload = self.state["activeToolPayload"]
        logger.debug(f"Executing tool: {tool_name} with payload: {payload}")
        result = f"Executed {tool_name} with payload {payload}"
        self.state["actionsTaken"].append({
            "name": tool_name,
            "payload": payload,
            "result": result,
            "reflection": ""
        })

    async def _reflect(self):
        self.state["currentStage"] = "reflect"
        self.state["systemPrompt"] = Prompts.reflection_prompt(self.state)
        messages = [{"role": "user", "content": self.state["systemPrompt"]}]
        logger.debug(f"Reflect request payload: {messages}")
        reflection_response = await self.completion_client.completion(messages)
        self.state["actionsTaken"][-1]["reflection"] = self._parse_response(reflection_response, step="reflect")

    def _parse_response(self, response: Dict[str, Any], step: str) -> str:
        logger.debug(f"Raw response for step {step}: {response}")
        try:
            if "completion" in response:
                return response["completion"]
            elif "content" in response:
                content_list = response.get("content", [])
                if content_list:
                    return content_list[0].get("text", "")
            raise ValueError("Invalid response format")
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            raise ValueError(f"Error parsing API response for step {step}: {response}")

    def _log_request_start(self, step):
        logger.debug(f"Step '{step}' started at {datetime.datetime.now()}")

    def _log_request_end(self, step):
        logger.debug(f"Step '{step}' ended at {datetime.datetime.now()}")

    def _log_to_markdown(self, log_type: str, header: str, content: str):
        with open("log.md", "a") as f:
            f.write(f"## {header}\n\n{content}\n\n")


@app.route("/", methods=["POST"])
async def process_request():
    data = await request.get_json()
    initial_message = data.get("messages", "")

    logger.debug(f"Incoming message: {initial_message}")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("API key is missing in environment variables or .env file.")

    agent = AIAgent(api_key)

    try:
        result = await agent.run(initial_message)
        logger.debug(f"Final sanitized state: {agent._sanitize_state()}")
        return jsonify({"response": result})
    except Exception as e:
        logger.error(f"Exception during agent execution: {str(e)}")
        return jsonify({"error": str(e)}), 500

