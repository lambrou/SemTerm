from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from background_workers.celery_worker import celery_app

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={200: {"description": "ok"}},
)

# @router.get(
#     "/task/{task_id}",
#     status_code=200,
#     responses={
#         200: {"description": "Task status retrieved."},
#         404: {"description": "Task not found."},
#     }
# )
# async def get_task(task_id: str):
#     task = AsyncResult(task_id, app=celery_app)
#     if not task or task.state == 'PENDING':
#         raise HTTPException(status_code=404, detail="Task not found.")
#     return {"status": task.status, "result": task.result}
