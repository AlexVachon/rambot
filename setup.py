from setuptools import setup, find_packages

setup(
    name="rambot",
    version="0.1.0",
    author="Alexandre Vachon",
    description="Rambot is a versatile and configurable web scraping framework designed to automate data extraction from web pages. It provides an intuitive structure for managing different scraping modes, handling browser automation, and logging.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AlexVachon/botminator/",
    packages=find_packages(),
    install_requires=[
        "botasaurus",
        "loguru",
        "pydantic-settings",
        "pydantic"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "rambot=rambot.main:main",
        ],
    },
    include_package_data=True,
    license="MIT"
)
