"""Legacy setuptools entry point for editable installs with older pip versions."""

from setuptools import find_packages, setup


setup(
    name="medrag",
    version="0.1.0",
    description="A local, cited medical-information RAG assistant",
    packages=find_packages(include=["medrag", "medrag.*"]),
    python_requires=">=3.9",
    extras_require={
        "ui": ["streamlit>=1.35"],
        "llm": ["anthropic>=0.30"],
        "dev": ["pytest>=8"],
    },
    entry_points={"console_scripts": ["medrag=medrag.cli:main"]},
)
