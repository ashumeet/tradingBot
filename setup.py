from setuptools import setup, find_packages

setup(
    name="trader_app",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    author="Ashu Samra",
    description="A modular trading application.",
    url="",
)
