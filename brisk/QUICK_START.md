# 🚀 Quick Start Guide - Multi-Agent ADK App

## ⚡ Get Started in 3 Steps

### 1. Set up API Key

```bash
# Copy the environment template
cp env_example.txt .env

# Edit .env and add your Google API key
# Get your key from: https://makersuite.google.com/app/apikey
```

### 2. Run the Application

```bash
# Option A: Use the startup script (recommended)
./run_app.sh

# Option B: Manual start
source venv/bin/activate
streamlit run app.py
```

### 3. Test Everything Works

```bash
# Run the demo to see it in action
python demo.py
```

## 🎯 What You Can Do

### Create Agents

- **Research Agent**: Market analysis, competitive intelligence
- **Data Analyst**: Statistical analysis, data visualization
- **Content Writer**: Content creation, copywriting
- **Custom Agents**: Define your own roles and expertise

### Assign Tasks

- Select an agent from the dropdown
- Enter a task description
- Add optional context
- Click "Run Task"

### Generate Reports

- Wait for agents to complete tasks
- Click "Generate Report" in the right column
- Download the report as a text file

## 📁 File Structure

```
brisk/
├── app.py              # Main Streamlit application
├── demo.py             # Demo script (run this first!)
├── run_app.sh          # Easy startup script
├── test_setup.py       # Verify your setup
├── requirements.txt    # Dependencies
├── README.md          # Full documentation
└── venv/              # Virtual environment
```

## 🔧 Troubleshooting

**API Key Issues:**

- Ensure `.env` file exists and has your actual API key
- Get a key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Application Won't Start:**

- Run `python test_setup.py` to diagnose issues
- Make sure virtual environment is activated

**Agents Not Responding:**

- Check agent status in the middle column
- Verify task descriptions are clear and specific

## 💡 Pro Tips

1. **Start with the demo**: Run `python demo.py` to see how it works
2. **Use specific roles**: The more detailed the agent role, the better the results
3. **Provide context**: Add relevant context to help agents understand the task
4. **Generate reports**: Use the report feature to synthesize multiple agent outputs

## 🎉 Ready to Go!

Your multi-agent ADK application is ready! The three-column interface provides:

- **Left**: Agent creation and task management
- **Middle**: Real-time agent outputs and status
- **Right**: Report generation and export

Happy agent building! 🤖
