import logging
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pymongo import DESCENDING
from starlette import status
from starlette.requests import Request
from database.connection_pool import get_db_client, get_db_client_async
from models.Response import CaseSummaryResponse
from models.Summary import CaseData, CaseSummary
from background_workers.celery_worker import summarize_case

router = APIRouter(
    tags=["summarizers"],
    responses={200: {"description": "ok"}},
)


@router.post(
    "/case",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        200: {"description": "Not used"},
        202: {"description": "Processing summary."},
        422: {"description": "Invalid input."},
        500: {"description": "Failed."},
    },
)
async def create_summary(request: Request, case_data: CaseData):
    logger = logging.getLogger("generative_summarizer")
    try:
        client = get_db_client()
        db = client["generative_summarizer"]
        if case_data.source == "user":
            if not case_data.summary:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid input. Summary must be provided when source == user.",
                )
            result = db["case_summaries"].insert_one(
                CaseSummary(
                    summary=case_data.summary,
                    source=case_data.source,
                    case_data=case_data,
                    status="COMPLETED",
                    completed_date=datetime.now(),
                ).dict()
            )
            return {
                "message": "Summary created.",
                "summary_id": str(result.inserted_id),
            }
        else:
            result = db["case_summaries"].insert_one(
                CaseSummary(case_data=case_data, status="PENDING", source="AI").dict()
            )
            summarize_case.delay(case_data.dict(), summary_id=str(result.inserted_id))
    except AttributeError as e:
        logger.debug(e)
        raise HTTPException(status_code=422, detail=f"Invalid input. {e}")
    return {
        "message": "Summary creation in progress.",
        "summary_id": str(result.inserted_id),
    }


@router.get("/case", status_code=status.HTTP_200_OK)
# pylint: disable=C0103
async def get_case_summary(request: Request, caseId: str) -> list[CaseSummaryResponse]:
    client = get_db_client_async()
    db = client["generative_summarizer"]
    summary_list = (
        await db["case_summaries"]
        .find({"case_data.case_id": caseId})
        .sort("created_date", DESCENDING)
        .to_list(length=100)
    )
    if len(summary_list) == 0:
        raise HTTPException(status_code=404, detail=f"Summary for {caseId} not found.")
    else:
        response = []
        for document in summary_list:
            response.append(CaseSummaryResponse(**document))
        return response


@router.get("/case/{summary_id}", status_code=status.HTTP_200_OK)
async def get_case_summary_by_id(
    request: Request, summary_id: str
) -> CaseSummaryResponse:
    summary_document = await request.app.state.database["case_summaries"].find_one(
        {"_id": ObjectId(summary_id)}
    )
    if not summary_document:
        raise HTTPException(status_code=404, detail="Summary not found.")
    else:
        return CaseSummaryResponse(**summary_document)
