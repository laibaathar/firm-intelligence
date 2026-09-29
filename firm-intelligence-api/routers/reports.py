"""Reports API — handed over by a contractor. Not reviewed.

SYNTHETIC PLACEHOLDER DATA ONLY.
"""

#import time   #2nd fix: (1)import time remove commented

import asyncio  #2nd fix: (2)added this import
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from routers.firms import get_firm_or_404 # ya change kya ha

router = APIRouter(prefix="/reports", tags=["reports"])


REPORTS: list[dict[str, Any]] = [
    {"id": 1, "title": "UK Market Outlook", "firm_id": 1, "revisions": ["v1"]},
    {"id": 2, "title": "US Partner Compensation", "firm_id": 2, "revisions": ["v1"]},
]

_view_counts: dict[int, int] = {}


class NewReport(BaseModel):
    title: str = Field(min_length=1)
    firm_id: int


def get_report_or_404(report_id: int) -> dict:
    for report in REPORTS:
        if report["id"] == report_id:
            return report
    raise HTTPException(status_code=404, detail=f"No report with id {report_id}")


@router.get("")
def list_reports():
    return REPORTS


@router.get("/{report_id}")
async def get_report(report_id: int):
    report = get_report_or_404(report_id)
   # _view_counts[report_id] = _view_counts.get(report_id, 0) + 1   #3rd fix: (1) remove these both lines
   # return {**report, "views": _view_counts[report_id]}

    return {               # 3rd fix: added these two lines for the fix as previously it was increasing views on each api hit
        **report, "views": _view_counts.get(report_id, 0),}


@router.post("", status_code=201)
def create_report(new: NewReport):

    get_firm_or_404(new.firm_id)  #ya change kya ha


    new_id = max(report["id"] for report in REPORTS) + 1
    report = {
        "id": new_id,
        "title": new.title,
        "firm_id": new.firm_id,
        "revisions": ["v1"],
    }
    REPORTS.append(report)
    return report


@router.put("/{report_id}")
def update_report(report_id: int, new: NewReport):
    report = get_report_or_404(report_id)

    get_firm_or_404(new.firm_id) #yahan change kya ha

    report["title"] = new.title
    report["firm_id"] = new.firm_id
    report["revisions"].append(f"v{len(report['revisions']) + 1}")
    return report


@router.get("/{report_id}/export")
async def export_report(report_id: int):
    report = get_report_or_404(report_id)

    #time.sleep(3)   #2nd fix: (3) commented / remove time

    await asyncio.sleep(3) #2nd fix: (4)added await asynchronous call
    return {"id": report["id"], "title": report["title"], "format": "pdf"}


@router.delete("/{report_id}", status_code=204)
def delete_report(report_id: int):
    report = get_report_or_404(report_id)
    REPORTS.remove(report)
    return
