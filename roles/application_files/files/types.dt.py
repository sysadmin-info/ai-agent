from typing import List, Optional, TypedDict, Literal, Any

# Define the stages that the agent can go through
Stage = Literal['init', 'plan', 'decide', 'describe', 'reflect', 'execute', 'final']

class ITool(TypedDict):
    """
    Represents a tool that the AI agent can use, with a name, instruction, and description.
    """
    name: str
    instruction: str
    description: str

class IAction(TypedDict):
    """
    Represents an action taken by the AI agent, with fields for the action name, payload, result, reflection, and the tool used.
    """
    name: str
    payload: str
    result: str
    reflection: str
    tool: str

class IState(TypedDict, total=False):
    """
    Represents the state of the AI agent, including system prompts, messages, the current stage and step,
    and actions taken so far.
    """
    systemPrompt: str                      # Current system prompt
    messages: List[dict]                   # All messages in the conversation
    currentStage: Stage                    # Stage on which the system prompt depends
    currentStep: int                       # Current step in the agent's operation
    maxSteps: int                          # Maximum number of steps allowed
    activeTool: Optional[ITool]            # The tool currently being used by the agent
    activeToolPayload: Optional[Any]       # Payload for the active tool
    plan: str                              # Current plan of action
    actionsTaken: List[IAction]            # List of actions taken so far
