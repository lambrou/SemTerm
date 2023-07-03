from pydantic import BaseModel

from models.Summary import Summary, CaseSummary


class BaseResponse(BaseModel):
    status: str = "ok"


class Info(BaseResponse):
    version: str
    endpoints: dict


class CaseSummaryResponse(BaseResponse, CaseSummary):
    pass


class SummarizeResponse(BaseResponse):
    summary_result: Summary
