from fastapi import APIRouter, Depends, Header, FastAPI, HTTPException
from data import FIRMS
from pydantic import BaseModel, Field

router = APIRouter(prefix="/firms", tags=["firms"])

_seen_keys: dict[str, dict] = {}

def get_firm_or_404(firm_id: int) -> dict:
    for firm in FIRMS:
            if firm["id"]== firm_id:
                return firm
    raise HTTPException(status_code = 404, detail = f"No firm with id {firm_id}")

#everything so far is read only .. now somebody sends you data and you have no idea what it is
# 1.first, we need to describe what you will accept (shape)

class NewFirm(BaseModel):
    #name, jurisdiction, revenue_usd_m, lawyers, equity_partners
    name: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=2, max_length=5)
    revenue_usd_m: float = Field(gt=0)
    lawyers:  int = Field(gt=0)
    equity_partners: int = Field(gt=0)
#a parameter annoted with a pydantic model means body
#a plain int or str means a url or query parameter




#@app.get("/firms")
#def list_firms():
   # return FIRMS

@router.get("")
def list_firms(
    jurisdiction: str | None = None,
    lawyers: int | None = None
):
    results = FIRMS

    if jurisdiction:
        results = [
            firm for firm in results
            if firm["jurisdiction"] == jurisdiction
        ]

    if lawyers:
        results = [
            firm for firm in results
            if firm["lawyers"] == lawyers
        ]
    if (jurisdiction or lawyers is not None) and not results:
        raise HTTPException(
            status_code=404,
            detail="No firms found matching the filters"
        )
    return results

#get one firm
#someone asks for firm 999
#return a 404

#@app.get("/firms/{firm_id}")
#def get_firm(firm_id: int):
    for firm in FIRMS:
        if firm["id"]== firm_id:
            return firm
        raise HTTPException(status_code = 404, detail = f"No firm with id {firm_id}")


#Refactored version of above function
@router.get("/{firm_id}")
def get_firm(firm: dict = Depends(get_firm_or_404)):
    return firm

#compute revenue per is total revenue divided by fee-earner headcount
 #profit per equity partner assumes a 35% margin, then divides by the number of equity
 #both are pretty standard law firm benchmarks... the kind of things Centellic platforms provide

#@app.get("/firms/{firm_id}/benchmarks")
#def get_benchmarks(firm_id: int):
    for firm in FIRMS:
        if firm["id"] == firm_id:
            revenue = firm["revenue_usd_m"]
            return {
                #id
                "id":firm["id"],
                #name
                "name":firm["name"],
                #rev per lawyer
                "revenue_per_lawyer_usd": round(revenue * 1_000_000 / firm["lawyers"]),
                #profit per ep
                "profit_per_equity+partner": round(revenue * 1_000_000 * 0.35 / firm["equity_partners"]),
                }
        raise HTTPException(status_code = 404, detail = f"No firm with id {firm_id}")
    
#Refactored version of above function
@router.get("/{firm_id}/benchmarks")
def get_benchmarks(firm: dict = Depends(get_firm_or_404)):

    revenue = firm["revenue_usd_m"]

    return {
        "id": firm["id"],
        "name": firm["name"],
        "revenue_per_lawyer_usd": round(
            revenue * 1_000_000 / firm["lawyers"]
        ),
        "profit_per_equity+partner": round(
            revenue * 1_000_000 * 0.35 / firm["equity_partners"]
        ),
    }

#Output
# 200 {"id":2,"name":"Marchetti Ruiz","revenue_per_lawyer_usd":1241667,"profit_per_equity+partner":3067647}
# 404 {"detail":"No firm with id 20"}


#post
# /firms
#@router.post("", status_code=201)
#def add_firm(new: NewFirm):
    new_id = max(firm["id"] for firm in FIRMS) +1
    firm ={
        "id" : new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue_usd_m": new.revenue_usd_m,
        "lawyers":  new.lawyers,
        "equity_partners": new.equity_partners     
    }
    FIRMS.append(firm)
    return firm


@router.post("", status_code = 201)
def add_firm(new: NewFirm, idempotency_key: str | None = Header(default=None)):
    if idempotency_key is not None and idempotency_key in _seen_keys:
        return _seen_keys[idempotency_key]


    new_id = max(firm["id"] for firm in FIRMS) + 1
    firm = {
        "id": new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue_usd_m": new.revenue_usd_m,
        "lawyers": new.lawyers,
        "equity_partners": new.equity_partners
    }

    FIRMS.append(firm)

    if idempotency_key is not None:
        _seen_keys[idempotency_key] = firm
    return firm


@router.put("/{firm_id}")
def update_firm(
    updated_firm: NewFirm,
    firm: dict = Depends(get_firm_or_404)
):
    firm.update(updated_firm.model_dump())
    return firm

@router.delete("/{firm_id}", status_code=204)
def delete_firm(
    firm: dict = Depends(get_firm_or_404)
):
    FIRMS.remove(firm)
    return


