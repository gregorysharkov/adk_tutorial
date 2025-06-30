from google.adk.agents import Agent
from google.adk.tools import google_search
from google.genai import types
import asyncio

# Create an agent with Google Search grounding
def get_search_agent():
    return Agent(
        name="search_test_agent",
        model="gemini-2.0-flash",
        description="Test agent for Google Search grounding.",
        instruction="Use Google Search to answer questions as needed.",
        tools=[google_search]
    )

async def test_search_grounding():
    agent = get_search_agent()
    prompt = "What is the latest news headline about artificial intelligence today?"
    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    # The following assumes you have a runner/session set up; for a direct test, use agent.run_async or similar
    # For demonstration, we'll just print the agent and tool config
    print("Agent config:", agent)
    print("Tools:", agent.tools)
    # You would need to set up a Runner and Session as per ADK docs to actually invoke the agent
    print("NOTE: To fully test, integrate with Runner and Session as in ADK examples.")

if __name__ == "__main__":
    asyncio.run(test_search_grounding()) 