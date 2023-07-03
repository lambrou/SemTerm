from celery import Celery

import background_workers


async def setup(app):
    app.state.database = app.state.mongodb.generative_summarizer_test
