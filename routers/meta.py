from fastapi import APIRouter
from fastapi.openapi.models import Info
from starlette import status
from starlette.requests import Request

from models.Response import BaseResponse

router = APIRouter(
    prefix="",
    tags=["meta"],
    responses={200: {"description": "ok"}},
)


@router.get("/", status_code=status.HTTP_200_OK)
async def root(request: Request) -> Info:
    blacklist = ["swagger_ui_redirect"]
    url_list = {}
    for route in request.app.routes:
        if route.name is not None and route.name not in blacklist:
            url_list[route.name] = route.path
    return Info(title="Generative Summarizer", version="1.0", endpoints=url_list)


@router.get("/health", status_code=status.HTTP_200_OK)
async def root_head() -> BaseResponse:
    return BaseResponse()
