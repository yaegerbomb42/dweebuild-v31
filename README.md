# 🏗️ Dweebuild v31: The Architect Edition

**Tool-Augmented Agents + Test-Driven Development Loop**

A production-ready, multi-agent development system that writes, tests, and validates code autonomously.

---

## 🚀 Features

### The Agentic Triad

1. **The Architect** - Designs project structure with rigorous engineering standards
2. **The Engineer** - Writes production-grade code using ReAct (Reasoning + Acting) loops
3. **The QA Lead** - Runs tests and enforces the "Loop of Truth" (code isn't accepted until tests pass)

### Intelligence Upgrades

- **ReAct Loops**: Agents think, act, and observe iteratively (inspired by Manus/Claude/Copilot)
- **Context Awareness**: Engineers explore the codebase before writing
- **Self-Correction**: Iterative design and implementation
- **Tool Augmentation**: Shell commands, file operations, pytest execution

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- A Groq API key (get one at [console.groq.com](https://console.groq.com))

### Setup

```bash
cd dweebuild_v31
export GROQ_API_KEY='your-key-here'
chmod +x launch_dweebuild.sh
./launch_dweebuild.sh
```

The script will:

1. Create a virtual environment
2. Install dependencies
3. Install Playwright browsers
4. Launch the Streamlit dashboard

---

## 🎯 Usage

1. **Set Your Mission**: Enter a directive like "Create a REST API with FastAPI"
2. **Ignite the Swarm**: Click the button to start the autonomous build process
3. **Watch the Magic**: Monitor agents in real-time as they design, code, and test
4. **Get Results**: Find your built project in `product_build/`

---

## 🏛️ Architecture

```
dweebuild_app/
├── src/dweebuild/
│   ├── core/          # Agent, Tool, Orchestrator, Memory
│   ├── agents/        # Architect, Engineer, QA
│   ├── tools/         # Shell, FileWrite, Pytest
│   └── ui/            # Streamlit Dashboard
├── tests/             # Self-tests
├── pyproject.toml     # Dependencies
└── launch.py          # Entry point
```

### The Loop of Truth™

```
ARCHITECT → designs structure
    ↓
ENGINEER → writes code + tests
    ↓
QA LEAD → runs pytest
    ↓
PASS? → Done ✓
FAIL? → Back to ENGINEER (with error details)
```

---

## 🛠️ Tech Stack

- **LLM**: Groq (llama-3.3-70b-versatile)
- **UI**: Streamlit
- **Browser**: Playwright
- **Testing**: Pytest
- **File Watching**: Watchdog

---

## 🎨 Dashboard

The **Mission Control** interface displays:

- **Swarm Status**: Real-time agent state (IDLE/WORKING/ERROR)
- **System Logs**: Centralized activity feed
- **Task Backlog**: Pending work queue

---

## ⚙️ Configuration

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)

### Customization

Edit `src/dweebuild/core/llm.py` to change:

- Model (default: `llama-3.3-70b-versatile`)
- Temperature (default: 0.2)

---

## 🧪 Example Mission

```
"Build a Python CLI tool that fetches weather data from OpenWeatherMap API and displays it with rich formatting"
```

The agents will:

1. Design the project structure (`src/`, `tests/`, `README.md`)
2. Implement the core logic with proper API handling
3. Write comprehensive unit tests
4. Validate everything passes before completing

---

## 📝 License

MIT License - Build with confidence.

---

## 🙏 Credits

Built with inspiration from:

- Manus (advanced reasoning)
- Claude Code Codex (context awareness)
- GitHub Copilot (codebase understanding)

**Dweebuild v31** - "We are done with toy scripts."
