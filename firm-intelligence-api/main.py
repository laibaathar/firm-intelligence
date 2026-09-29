from fastapi import FastAPI
from routers import firms, knowledge, people, reports, insights, agent
from contextlib import asynccontextmanager



app = FastAPI(title = "Firm Intelligence API")

app.include_router(firms.router)
app.include_router(people.router)
app.include_router(reports.router)
app.include_router(insights.router)
app.include_router(knowledge.router)
app.include_router(agent.router)


@app.get("/health")
def health():
    return {"status": "ok"}
