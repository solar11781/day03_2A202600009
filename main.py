import os
from dotenv import load_dotenv

# Import core modules
from src.core.local_provider import LocalProvider
from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent

# Import the custom tool function
from src.tools.calculator import calculate_date_with_llm
from src.tools.search import search_with_llm
from src.tools.task_planner import task_planner

# Load environment variables
load_dotenv()

# ==========================================
# 1. MOCK THE MISSING TOOLS (SEARCH & CALENDAR)
# ==========================================
# def search_mock(query: str) -> str:
#     """Mock function for the search tool."""
#     print(f"\n[Tool Execution] Searching for: {query}")
#     return """
#     Found the following highly recommended Machine Learning resources:
#     1. "Machine Learning Specialization" course by Andrew Ng (Coursera).
#     2. Book: "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow" by Aurélien Géron.
#     3. MIT OpenCourseWare "Machine Learning" playlist on YouTube.
#     """

# def calendar_mock(details: str) -> str:
#     """Mock function for the calendar scheduling tool."""
#     print(f"\n[Tool Execution] Scheduling event: {details}")
#     return "Success: The study schedule has been successfully saved to your Google Calendar."

# ==========================================
# 2. MAIN EXECUTION FUNCTION
# ==========================================
def main():
    print("🚀 Initializing AI Lab ReAct Agent (Powered by Local LLM)...")
    
    # INITIALIZE LLM (choose provider via DEFAULT_PROVIDER env var)
    provider_choice = os.getenv("DEFAULT_PROVIDER", "local").lower()
    if provider_choice == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        llm = LocalProvider(model_path=model_path)
    else:
        llm = GeminiProvider(model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), api_key=os.getenv("GEMINI_API_KEY"))
    
    # ==========================================
    # 3. CONFIGURE THE TOOLSET
    # ==========================================
    tools_config = [
        {
            "name": "search",
            "description": "Search the internet for study materials and courses. The argument should be the search query string.",
            "func": lambda args: search_with_llm(args, llm)
        },
        {
            "name": "calculate_date",
            "description": "Calculate the number of days based on a natural language time expression. Returns the number of days.",
            "func": lambda args: calculate_date_with_llm(args, llm)
        },
        {
            "name": "calendar",
            "description": "Schedule calendar events. The argument should be a detailed description of the event, including days and hours.",
            "func": lambda args: task_planner(args, llm)
        }
    ]
    
    # ==========================================
    # 4. INITIALIZE AGENT AND RUN USE CASE
    # ==========================================
    agent = ReActAgent(llm=llm, tools=tools_config, max_steps=7)
    
    # The specific AI Lab application use case translated to English
    user_query = "Make a study plan from now to 30/04"
    
    print(f"\n👤 User: {user_query}")
    print("-" * 50)
    
    # Execute the ReAct loop
    final_response = agent.run(user_query)
    
    print("\n" + "=" * 50)
    print("🤖 FINAL ANSWER:")
    print(final_response)
    print("=" * 50)

if __name__ == "__main__":
    main()