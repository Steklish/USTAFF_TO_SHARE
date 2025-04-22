from google.genai import types # For creating message Content/Parts

from agent import *
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'

# Reset
RESET = '\033[0m'


import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")


# Define constants for identifying the interaction context
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity
session_service = InMemorySessionService()






async def async_main():

    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    root_agent, exit_stack = await create_agent()
    
    runner = Runner(
        agent=root_agent, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service # Uses our session manager
    )

    # Prepare the user's message in ADK format
    while 1:
        query = input(f"\n{MAGENTA}>>> {RESET}")
        content = types.Content(role='user', parts=[types.Part(text=query)])

        final_response_text = "Agent did not produce a final response." # Default

        # Key Concept: run_async executes the agent logic and yields Events.
        # We iterate through events to find the final answer.
        
        
        
        
        
        try:
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
                # You can uncomment the line below to see *all* events during execution
                print(f"  [Event] {BLUE}Author:{RESET} {event.author}, {GREEN}Type:{RESET} {type(event).__name__}, Final: {event.is_final_response()}, {YELLOW}Content: {RESET}{event.content}")

                # Key Concept: is_final_response() marks the concluding message for the turn.
                # print(event.__str__())
                if event.is_final_response():
                    if event.content and event.content.parts:
                        # Assuming text response in the first part
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                        final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                    # Add more checks here if needed (e.g., specific error codes)
                    break # Stop processing events once the final response is found

            print(f"{YELLOW}<<< Agent Response: {final_response_text} {RESET}")
            print(RED, session.state, RESET)
        except Exception as e:
            print(e)
    
    
    
    
if __name__ == "__main__":
    asyncio.run(async_main())