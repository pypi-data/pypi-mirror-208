from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webwatchdog",
    version="1.0.0",
    description="A Python library to check if a website is up or down.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="itsknk",
    packages=["up_or_down"],
    install_requires=["requests", "colorama"],
)

