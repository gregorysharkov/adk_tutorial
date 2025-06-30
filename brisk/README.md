# 🤖 Multi-Agent ADK Application

A Streamlit-based multi-agent application using Google's Generative AI (ADK) with a three-column interface for agent management, task execution, and report generation.

## Features

- **Three-Column Layout**:
  - Left: Agent creation and task assignment
  - Middle: Real-time agent outputs
  - Right: Report generation and export
- **Multi-Agent System**: Create and manage multiple AI agents with different roles
- **Real-time Processing**: Agents work in background threads
- **Report Generation**: Automatic report creation from agent outputs
- **Export Functionality**: Download reports as text files

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Key

1. Get your Google Generative AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root:
   ```bash
   cp env_example.txt .env
   ```
3. Edit `.env` and add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### 3. Run the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

### Creating Agents

1. In the left column, fill in:
   - **Agent Name**: A descriptive name for your agent
   - **Agent Role**: Detailed description of the agent's expertise and responsibilities
   - **Model**: Choose from available Gemini models
2. Click "Create Agent"

### Assigning Tasks

1. Select an agent from the dropdown
2. Enter a task description
3. Optionally provide additional context
4. Click "Run Task"

### Monitoring Outputs

- The middle column shows real-time status and outputs from all agents
- Agents show their current status: idle, working, completed, or error
- Expand each agent to view their detailed output

### Generating Reports

1. Wait for agents to complete their tasks
2. Click "Generate Report" in the right column
3. The system will create a comprehensive report based on all agent outputs
4. Use the download button to save the report as a text file

## Agent Examples

### Research Agent

- **Role**: "Expert researcher specializing in market analysis, competitive intelligence, and industry trends. Skilled at gathering and synthesizing information from multiple sources."
- **Tasks**: Market research, competitor analysis, industry reports

### Data Analyst Agent

- **Role**: "Data scientist with expertise in statistical analysis, data visualization, and predictive modeling. Skilled at interpreting complex datasets and extracting actionable insights."
- **Tasks**: Data analysis, statistical reports, trend identification

### Content Writer Agent

- **Role**: "Professional content writer with expertise in creating engaging, informative content for various audiences. Skilled at adapting tone and style for different purposes."
- **Tasks**: Content creation, copywriting, documentation

## Technical Details

- **Framework**: Streamlit
- **AI Provider**: Google Generative AI (Gemini models)
- **Architecture**: Multi-threaded agent processing
- **State Management**: Streamlit session state
- **UI**: Responsive three-column layout

## Troubleshooting

### API Key Issues

- Ensure your `.env` file is in the correct location
- Verify your API key is valid and has sufficient quota
- Check that the key has access to the selected Gemini models

### Agent Not Responding

- Check the agent's status in the middle column
- Verify the task description is clear and specific
- Ensure the agent's role is well-defined

### Performance Issues

- Consider using faster models (gemini-1.5-flash) for quick responses
- Limit the number of concurrent agents if experiencing slowdowns
- Monitor API usage and quotas

## License

This project is for educational and development purposes.
