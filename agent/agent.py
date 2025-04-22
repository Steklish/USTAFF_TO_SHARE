import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from dotenv import load_dotenv


from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters


load_dotenv()
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (41 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time() -> dict:
    """Returns the current time
    Returns:
        dict: status and result or error msg.
    """

    now = datetime.datetime.now()
    report = (
        f'The current time is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


async def get_tools_async():
    """Gets tools from the File System MCP Server."""
    print("Attempting to connect to MCP Filesystem server...")
    tools, exit_stack = await MCPToolset.from_server(
        # Use StdioServerParameters for local process communication
        connection_params=StdioServerParameters(
            command='npx', # Command to run the server
            args=["-y",    # Arguments for the command
                    "@modelcontextprotocol/server-filesystem",
                    "D:/VS_code/AI/Ustaff/data"],
        )
        # For remote servers, you would use SseServerParams instead:
        # connection_params=SseServerParams(url="http://remote-server:port/path", headers={...})
    )
    print("MCP Toolset created successfully.")
    # MCP requires maintaining a connection to the local MCP Server.
    # exit_stack manages the cleanup of this connection.
    return tools, exit_stack




# sub_agent_time = Agent(
#     name="time_agent",
#     model="gemini-2.0-flash",
#     description=(
#         "Agent to answer questions about the time."
#     ),
#     instruction=(
#         "You are a helpful agent who can answer user questions about the time."
#     ),
#     tools=[get_current_time],
# )
# sub_agent_weather = Agent(
#     name="weather_agent",
#     model="gemini-2.0-flash",
#     description=(
#         "Agent to answer questions about weather in a city."
#     ),
#     instruction=(
#         "You are a helpful agent who can answer user questions about weather in a city."
#     ),
#     tools=[get_weather],
# )


async def create_agent():
  """Gets tools from MCP Server."""
  tools, exit_stack = await get_tools_async()

  agent = Agent(
      model='gemini-2.0-flash', # Adjust model name if needed based on availability
      name='filesystem_assistant',
      instruction='Help user interact with the local filesystem using available tools.',
      tools=tools, # Provide the MCP tools to the ADK agent
  )
  return agent, exit_stack

