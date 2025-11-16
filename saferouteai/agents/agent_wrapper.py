"""Simple Agent wrapper for Google Generative AI models."""
from google.generativeai import GenerativeModel
from typing import List, Callable, Dict, Any, Optional
import inspect
import json


class Tool:
    """Tool wrapper for agent function calling."""
    
    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function
        
        # Extract function signature for tool definition
        sig = inspect.signature(function)
        self.parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation in (int, float):
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"
                elif param.annotation == dict or param.annotation == Dict:
                    param_type = "object"
            
            self.parameters["properties"][param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            
            if param.default == inspect.Parameter.empty:
                self.parameters["required"].append(param_name)


class Agent:
    """Simple Agent wrapper using GenerativeModel."""
    
    def __init__(self, model: GenerativeModel, instructions: str = "", tools: List[Tool] = None):
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
        
        # Convert tools to function calling format if available
        if self.tools and hasattr(self.model, 'generate_content'):
            # Store tool functions for manual calling
            self._tool_functions = {tool.name: tool.function for tool in self.tools}
    
    async def run(self, prompt: str) -> 'AgentResponse':
        """Run the agent with a prompt."""
        full_prompt = f"{self.instructions}\n\n{prompt}"
        
        try:
            # Use generate_content (synchronous but we're in async context)
            # In a full implementation, we'd use function calling here
            response = self.model.generate_content(full_prompt)
            text = response.text if hasattr(response, 'text') else str(response)
            return AgentResponse(text)
        except Exception as e:
            # Fallback to simple text response
            return AgentResponse(f"Error: {str(e)}")


class AgentResponse:
    """Response wrapper for agent output."""
    
    def __init__(self, text: str):
        self.text = text
    
    def __str__(self):
        return self.text

