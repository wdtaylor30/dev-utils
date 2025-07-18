# --- set up llm ---
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
llm = Ollama(model = "granite3.3:8b", 
    request_timeout = 120.0,
    context_window = 8192,
    temperature = 0.1)
Settings.llm = llm

# --- initialize MCP client and build agent ---
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import AgentWorkflow

# --- async setup function for tools (no change needed here) ---
async def get_tools_async():
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    mcp_tools = McpToolSpec(client = mcp_client)
    tools = await mcp_tools.to_tool_list_async()
    return tools

# --- main asynchronous function to run the client ---
async def main():
    # --- async call to get tools ---
    tools = await get_tools_async() # Await the async function

    for tool in tools:
        print(f"Tool: {tool.metadata.name}\nDescription: {tool.metadata.description}\n")

    # --- initialize and run the agent ---
    agent = AgentWorkflow.from_tools_or_functions(
        tools,
        llm=llm,
        verbose=True,
        system_prompt=(
            "You are a helpful assistant that can interact with the user's filesystem "
            "within the '~/projects' directory. "
            "You have access to the following tools:\n\n"
            "- `list_directory`: Use this tool to list the contents of a directory. "
            "   Signature: `list_directory(directory_path: str = '.') -> list[str]`\n"
            "   Description: When the user asks to see files, list contents, or explore directories, use this tool.\n"
            "- `read_file`: Use this tool to read the content of a specific file.\n"
            "   Signature: `read_file(file_path: str) -> str`\n"
            "   Description: Use this tool to read the content of a specific file.\n\n"
            "When you need to use a tool, respond ONLY in the following strict format, without any extra text or conversation:\n"
            "Thought: I need to use a tool to accomplish the user's request.\n"
            "Action: tool_name\n"
            "Action Input: {'param1': 'value1', 'param2': 'value2'}\n\n"
            "If you do NOT need to use a tool, respond naturally to the user. "
            "Do NOT generate code examples. Focus on generating the tool call in the specified format if a tool is needed."
            "Make sure to replace `tool_name` with the actual name of the tool (e.g., `list_directory`)."
            "For `Action Input`, provide a valid JSON dictionary corresponding to the tool's arguments."
        )
    )

    print("Agent initialized. Type 'exit' to quit.")
    print("Note: This agent executes a single workflow run per query and does not maintain chat history automatically.")
    while True:
        query = input("You: ")
        if query.lower() == 'exit':
            print("Exiting agent.")
            break
        try:
            response = await agent.run(query) # Await the agent.run() call
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Agent Error: {e}")
            print("Please try again or 'exit' to quit.")

# --- run the main asynchronous function ---
import asyncio

if __name__ == "__main__":
    asyncio.run(main())