from setuptools import setup, find_packages

setup(
    name="timebased_logger",
    version="0.1.0",
    description="A logger that logs messages based on time intervals, not message count.",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.6",
    url="https://johnscolaro.xyz/blog/log-by-time-not-by-count",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 