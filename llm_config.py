"""
llm_config.py
Handles LLM selection and customization logic for the workspace.
"""
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

CHOICE_FILE = "llm_choice.txt"

def choose_llm():
    print("Choose LLM Provider (only first time):")
    print("1. OpenAI (GPT-3.5 / GPT-4)")
    print("2. LLaMA (Hugging Face Local Model)")
    choice = input("Enter your choice (1 or 2): ").strip()
    if choice not in ["1", "2"]:
        print("Invalid choice, defaulting to OpenAI GPT-3.5.")
        choice = "1"
    with open(CHOICE_FILE, "w") as f:
        f.write(choice)
    return choice

def get_llm():
    if os.path.exists(CHOICE_FILE):
        with open(CHOICE_FILE, "r") as f:
            choice = f.read().strip()
    else:
        choice = choose_llm()
    if choice == "1":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(api_key=api_key, model_name="gpt-3.5-turbo")
    elif choice == "2":
        from langchain_community.chat_models import ChatHuggingFace
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        model_name = "meta-llama/Llama-2-7b-chat-hf"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
        return ChatHuggingFace(model=model, tokenizer=tokenizer)

def set_env_var(key, value):
    """Set or update a key-value pair in the .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            updated = True
            break
    if not updated:
        lines.append(f'{key}={value}\n')
    with open(env_path, 'w') as f:
        f.writelines(lines)
    print(f"Set {key} in .env file.")

def setup_keys():
    openai_key = input("Enter your OpenAI API Key: ").strip()
    clockify_key = input("Enter your Clockify API Token: ").strip()
    set_env_var("OPENAI_API_KEY", openai_key)
    set_env_var("CLOCKIFY_API_TOKEN", clockify_key)
    print("API keys saved to .env.")

def print_help():
    help_text = '''
Clockify LLM Console Tool

Usage:
  python llm_config.py [--help] [--choose-llm] [--show-choice] [--setup-keys]

Options:
  --help           Show this help message and exit
  --choose-llm     Prompt to choose and save LLM provider
  --show-choice    Display the currently selected LLM provider
  --setup-keys     Setup OpenAI and Clockify API keys in .env file
'''
    print(help_text)

def show_choice():
    if os.path.exists(CHOICE_FILE):
        with open(CHOICE_FILE, "r") as f:
            choice = f.read().strip()
        if choice == "1":
            print("Current LLM: OpenAI (GPT-3.5 / GPT-4)")
        elif choice == "2":
            print("Current LLM: LLaMA (Hugging Face Local Model)")
        else:
            print("Current LLM: Unknown")
    else:
        print("No LLM selected yet.")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='store_true')
    parser.add_argument('--choose-llm', action='store_true')
    parser.add_argument('--show-choice', action='store_true')
    parser.add_argument('--setup-keys', action='store_true')
    args = parser.parse_args()

    if args.help:
        print_help()
    elif args.choose_llm:
        choose_llm()
    elif args.show_choice:
        show_choice()
    elif args.setup_keys:
        setup_keys()
    else:
        print_help()

if __name__ == "__main__":
    main()
