from setuptools import setup, find_packages

setup(
    name="semterm",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "semterm = semterm.main:main",
        ],
    },
    install_requires=["black", "flake8", "pytest"],
)
