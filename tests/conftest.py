import asyncio

import pytest
from asgi_lifespan import LifespanManager
from celery.contrib.testing.worker import start_worker
from httpx import AsyncClient

from tests.global_setup import setup
from tests.global_teardown import teardown

from background_workers.celery_worker import celery_app


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {
        "queues": ("celery",),
    }


@pytest.fixture(scope="session")
def celery_worker_context():
    celery_app.conf.update(
        {
            "task_always_eager": True,
            "task_eager_propagates": True,
            "broker_url": "redis://",
            "result_backend": "redis://",
        }
    )

    with start_worker(celery_app, perform_ping_check=False) as worker_context:
        yield worker_context


@pytest.fixture(scope="session")
def app():
    from main import app

    return app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    event_loop = asyncio.new_event_loop()
    yield event_loop
    event_loop.close()


@pytest.fixture(scope="session")
async def test_client(app):
    async with AsyncClient(
        app=app, base_url="http://test"
    ) as test_client, LifespanManager(app):
        print("Client is ready")
        yield test_client


@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown(app):
    await setup(app)
    yield
    await teardown(app)
