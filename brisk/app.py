import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import time
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("Please set GOOGLE_API_KEY in your .env file")
    st.stop()

# Initialize session state
if 'agents' not in st.session_state:
    st.session_state.agents = []
if 'agent_outputs' not in st.session_state:
    st.session_state.agent_outputs = {}
if 'report' not in st.session_state:
    st.session_state.report = ""
if 'pending_tasks' not in st.session_state:
    st.session_state.pending_tasks = []

class Agent:
    def __init__(self, name: str, role: str, model: str = "gemini-1.5-flash"):
        self.name = name
        self.role = role
        self.model = model
        self.model_instance = genai.GenerativeModel(model)
        self.output = ""
        self.status = "idle"
        self.last_updated = time.time()
        
    def process_task(self, task: str, context: str = "") -> str:
        """Process a task and return the result"""
        try:
            self.status = "working"
            self.last_updated = time.time()
            prompt = f"""
            You are {self.name}, a {self.role}.
            
            Task: {task}
            Context: {context}
            
            Please provide a detailed response based on your role and expertise.
            """
            
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

def create_agent(name: str, role: str, model: str = "gemini-1.5-flash") -> Agent:
    """Create a new agent"""
    agent = Agent(name, role, model)
    st.session_state.agents.append(agent)
    st.session_state.agent_outputs[agent.name] = ""
    return agent

def main():
    st.set_page_config(
        page_title="Multi-Agent ADK App",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Multi-Agent ADK Application")
    st.markdown("---")
    
    # Three-column layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.header("🎯 Agent Control Panel")
        
        # Agent creation section
        st.subheader("Create New Agent")
        with st.form("create_agent"):
            agent_name = st.text_input("Agent Name", placeholder="e.g., Research Agent")
            agent_role = st.text_area("Agent Role", placeholder="Describe the agent's role and expertise")
            agent_model = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"])
            
            if st.form_submit_button("Create Agent"):
                if agent_name and agent_role:
                    create_agent(agent_name, agent_role, agent_model)
                    st.success(f"Agent '{agent_name}' created successfully!")
                else:
                    st.error("Please provide both name and role for the agent")
        
        # Task assignment section
        st.subheader("Assign Task")
        if st.session_state.agents:
            with st.form("assign_task"):
                selected_agent = st.selectbox(
                    "Select Agent",
                    options=[agent.name for agent in st.session_state.agents]
                )
                task_description = st.text_area(
                    "Task Description",
                    placeholder="Describe the task for the selected agent"
                )
                context = st.text_area(
                    "Additional Context (Optional)",
                    placeholder="Any additional context or information"
                )
                
                if st.form_submit_button("Run Task"):
                    if task_description:
                        agent = next((a for a in st.session_state.agents if a.name == selected_agent), None)
                        if agent:
                            # Process task immediately (no threading)
                            result = agent.process_task(task_description, context)
                            st.session_state.agent_outputs[agent.name] = result
                            st.success(f"Task completed for {selected_agent}")
                        else:
                            st.error("Agent not found")
                    else:
                        st.error("Please provide a task description")
        else:
            st.info("Create an agent first to assign tasks")
        
        # Agent management
        st.subheader("Agent Management")
        if st.session_state.agents:
            for i, agent in enumerate(st.session_state.agents):
                with st.expander(f"{agent.name} ({agent.status})"):
                    st.write(f"**Role:** {agent.role}")
                    st.write(f"**Model:** {agent.model}")
                    if st.button(f"Remove {agent.name}", key=f"remove_{i}"):
                        st.session_state.agents.pop(i)
                        if agent.name in st.session_state.agent_outputs:
                            del st.session_state.agent_outputs[agent.name]
                        st.rerun()
        else:
            st.info("No agents created yet")
    
    with col2:
        st.header("📊 Agent Outputs")
        
        if st.session_state.agents:
            for agent in st.session_state.agents:
                with st.expander(f"{agent.name} - {agent.status.upper()}", expanded=True):
                    if agent.status == "working":
                        with st.spinner(f"{agent.name} is working..."):
                            st.write("Processing...")
                            if hasattr(agent, 'last_updated'):
                                st.caption(f"Last updated: {time.strftime('%H:%M:%S', time.localtime(agent.last_updated))}")
                    elif agent.status == "completed":
                        output = st.session_state.agent_outputs.get(agent.name, agent.output)
                        st.write(output if output else "No output yet")
                        if hasattr(agent, 'last_updated'):
                            st.caption(f"Completed at: {time.strftime('%H:%M:%S', time.localtime(agent.last_updated))}")
                    elif agent.status == "error":
                        output = st.session_state.agent_outputs.get(agent.name, agent.output)
                        st.error(output if output else "Error occurred")
                        if hasattr(agent, 'last_updated'):
                            st.caption(f"Error at: {time.strftime('%H:%M:%S', time.localtime(agent.last_updated))}")
                    else:
                        st.info("Agent is idle. Assign a task to get started.")
        else:
            st.info("Create agents in the left panel to see their outputs here")
    
    with col3:
        st.header("📝 Report Panel")
        
        # Report generation
        if st.session_state.agents and any(agent.status == "completed" for agent in st.session_state.agents):
            if st.button("Generate Report"):
                completed_agents = [agent for agent in st.session_state.agents if agent.status == "completed"]
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
            st.text_area("Report", st.session_state.report, height=400, disabled=True)
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
                    mime="text/plain"
                )

if __name__ == "__main__":
    main() 