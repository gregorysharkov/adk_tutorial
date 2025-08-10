import asyncio
import json
import os
import time

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("Please set GOOGLE_API_KEY in your .env file")
    st.stop()

AGENTS_FILE = "agents.json"

try:
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False


class Agent:
    def __init__(
        self,
        name: str,
        role: str,
        model: str = "gemini-1.5-flash",
        use_search: bool = False,
    ):
        self.name = name
        self.role = role
        self.model = model
        self.use_search = use_search
        self.model_instance = genai.GenerativeModel(model)
        self.output = ""
        self.status = "idle"
        self.last_updated = time.time()
        self.tools = (
            [google_search] if use_search and model.startswith("gemini-2.0") else []
        )
        self.runner = None
        self.session_service = None
        self.session = None
        if self.tools:
            self.session_service = InMemorySessionService()
            # Use a unique session id per agent
            self.session_id = f"session_{self.name}_{int(time.time())}"
            self.runner = Runner(
                agent=self.get_adk_agent(),
                app_name="adk_app",
                session_service=self.session_service,
            )
            # Session will be created on first use

    def get_adk_agent(self):
        # Return a new ADK Agent instance with the same config
        from google.adk.agents import Agent as ADKAgent

        return ADKAgent(
            name=self.name,
            model=self.model,
            description=self.role,
            instruction=self.role,
            tools=self.tools,
        )

    async def process_task_async(self, task: str, context: str = "") -> str:
        self.status = "working"
        self.last_updated = time.time()
        prompt = f"""
        You are {self.name}, a {self.role}.
        Task: {task}
        Context: {context}
        Please provide a detailed response based on your role and expertise.
        """
        from google.genai import types

        try:
            if self.tools:
                # Use ADK runner/session for tool-enabled agents
                if not self.session:
                    self.session = await self.session_service.create_session(
                        app_name="adk_app", user_id="user", session_id=self.session_id
                    )
                content = types.Content(role="user", parts=[types.Part(text=prompt)])
                events = self.runner.run_async(
                    user_id="user", session_id=self.session_id, new_message=content
                )
                result = ""
                async for event in events:
                    if event.is_final_response():
                        result = event.content.parts[0].text
                        break
                self.output = result
                self.status = "completed"
                self.last_updated = time.time()
                return result
            else:
                # Fallback to plain LLM
                response = self.model_instance.generate_content(prompt)
                self.output = response.text
                self.status = "completed"
                self.last_updated = time.time()
                return self.output
        except Exception as e:
            self.status = "error"
            self.output = f"Error: {str(e)}"
            self.last_updated = time.time()
            return self.output

    def process_task(self, task: str, context: str = "") -> str:
        if self.tools:
            return asyncio.run(self.process_task_async(task, context))
        else:
            # Fallback to plain LLM (synchronous)
            self.status = "working"
            self.last_updated = time.time()
            prompt = f"""
            You are {self.name}, a {self.role}.
            Task: {task}
            Context: {context}
            Please provide a detailed response based on your role and expertise.
            """
            try:
                response = self.model_instance.generate_content(prompt)
                self.output = response.text
                self.status = "completed"
                self.last_updated = time.time()
                return self.output
            except Exception as e:
                self.status = "error"
                self.output = f"Error: {str(e)}"
                self.last_updated = time.time()
                return self.output

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "use_search": self.use_search,
        }

    @staticmethod
    def from_dict(data):
        return Agent(
            data["name"],
            data["role"],
            data.get("model", "gemini-1.5-flash"),
            data.get("use_search", False),
        )


def save_agents():
    with open(AGENTS_FILE, "w") as f:
        json.dump([agent.to_dict() for agent in st.session_state.agents], f)


def load_agents():
    if os.path.exists(AGENTS_FILE):
        with open(AGENTS_FILE) as f:
            agent_dicts = json.load(f)
            return [Agent.from_dict(a) for a in agent_dicts]
    return []


# Initialize session state
if "agents" not in st.session_state:
    st.session_state.agents = load_agents()
if "agent_outputs" not in st.session_state:
    st.session_state.agent_outputs = {}
if "report" not in st.session_state:
    st.session_state.report = ""
if "pending_tasks" not in st.session_state:
    st.session_state.pending_tasks = []


def create_agent(
    name: str, role: str, model: str = "gemini-1.5-flash", use_search: bool = False
) -> Agent:
    """Create a new agent"""
    agent = Agent(name, role, model, use_search)
    st.session_state.agents.append(agent)
    st.session_state.agent_outputs[agent.name] = ""
    save_agents()
    return agent


def main():
    st.set_page_config(
        page_title="Multi-Agent ADK App",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🤖 Multi-Agent ADK Application")
    st.markdown("---")

    # Add custom CSS for smaller headers
    st.markdown(
        """
        <style>
        .small-header { font-size: 1.3rem !important; font-weight: 700; margin-bottom: 0.5rem; }
        .small-subheader { font-size: 1.05rem !important; font-weight: 600; margin-bottom: 0.3rem; }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Three-column layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown(
            '<div class="small-header">🎯 Agent Control Panel</div>',
            unsafe_allow_html=True,
        )
        # 1. Assign Task section
        st.markdown(
            '<div class="small-subheader">Assign Task</div>', unsafe_allow_html=True
        )
        if st.session_state.agents:
            with st.form("assign_task"):
                agent_names = ["All agents"] + [
                    agent.name for agent in st.session_state.agents
                ]
                selected_agent = st.selectbox("Select Agent", options=agent_names)
                task_description = st.text_area(
                    "Task Description",
                    placeholder="Describe the task for the selected agent(s)",
                )
                context = st.text_area(
                    "Additional Context (Optional)",
                    placeholder="Any additional context or information",
                )
                if st.form_submit_button("Run Task"):
                    if task_description:
                        if selected_agent == "All agents":
                            for agent in st.session_state.agents:
                                result = agent.process_task(task_description, context)
                                st.session_state.agent_outputs[agent.name] = result
                            st.success("Task completed for all agents")
                        else:
                            agent = next(
                                (
                                    a
                                    for a in st.session_state.agents
                                    if a.name == selected_agent
                                ),
                                None,
                            )
                            if agent:
                                result = agent.process_task(task_description, context)
                                st.session_state.agent_outputs[agent.name] = result
                                st.success(f"Task completed for {selected_agent}")
                            else:
                                st.error("Agent not found")
                    else:
                        st.error("Please provide a task description")
        else:
            st.info("Create an agent first to assign tasks")
        # 2. Agent Management section
        st.markdown(
            '<div class="small-subheader">Agent Management</div>',
            unsafe_allow_html=True,
        )
        if st.session_state.agents:
            for i, agent in enumerate(st.session_state.agents):
                with st.expander(f"{agent.name} ({agent.status})"):
                    st.write(f"**Role:** {agent.role}")
                    st.write(f"**Model:** {agent.model}")
                    if st.button(f"Remove {agent.name}", key=f"remove_{i}"):
                        st.session_state.agents.pop(i)
                        if agent.name in st.session_state.agent_outputs:
                            del st.session_state.agent_outputs[agent.name]
                        save_agents()
                        st.rerun()
        else:
            st.info("No agents created yet")
        # 3. Create New Agent section
        st.markdown(
            '<div class="small-subheader">Create New Agent</div>',
            unsafe_allow_html=True,
        )
        with st.form("create_agent"):
            agent_name = st.text_input("Agent Name", placeholder="e.g., Research Agent")
            agent_role = st.text_area(
                "Agent Role", placeholder="Describe the agent's role and expertise"
            )
            submitted = st.form_submit_button("Create Agent")
        with st.container():
            st.markdown("**Agent Options**")
            agent_model = st.selectbox(
                "Model",
                [
                    "gemini-1.5-flash",
                    "gemini-1.5-pro",
                    "gemini-pro",
                    "gemini-2.0-flash",
                ],
                key="agent_model_select",
            )
            search_checkbox_disabled = agent_model.strip() != "gemini-2.0-flash"
            search_tooltip = (
                "Enable Google Search grounding (requires gemini-2.0-flash)"
            )
            use_search = st.checkbox(
                "Enable Google Search grounding",
                value=False,
                disabled=search_checkbox_disabled,
                help=search_tooltip,
                key="search_checkbox",
            )
        if submitted:
            if agent_name and agent_role:
                create_agent(agent_name, agent_role, agent_model, use_search)
                st.success(f"Agent '{agent_name}' created successfully!")
            else:
                st.error("Please provide both name and role for the agent")

    with col2:
        st.markdown(
            '<div class="small-header">📊 Agent Outputs</div>', unsafe_allow_html=True
        )

        if st.session_state.agents:
            for agent in st.session_state.agents:
                with st.expander(
                    f"{agent.name} - {agent.status.upper()}", expanded=True
                ):
                    if agent.status == "working":
                        with st.spinner(f"{agent.name} is working..."):
                            st.write("Processing...")
                            if hasattr(agent, "last_updated"):
                                st.caption(
                                    f"Last updated: {time.strftime('%H:%M:%S', time.localtime(agent.last_updated))}"
                                )
                    elif agent.status == "completed":
                        output = st.session_state.agent_outputs.get(
                            agent.name, agent.output
                        )
                        st.write(output if output else "No output yet")
                        if hasattr(agent, "last_updated"):
                            st.caption(
                                f"Completed at: {time.strftime('%H:%M:%S', time.localtime(agent.last_updated))}"
                            )
                    elif agent.status == "error":
                        output = st.session_state.agent_outputs.get(
                            agent.name, agent.output
                        )
                        st.error(output if output else "Error occurred")
                        if hasattr(agent, "last_updated"):
                            st.caption(
                                f"Error at: {time.strftime('%H:%M:%S', time.localtime(agent.last_updated))}"
                            )
                    else:
                        st.info("Agent is idle. Assign a task to get started.")
        else:
            st.info("Create agents in the left panel to see their outputs here")

    with col3:
        st.markdown(
            '<div class="small-header">📝 Report Panel</div>', unsafe_allow_html=True
        )
        # Auto-generate report if all agents are finished and report is empty
        if (
            st.session_state.agents
            and all(
                agent.status in ["completed", "error"]
                for agent in st.session_state.agents
            )
            and not st.session_state.report
        ):
            completed_agents = [
                agent
                for agent in st.session_state.agents
                if agent.status == "completed"
            ]
            if completed_agents:
                report_prompt = f"""
                Generate a comprehensive report based on the following agent outputs:
                
                {chr(10).join([f"Agent: {agent.name} ({agent.role}){chr(10)}Output: {st.session_state.agent_outputs.get(agent.name, agent.output)}" for agent in completed_agents])}
                
                Please provide a well-structured report that summarizes the findings and insights from all agents.
                """
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(report_prompt)
                    st.session_state.report = response.text
                    st.success("Report generated automatically!")
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
        # Report generation (manual)
        if st.session_state.agents and any(
            agent.status == "completed" for agent in st.session_state.agents
        ):
            if st.button("Generate Report"):
                completed_agents = [
                    agent
                    for agent in st.session_state.agents
                    if agent.status == "completed"
                ]
                if completed_agents:
                    report_prompt = f"""
                    Generate a comprehensive report based on the following agent outputs:
                    
                    {chr(10).join([f"Agent: {agent.name} ({agent.role}){chr(10)}Output: {st.session_state.agent_outputs.get(agent.name, agent.output)}" for agent in completed_agents])}
                    
                    Please provide a well-structured report that summarizes the findings and insights from all agents.
                    """
                    try:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        response = model.generate_content(report_prompt)
                        st.session_state.report = response.text
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")

        # Report display
        st.subheader("Current Report")
        if st.session_state.report:
            new_report = st.text_area("Report", st.session_state.report, height=400)
            if new_report != st.session_state.report:
                st.session_state.report = new_report
            if st.button("Clear Report"):
                st.session_state.report = ""
                st.rerun()
        else:
            st.info("Generate a report to see it here")

        # Export options
        if st.session_state.report:
            st.subheader("Export Options")
            if st.button("Download Report as TXT"):
                st.download_button(
                    label="Download Report",
                    data=st.session_state.report,
                    file_name="agent_report.txt",
                    mime="text/plain",
                )


if __name__ == "__main__":
    main()
