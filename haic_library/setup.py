from setuptools import setup, find_packages

setup(
    name="ai_metrics",
    version="0.1.0",
    description="A library for evaluating Human-AI collaboration across various metrics.",
    author="HUA",
    # author_email="mai@",
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy",
        "sqlmodel",
        "minio",
        "python-dotenv"
        # add any other dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
