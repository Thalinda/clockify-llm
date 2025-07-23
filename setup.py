from setuptools import setup

setup(
    name="clockify_llm",
    version="0.1",
    py_modules=["llm_config"],
    install_requires=[
        "python-dotenv",
        "langchain",
        "langchain-openai",
        "transformers",
        "torch",
    ],
    entry_points={
        "console_scripts": [
            "clockify-llm=llm_config:main"
        ]
    },
    author="Thalinda Bandara",
    description="Clockify LLM Console Tool",
    python_requires=">=3.8",
) 
    