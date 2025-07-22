import sys
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.memory import Memory
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import ReActAgent
import asyncio

# --- set up llm ---
CONTEXT_WINDOW = 8192 # used in both llm and memory instantiation 
llm = Ollama(model = "granite3.3:8b", 
    request_timeout = 120.0,
    context_window = CONTEXT_WINDOW,
    temperature = 0.1)
Settings.llm = llm

# --- async setup function for tools ---
async def get_tools_async(mcp_client: BasicMCPClient) -> list:
    mcp_tools = McpToolSpec(client = mcp_client)
    tools = await mcp_tools.to_tool_list_async()
    return tools

# --- main asynchronous function to run the client ---
async def setup_agent():
    # --- async call to get tools ---
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    tools = await get_tools_async(mcp_client) 

    for tool in tools:
        print(f"Tool: {tool.metadata.name}\nDescription: {tool.metadata.description}\n")

    agent = ReActAgent(
        name = "dean",
        llm = llm,
        tools = tools,
        system_prompt = (
            "You are a helpful assistant that can interact with the user's filesystem, primarily using built-in Unix commands."
            "You have access to the following tools:\n\n"
            "- `run_shell_command`: Use this tool to run a Unix shell command.\n"
            "-  Signature: `run_shell_command(command: str, cwd: str = '.') -> dict`\n"
            "-  Description: Use this tool to interact with the file system with native Unix commands."
            "When you need to use a tool, respond ONLY in the following strict format, without any extra text or conversation:\n"
            "Thought: I need to use a tool to accomplish the user's request.\n"
            "Action: tool_name\n"
            "Action Input: {'param1': 'value1', 'param2': 'value2'}\n\n"
            "You may need to infer the values. For example, inputs noting files are relative to the base directory ~/projects. If the user doesn't specify an Action Input, you should be able to populate the Action Input yourself."
            "If you do NOT need to use a tool, respond naturally to the user. This includes calculations, which you should be able to do without tool use."
            "Do NOT generate code examples. Focus on generating the tool call in the specified format if a tool is needed."
            "Make sure to replace `tool_name` with the actual name of the tool (e.g., `list_directory`)."
            "For `Action Input`, provide a valid JSON dictionary corresponding to the tool's arguments."
            "Output should be human-readable." 
        ),
        verbose = False
    )

    return agent

async def main():
    try:
        agent = await setup_agent()

        print("Agent initialized. Type 'exit' to quit.")

        mem = Memory.from_defaults(
            session_id = 'session', # unique identifier for sql database
            token_limit = CONTEXT_WINDOW, # at or around the context window
            token_flush_size = 10, # number of tokens to flush to long-term memory, or drop if no ltm is setup
            chat_history_token_ratio = 1.0 # ratio of tokens for short- vs long-term memory
        )

        while True:
            query = input("> ")
            if query.lower() == 'exit':
                print("Exiting agent.")
                break

            response = await agent.run(query, memory = mem)
            print(f"\n{response}\n")

    except Exception as e:
        print(f"Agent Error: {e}")
        return 1
    
    return 0

# --- run the main asynchronous function ---
if __name__ == "__main__":
    sys.exit(asyncio.run(main()))