import json
from google.genai import types
from google.adk.runners import Runner


async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    content = types.Content(role="user", parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        final_response = "Agent did not produce a response"

        print("=" * 40)
        print_event(event)
        if not event.is_final_response:
            agent_response = event.content.parts[0].text
            print(f"<<< Intermediate response: {agent_response}")
            continue

        # If something goes wrong, escalate to a human
        if event.actions and event.actions.escalate:
            esclation_response = f"Escalating to a human agent: {event.error_code}: {event.error_message}"
            print(esclation_response)
            break

        if event.content and event.content.parts:
            final_response = event.content.parts[0].text

        if final_response:
            print(f"<<< Final response: {final_response}")


def print_event(event):
    """Prints a formatted representation of an agent event."""

    def safe_serializer(obj):
        """A safe JSON serializer that handles objects with non-serializable attributes."""
        # For objects with a to_dict method, use it.
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        # For other objects, convert them to a dictionary, filtering out non-serializable types.
        if hasattr(obj, "__dict__"):
            return {
                key: value
                for key, value in vars(obj).items()
                if not key.startswith("_")
            }
        # For basic types that are not serializable by default.
        return str(obj)

    if hasattr(event, "content") and event.content:
        print(json.dumps(event, indent=4, default=safe_serializer))
    else:
        # Fallback for events without content
        print(event)
