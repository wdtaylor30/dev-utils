import os
from langchain_community.chat_models import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from tools import file_tools

# --- ollama config ---
# configuration should be tailored to the machine dean is running on
ollama_base_url = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
print(f"Connecting to Ollama at: {ollama_base_url}")

llm = ChatOllama(model = 'codegemma:7b', base_url = ollama_base_url, temperature = 0.0)

# --- prompting ---
# TODO: consider making this a standalone markdown file that's read in
system_message = """You are a Ph.D.-level computer scientist. You can read, write, and list files within a specified directory. Your goal is to assist the user with code generation, architecture,  project planning, and systematic, reproducible approaches to non-code-related tasks; you specifialize in writing computationally efficient code for advanced data science routines. You follow these strict best practices:
1.  **PEP 8 Compliance:** All Python code must strictly follow PEP 8 style guidelines.
2.  **R Style** All R code must strictly follow R best practices.
3.  **Readability:** Use clear, descriptive variable and function names. Add comments where necessary.
3.  **Modularity:** Break down complex problems into smaller, reusable functions. Follow the Single Responsibility Principle: as often as possible, functions should only do one thing.
4.  **Error Handling:** Include basic error handling (e.g., try-except blocks) where appropriate.
5.  **Docstrings:** Every function and class should have a clear docstring explaining its purpose, arguments, and return values. These docstrings should follow a simple, reproducible style.
7.  **Security Awareness:** Avoid common security pitfalls (e.g., SQL injection, insecure file operations).
8.  **Efficiency:** Suggest reasonably efficient algorithms.
10.  **Confirmation:** Always confirm with the user before making any significant file modifications.

When you need to interact with files, you MUST use the provided tools: {tools}

Always show the full contents of any file you plan to write, then ask the user if they would like to write it.
If asked to solve a problem that requires creating multiple files, consider breaking the problem into smaller steps.
"""

prompt = ChatPromptTemplate.from_messages([
    ('system', system_message),
    MessagesPlaceholder(variable_name = 'chat_history')
    ('human', '{input}'),
    MessagesPlaceholder(variable_name = 'agent_scratchpad')
])

# --- create agent and executor ---
agent = create_react_agent(llm = llm, tools = file_tools, prompt = prompt)
agent_executor = AgentExecutor(
    agent = agent,
    tools = file_tools,
    verbose = True,
    handle_parsing_errors = True
)

# --- chat loop ---
chat_history = []

print("Session started. Type 'exit' to end the session.")

while True:
    user_input = input('> ')
    if user_input.lower() == 'exit':
        print('CodeBuddy: Goodbye!')
        break
    
    try:
        # the agent_executor takes the user input and current chat history
        response = agent_executor.invoke({'input': user_input, 'chat_history': chat_history})
        
        # agent's final answer is in response['output']
        print(f"CodeBuddy: {response['output']}")
        
        # update chat history for the next turn
        chat_history.extend([HumanMessage(content = user_input), AIMessage(content = respond['output'])])
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please try rephrasing your request, or check the log for details.")
        
        # add the error to chat history so the agent can debug it
        chat_history.extend([HumanMessage(content = user_input), AIMessage(content = f"Error: {e}")])