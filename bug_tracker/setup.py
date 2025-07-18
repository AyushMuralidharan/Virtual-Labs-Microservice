from setuptools import setup, find_packages

setup(
    name="bug_tracker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pymongo",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "requests",
        "pytest",
        "httpx",
    ],
) 