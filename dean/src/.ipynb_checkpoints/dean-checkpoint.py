import os
from langchain_community.chat_models import ChatOllama
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage
from tools import file_tools

# --- ollama config ---
# configuration should be tailored to the machine dean is running on
ollama_base_url = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
print(f"Connecting to Ollama at: {ollama_base_url}")

llm = ChatOllama(model = 'codegemma:7b', base_url = ollama_base_url, temperature = 0.8)

# --- prompting ---
# TODO: fix pathing
PROMPT_FILE = '/home/wdtay/bin/dev-utils/dean/hand/system_prompt.md'
try:
    with open(PROMPT_FILE, 'r') as f:
        system_message = f.read()
except FileNotFoundError:
    print(f"Error: Prompt file '{PROMPT_FILE}' not found.")
    exit(1)

# --- create agent and executor ---
# define memory
memory = ConversationBufferMemory(memory_key = 'chat_history', return_messages = True)

agent_executor = initialize_agent(
    tools = file_tools,
    llm = llm,
    agent = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose = True,
    handle_parsing_errors = True,
    memory = memory,
    agent_kwargs = {'system_message': system_message}
)

# --- chat loop ---
print("Session started. Type 'bye' to end the session.")

while True:
    user_input = input('> ')
    if user_input.lower() == 'bye':
        print('Goodbye!')
        break
    
    try:
        response = agent_executor.invoke({'input': user_input})
        
        # agent's final answer is in response['output']
        print(f"{response['output']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print('Please try rephrasing your request.')