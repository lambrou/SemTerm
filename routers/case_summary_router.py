import logging

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from starlette import status
from starlette.background import BackgroundTasks
from fastapi.responses import Response
from starlette.requests import Request

from models.Response import Info, BaseResponse, CaseSummaryResponse
from models.Summary import CaseData, CaseSummary, Summary
from background_workers.celery_worker import summarize_case

router = APIRouter(
    prefix="/summarize",
    tags=["summarizers"],
    responses={200: {"description": "ok"}},
)


@router.post(
    "/summarize_case",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Processing summary."},
        422: {"description": "Invalid input."},
        500: {"description": "Failed."},
    }
)
async def create_summary(case_data: CaseData):
    logger = logging.getLogger("generative_summarizer")
    try:
        task = summarize_case.delay(case_data.dict())
    except ValidationError as e:
        logger.debug(e)
        raise HTTPException(status_code=422, detail=f"Invalid input. {e}")
    return {"message": "Summary creation in progress.", "task_id": str(task.id)}


@router.get("/case_summary/{summary_id}", status_code=status.HTTP_200_OK)
async def get_case_summary(request: Request, summary_id: str) -> CaseSummaryResponse:
    summary_document = await request.app.state.mongodb.summaries.find_one({"_id": summary_id})
    if not summary_document:
        raise HTTPException(status_code=404, detail="Summary not found.")
    else:
        return CaseSummaryResponse(**summary_document)


@router.put("/update_case_summary/{summary_id}", response_model=CaseSummary, status_code=status.HTTP_200_OK)
async def update_case_summary(request: Request, summary_id: str, case_summary: Summary):
    summary = case_summary.summary
    summary_document = await request.app.state.mongodb.summaries.update_one(
        {"_id": summary_id}, {"$set": {'summary': summary}}
    )
    if summary_document.acknowledged:
        if summary_document.modified_count == 0:
            raise HTTPException(status_code=404, detail="Summary not found.")
        updated_summary_document = await request.app.state.mongodb.summaries.find_one({"_id": summary_id})
        return CaseSummary(**updated_summary_document)
    else:
        raise HTTPException(status_code=500, detail="An error occurred while updating the summary.")


@router.delete("/delete_case_summary/{summary_id}", status_code=status.HTTP_200_OK)
async def delete_case_summary(request: Request, summary_id: str) -> BaseResponse:
    delete_result = await request.app.state.mongodb.summaries.delete_one({"_id": summary_id})
    if delete_result.acknowledged:
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Summary not found.")
        else:
            return BaseResponse()
    else:
        raise HTTPException(status_code=500, detail="An error occurred while deleting the summary.")
