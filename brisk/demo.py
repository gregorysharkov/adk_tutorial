"""
Demo script for the Multi-Agent ADK Application
This script demonstrates how to create agents and assign tasks programmatically
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("❌ Please set GOOGLE_API_KEY in your .env file")
    exit(1)

class Agent:
    def __init__(self, name: str, role: str, model: str = "gemini-1.5-flash"):
        self.name = name
        self.role = role
        self.model = model
        self.model_instance = genai.GenerativeModel(model)
        self.output = ""
        self.status = "idle"
        
    def process_task(self, task: str, context: str = "") -> str:
        """Process a task and return the result"""
        try:
            self.status = "working"
            print(f"🤖 {self.name} is working on: {task[:50]}...")
            
            prompt = f"""
            You are {self.name}, a {self.role}.
            
            Task: {task}
            Context: {context}
            
            Please provide a detailed response based on your role and expertise.
            """
            
            response = self.model_instance.generate_content(prompt)
            self.output = response.text
            self.status = "completed"
            print(f"✅ {self.name} completed the task")
            return self.output
        except Exception as e:
            self.status = "error"
            self.output = f"Error: {str(e)}"
            print(f"❌ {self.name} encountered an error: {str(e)}")
            return self.output

def create_agent(name: str, role: str, model: str = "gemini-1.5-flash") -> Agent:
    """Create a new agent"""
    agent = Agent(name, role, model)
    print(f"🤖 Created agent: {name} ({role})")
    return agent

def main():
    print("🚀 Multi-Agent ADK Demo")
    print("=" * 50)
    
    # Create agents
    print("\n📋 Creating agents...")
    
    research_agent = create_agent(
        "Research Agent",
        "Expert researcher specializing in market analysis, competitive intelligence, and industry trends. Skilled at gathering and synthesizing information from multiple sources."
    )
    
    data_analyst = create_agent(
        "Data Analyst",
        "Data scientist with expertise in statistical analysis, data visualization, and predictive modeling. Skilled at interpreting complex datasets and extracting actionable insights."
    )
    
    content_writer = create_agent(
        "Content Writer",
        "Professional content writer with expertise in creating engaging, informative content for various audiences. Skilled at adapting tone and style for different purposes."
    )
    
    agents = [research_agent, data_analyst, content_writer]
    
    # Assign tasks
    print("\n📝 Assigning tasks...")
    
    tasks = [
        (research_agent, "Analyze the current market trends in artificial intelligence and machine learning for 2024", "Focus on enterprise adoption and emerging technologies"),
        (data_analyst, "Create a statistical summary of AI adoption rates across different industries", "Include growth projections and key metrics"),
        (content_writer, "Write a comprehensive blog post about AI trends based on the research findings", "Target audience: business executives and technology leaders")
    ]
    
    # Process tasks
    print("\n⚡ Processing tasks...")
    for agent, task, context in tasks:
        result = agent.process_task(task, context)
        print(f"\n📊 {agent.name} Output:")
        print("-" * 40)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("-" * 40)
        time.sleep(1)  # Small delay between tasks
    
    # Generate report
    print("\n📋 Generating comprehensive report...")
    
    report_prompt = f"""
    Generate a comprehensive report based on the following agent outputs:
    
    {chr(10).join([f"Agent: {agent.name} ({agent.role}){chr(10)}Output: {agent.output}" for agent in agents])}
    
    Please provide a well-structured report that summarizes the findings and insights from all agents.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(report_prompt)
        report = response.text
        
        print("\n📄 Final Report:")
        print("=" * 50)
        print(report)
        print("=" * 50)
        
        # Save report to file
        with open("demo_report.txt", "w") as f:
            f.write(report)
        print(f"\n💾 Report saved to: demo_report.txt")
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
    
    print("\n🎉 Demo completed successfully!")
    print("\n💡 To run the full Streamlit application:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main() 