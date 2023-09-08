from database.connection_pool import get_db_client_async


async def setup(app):
    if not hasattr(app.state, "mongodb"):
        app.state.database = get_db_client_async()["generative_summarizer_test"]
        app.state.mongodb = get_db_client_async()
    else:
        app.state.database = app.state.mongodb.generative_summarizer_test
