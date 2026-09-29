# Import FastAPI tools for creating routes and handling errors
from fastapi import APIRouter, HTTPException

# Import Pydantic tools for checking/validating user input
from pydantic import BaseModel, Field

# Import Anthropic so we can handle its specific errors
import anthropic

# Import our agent logic
import agent


# Create a router for all agent-related endpoints
# This means our URLs will start with /agent
router = APIRouter(prefix="/agent", tags=["agent"])


# This defines what the user must send
class AgentQuestion(BaseModel):
    # The question must be a string and cannot be empty
    question: str = Field(min_length=1)


# Create a POST endpoint: /agent/ask
@router.post("/ask")
def ask_agent(request: AgentQuestion):

    try:
        # Send the user's question to the agent
        # The agent handles the LLM and tool-use loop
        return agent.ask_with_tools(request.question)

    # If the AI provider takes too long
    except anthropic.APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="AI provider timed out"
        )

    # If we hit the AI provider's rate limit
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="AI provider rate limit reached"
        )

    # If the AI provider is unavailable or has another API error
    except anthropic.APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="AI provider is unavailable"
        )

    # Catch any other unexpected error
    # This prevents the error from escaping as a bare 500
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Agent request failed"
        )