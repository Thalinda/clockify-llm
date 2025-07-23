# Clockify LLM Console Tool

A command-line utility to generate detailed Clockify time entry descriptions using LLMs (OpenAI GPT or LLaMA). Easily select your preferred LLM provider and generate descriptions from user input or git commit messages.

## Features
- Choose between OpenAI (GPT-3.5/4) and LLaMA (local Hugging Face model)
- Save your LLM choice for future runs
- Generate time entry descriptions from user input or git logs
- Console tool with easy-to-use commands

## Installation
1. Clone this repository:
   ```sh
   git clone <your-repo-url>
   cd clock
   ```
2. Install globally:
   ```sh
   pip install .
   ```

## Usage
After installation, use the CLI tool from anywhere:

```sh
clockify-llm --help
```

### Options
- `--help`           Show help message
- `--choose-llm`     Prompt to choose and save LLM provider
- `--show-choice`    Display the currently selected LLM provider

## Environment Variables
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key
CLOCKIFY_API_TOKEN=your_clockify_api_token
API=https://api.clockify.me/api/v1
```

## Requirements
- Python 3.8+
- See `setup.py` for required Python packages

## License
MIT
