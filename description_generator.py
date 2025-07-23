import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

CHOICE_FILE = "llm_choice.txt"

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(api_key=openai_api_key, model_name="gpt-3.5-turbo")

prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant for time tracking. Given a short user input and also if git commit also there use that to generate the description, 
    generate a detailed and informative Clockify time entry description (max 100 characters). Be specific about the activity, task, or context based on the input. 
    Do not mention LangChain or AI unless the user input is about those topics.
    User input: {info}
    Description:
    """
)

prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant for time tracking. Given a short user input and also if git commit is there, 
    use that to generate the description, generate a detailed and informative Clockify time entry description 
    (max 100 characters). Be specific about the activity, task, or context based on the input. 
    Do not mention LangChain or AI unless the user input is about those topics.
    User input: {info}
    Description:
    """
)

def choose_llm():
    """Ask the user for their choice once and save it for future use."""
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
    """Get the saved choice or ask the user if not already chosen."""
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

def generate_description(info: str) -> str:
    chain = prompt | llm
    result = chain.invoke({"info": info})
    return result.content.strip()


if __name__ == "__main__":
    llm = get_llm()
    user_info = input("Enter brief info for time entry: ")
    description = generate_description(llm, user_info)
    print("Generated description:", description)
