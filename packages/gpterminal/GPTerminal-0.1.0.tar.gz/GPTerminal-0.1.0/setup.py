from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="GPTerminal",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A command line tool that utilizes GPT models to assist with various tasks",
    long_description=long_description,
 long_description_content_type="text/markdown",
    url="https://github.com/yourusername/GPTerminal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "click",
        "requests>=2.25.0",
        "rich>=10.0.0",
        "openai>=0.10.2",
        "tiktoken",
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gpterminal=cli:dxr",
        ],
    },
)
