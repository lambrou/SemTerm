# SemTerm: The Semantic Terminal 🚀

Welcome to SemTerm, the revolutionary Semantic Terminal that leverages the power of Large Language Models to perform complex tasks with a simple, human speech-like command. With SemTerm, you can spin up Django projects, run servers, and much more, all with a simple, intuitive instruction. SemTerm offers a futuristic command-line experience currently available only for Linux and MacOS users.

## Table of Contents 📚

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Ideas for Future Development](#ideas-for-future-development)
6. [Contribute](#contribute)
7. [License](#license)

## Features 🌟

* User-friendly semantic input
* Harness the power of Large Language Models for complex shell commands

## Requirements 🔧

* Python 3.10
  * langchain
  * tiktoken
  * pexpect 
  * pydantic
* Linux (Debian-based recommended) or MacOS

## Installation 📦

By default, the libraries use your `OPENAI_API_KEY` environment variable. You can set this variable in your `.bashrc` or `.zshrc` file:

```bash
export OPENAI_API_KEY="your-key-here"
```

1. Clone the SemTerm repository:

```bash
git clone https://github.com/lambrou/SemTerm
```

2. Change into the project directory:

```bash
cd SemTerm
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage 🖥️ (Debian Package Coming Soon!)

```bash
python -m semterm.main
```

```bash
You > Hey, will you spin me up a django project called more_human_than_human and run it?
semterm > django-admin startproject myproject && cd myproject && python manage.py runserver

You have 17 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
May 01, 2023 - 18:19:51
Django version 2.2.28, using settings 'more_human_than_human.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

semterm >  I have spun up a Django project called more_human_than_human and started the server. 
You can access it at http://127.0.0.1:8000/
You > Wow, thanks!!
semterm > Not a problem, please let me know if there is anything else I can assist you with.

```

## Ideas for Future Development 💡

We have a roadmap for future enhancements, including:

1. Incorporating support for deploying projects to cloud platforms such as AWS, GCP, or Heroku.
2. Expanding cross-platform compatibility to include Windows users.

## Contribute 🤝

We welcome contributions to SemTerm!

## License ⚖️

SemTerm is released under the [MIT License](LICENSE).