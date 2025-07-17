from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=openai_api_key, model_name="gpt-3.5-turbo")
prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant for time tracking. Given a short user input and also if git commit also there use that to generate the description, generate a detailed and informative Clockify time entry description (max 100 characters). Be specific about the activity, task, or context based on the input. Do not mention LangChain or AI unless the user input is about those topics.
    User input: {info}
    Description:
    """
)

def generate_description(info: str) -> str:
    chain = prompt | llm
    result = chain.invoke({"info": info})
    # Truncate to 100 characters if needed
    return result.content.strip()[:100]

if __name__ == "__main__":
    user_info = input("Enter brief info for time entry: ")
    description = generate_description(user_info)
    print("Generated description:", description)
