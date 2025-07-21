from setuptools import setup, find_packages

setup(
    name="timebased_logger",
    version="0.1.0",
    description="A logger that logs messages based on time intervals, not message count.",
    author="Prakash Sellathurai",
    packages=find_packages(),
    python_requires=">=3.6",
    url="https://github.com/prakashsellathurai/Timebased-logger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 