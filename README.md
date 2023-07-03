Generative Summarizer
=====================

Generative Summarizer is a pythonic backend service for asynchronous summary generation and storage.


Main Stack
--------

* Python 3.11
* FastAPI
* Hypothesis (for testing)
* Poetry

Features
--------

* Async API and Database operations using FastAPI and Motor
* Pydantic models for data validation
* Unit testing with Hypothesis
* Dependency management using Poetry
* Preprocessing using Deduce, Faker and Tiktoken
* Language model agnostic design

Getting Started
---------------

### Docker Compose

To start the `FastAPI` server and `mongo` database, ensure you have
a `.env.docker` file in the root directory with the following variables:

```
OPENAI_API_KEY
DATABASE_URL=mongodb://db:27017
```

Then, run the following command:

```bash
docker compose up -d
```

Project will be available at `localhost:8000`

### Dev Install

The project uses Poetry for dependency management.
To install all the dependencies, simply run:

```bash
poetry install
```

Testing
-------

The project uses [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) for property-based testing.

Hypothesis allows us to specify the kind of data our functions work with and then
generates test cases.

To run the unit tests, use the following command:

```bash
pytest tests/
```

To run tests with coverage, run

```bash
pytests --cov tests/
```

Global setup and teardown scripts are located within the `tests/` folder with filenames `global_setup.py`
and `global_teardown.py`.

Service Configuration
--------
This project uses pydantic's `BaseSettings` class for configuration.

The configuration file is located at `settings/Settings.py`

The `Settings` model imports all the environment variables from the `.env` file in the root directory.

Database
--------

The project uses MongoDB for data storage, making use of Motor for asynchronous database operations. This results in
non-blocking IO operations, which ensures our service maintains high performance and responsiveness even when dealing
with large amounts of data.

Models
--------

Models in this project are defined with Pydantic, used for database operations, API request and response formatting.
Pydantic provides robust data validation which increases the reliability and security of the application.

Langchain Adapter
--------

All the code specific to the Langchain library resides in the `langchain_adapter/` folder. This includes
the `summaries/chains/`
and `summaries/prompts/` directories.

API Endpoints
--------

API endpoints are defined in the `routers/` folder.

Preprocessing
-------------

The `preprocessing/` folder houses important classes such as `IdentityHandler.py` and `TokenHandler.py`.

`IdentityHandler.py` is responsible for handling sensitive data operations including deidentifying, surrogating, and
reidentifying the data.

`TokenHandler.py` is used for tokenizing operations like splitting text based on token size.

Logging
-------

The project utilizes Python's logging package for logging purposes. The configuration for this can be found
in `LogConfig.py` within the `logs/` folder.
