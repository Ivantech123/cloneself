from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-persona-bot",
    version="1.1.0",
    author="Ivantech123",
    author_email="your.email@example.com",
    description="AI Persona Bot - Умный чат-бот с голосом и личностью",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ivantech123/cloneself",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-persona-bot=ai_persona_bot:main",
        ],
    },
)
