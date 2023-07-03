async def teardown(app):
    app.state.mongodb.drop_database('generative_summarizer_test')
