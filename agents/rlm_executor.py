"""
RLM Safe Execution Wrapper for OpenCode Agents
Provides isolated, safe code execution for autonomous agents
"""

from rlm import RLM
from rlm.environments import LocalREPL, ModalREPL
from rlm.clients import OpenAIClient
from typing import Dict, Any
import os


class RLMExecutor:
    """
    Wraps agent code execution in RLM isolated environments.
    
    Usage:
        executor = RLMExecutor(environment="local")
        result = executor.execute_safely(code, context, lm_client)
    """
    
    def __init__(self, environment: str = "local"):
        """
        Args:
            environment: "local" (LocalREPL), "modal" (ModalREPL), 
                        "docker" (DockerREPL)
        """
        self.environment = environment
        self.env_map = {
            "local": LocalREPL,
            "modal": ModalREPL,
            # Add more as needed
        }
    
    def execute_safely(
        self, 
        code: str, 
        context: Dict[str, Any],
        lm_client
    ) -> Any:
        """
        Execute agent-generated code in isolated RLM environment.
        
        Args:
            code: Python code to execute
            context: Context payload (codebase info, task details, etc.)
            lm_client: LM client for llm_query() calls
            
        Returns:
            Execution result from RLM
        """
        # Create isolated environment
        repl_class = self.env_map.get(self.environment, LocalREPL)
        repl = repl_class()
        
        # Create RLM instance
        rlm = RLM(
            client=lm_client,
            repl=repl,
            system_prompt="Execute code safely in isolated environment"
        )
        
        # Load context
        repl.load_context(context)
        
        # Execute
        result = rlm.completion(
            prompt=code,
            context_payload=context
        )
        
        # Cleanup
        repl.cleanup()
        
        return result


# Example usage
if __name__ == "__main__":
    executor = RLMExecutor(environment="local")
    
    # Example code to execute
    code = """
import sys
print(f"Python version: {sys.version}")
print(f"Context: {context}")
"""
    
    # Execute safely
    result = executor.execute_safely(
        code=code,
        context={"task": "test", "codebase": {}},
        lm_client=OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
    )
    
    print(result)
