# SemTerm: The Semantic Terminal 🖥️🚀

SemTerm is a groundbreaking command-line tool that harnesses the capabilities of Large Language Models to execute complex tasks using natural, conversational input.
With SemTerm, you can run complex bash commands with a simple, intuitive instruction. 

SemTerm offers a futuristic command-line experience currently available only for Linux and MacOS users.

You can ask it things like
```bash
You > How large is this directory?
semterm > du -sh
146M    .
semterm >  The size of the current directory is 146M.
```

And pretty much anything else you can think of. You are only limited by your imagination. 💭

Join our [Discord](https://discord.gg/TQSbWnck) to discuss SemTerm and help out with development!

## Features 🌟

* User-friendly semantic input
* SemTerm has thoughts, observations and actions.
* Can perform multiple shell commands at once
* Can request more information from the user
* sudo ability is currently being worked on and tested

## Requirements 🔧

* Python 3.10
  * langchain
  * tiktoken
  * pexpect 
  * pydantic
* Linux (Debian-based recommended) or MacOS

## Installation 📦

* Requires Python 3.10

Install via `pip`

```bash
pip install semterm
```

By default, the libraries use your `OPENAI_API_KEY` environment variable. 

You can set this variable in your `.bashrc` or `.zshrc` file:

```bash
export OPENAI_API_KEY="your-key-here"
```

## Usage 🖥️

Just type `semterm` in the terminal to get started!

```bash
$ semterm
You > Hey, will you spin me up a django project called more_human_than_human and run it?
semterm > django-admin startproject more_human_than_human && cd more_human_than_human && python manage.py runserver

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

## Expectations and Contribution
While SemTerm is a powerful and unique tool, it's important to understand that it's still in development and may not always provide the perfect solution. As with any complex technology, occasional mistakes or unexpected behaviors are part of the journey towards improvement.

We encourage users to approach SemTerm with an open mind, embracing its potential while also understanding its current limitations. In fact, we'd love for you to be part of our ongoing development process. If you encounter any issues or have ideas for enhancements, we invite you to contribute by:

* Reporting bugs or unexpected behavior
* Suggesting improvements or new features
* Submitting pull requests with code fixes or enhancements

By working together, we can refine SemTerm and create a more powerful, accurate, and efficient tool for everyone.

Thank you for being a part of our journey, and we look forward to your valuable feedback and contributions!

## License ⚖️

SemTerm is released under the [MIT License](LICENSE).
