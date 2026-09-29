from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, Depends, Header, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

import llm
from routers.firms import get_firm_or_404

from pydantic import BaseModel



router = APIRouter(prefix="/firms", tags=["insights"])







@router.post("/{firm_id}/summary")
def create_firm_summary(
    firm: dict = Depends(get_firm_or_404)
):
    try:
        return llm.summarise_firm(firm)

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out"
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="LLM rate limit exceeded"
        )

    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="LLM service error"
        )

    except Exception as e:
        print("ACTUAL LLM ERROR:", repr(e))
        raise HTTPException(
            status_code=502,
            detail="Failed to generate firm summary"
    )

@router.get("/{firm_id}/summary/estimate")
def estimate(firm: dict = Depends(get_firm_or_404)):
    return {
        "id": firm["id"],
        "estimated_input_tokens": llm.estimate_input_token(firm),
        "model": llm.MODEL,
    }

@router.get("/{firm_id}/summary/stream")
def stream_summary(firm: dict = Depends(get_firm_or_404)):
    return StreamingResponse(
        llm.stream_firm_summary(firm),
        media_type="text/plain",
        
    )

@router.post("/{firm_id}/analysis")
def create_firm_analysis(firm: dict = Depends(get_firm_or_404)):
    try:
        return llm.analyse_firm(firm)

    except APITimeoutError:
        raise HTTPException(status_code=504,detail="Analysis provider timed out")

    except RateLimitError:
        raise HTTPException(status_code=429,detail="Analysis provider rate limit exceeded")

    except APIStatusError:
        raise HTTPException(status_code=502,detail="Analysis provider unavaliable service error")

    except Exception as e:
        print("ACTUAL LLM ERROR:", repr(e))
        raise HTTPException(status_code=502,detail="Failed to analyse firm")




