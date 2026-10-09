from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from anthropic import APIStatusError, APITimeoutError, RateLimitError
import grounding

import knowledge_store as knowledge
import llm

#our relevance floor
#below this we treat the retrived context as not actually relevant
RELEVANCE_FLOOR = 0.35


router = APIRouter(prefix="/knowledge",tags=["knowledge"])


class Question(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=0, le=8)

@router.post("/index")
def rebuild_index():
    """Embed the corpus. costs tokens... so it is a deliberate POST,"""
    tokens = knowledge.build_index()
    return {"indexed": knowledge.count(), "embedding_tokens": tokens}

@router.post("/search")
def search_documents(q: Question):
    """Retrival only no generated text or model call etc ... only what was found"""
    try:
        return {"question": q.question, "results": knowledge.search(q.question,top_k=q.top_k )}
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

#function behaviour...
 #the refusal happens before the model is called, not after
 #why 200 and not a 404 for a refusal????
  # the request was valid....service handled it correctly and " we have no relevant doc is a real answer"
 # sources...
  #this makes our answer checkable....without it a client has an answer/ para that they have to trust.... with it they can open doc-004 and verify the claim themselves
  #504,429,502....never a abre 500
@router.post("/ask")
def ask(q: Question):
    """Retrieve, than answer using only what was retrived... or refuse"""
    #1. Retrieve
    #same call as /knowledge/search
    try:
        hits = knowledge.search(q.question, q.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


    #2. Filter, and decide whether to make a call to the model at all
    #(compare against our RELEVANCE_FLOOR)

    usable = [hit for hit in hits if hit["score"] >= RELEVANCE_FLOOR]

    if not usable:
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": "No document in the corpus is relevant to that question.",
            "sources": []
        }

    #3.  Build context, generate the answer

    context = "\n\n".join(f"[{h['id']}] {h['title']}\n{h['text']}"for h in usable)

    try:
        result = llm.answer_from_context(q.question, context)
    except APITimeoutError:
        raise HTTPException(status_code=504,detail="Answer provider timed out")

    except RateLimitError:
        raise HTTPException(status_code=429,detail=" Answer provider rate limit exceeded")

    #except APIStatusError:
       # raise HTTPException(status_code=502,detail="Answer provider unavaliable service error")"""
    
    except APIStatusError as e:
        print("ANTHROPIC ERROR:", e)
        raise HTTPException(status_code=502, detail=str(e))


    #4. Return the successful answer
    return {
        "question": q.question,
        "answer": result["answer"],
        "refused": False,
        "sources": [{"id": h["id"],"title": h["title"], "score": round(h["score"], 3)} for h in usable],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "stop_reason": result["stop_reason"],
        "grounding": grounding.check_citations(result["answer"], [h["id"] for h in usable])
    }