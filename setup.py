from setuptools import setup, find_packages

setup(
    name="semterm",
    version="0.6.1",
    description="The Semantic Terminal",
    long_description="The Semantic Terminal",
    author="Lambrou",
    author_email="alexanderlambrou0602@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "semterm = semterm.main:main",
        ],
    },
    install_requires=[
        "langchain",
        "langchain-community",
        "langchain-experimental",
        "langchain-openai",
        "pexpect",
        "pydantic",
    ],
)
