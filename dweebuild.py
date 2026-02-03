import streamlit as st
import asyncio
import os
import time
import json
import base64
import re
import random
import aiofiles
import subprocess
import shutil
from datetime import datetime
from collections import deque
from groq import AsyncGroq
from playwright.async_api import async_playwright
from duckduckgo_search import DDGS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="dweebuild // ARCHITECT", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;900&display=swap');
    
    :root { --bg: #09090b; --panel: #18181b; --accent: #3b82f6; --success: #22c55e; --error: #ef4444; --text: #f4f4f5; }
    
    .stApp { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    
    /* MODULAR DASHBOARD */
    .dwee-panel {
        background: var(--panel);
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .panel-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        color: #71717a;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    
    /* AGENT CARDS */
    .agent-card {
        background: #000;
        border-left: 3px solid #333;
        padding: 10px;
        margin-bottom: 8px;
        font-family: 'Inter', sans-serif;
    }
    .agent-working { border-color: var(--accent); background: #1e1b4b; }
    .agent-error { border-color: var(--error); background: #450a0a; }
    
    /* TERMINAL OUTPUT */
    .terminal {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        background: #000;
        color: #a1a1aa;
        padding: 10px;
        height: 150px;
        overflow-y: auto;
        white-space: pre-wrap;
        border: 1px solid #27272a;
    }
    .term-cmd { color: #facc15; }
    .term-success { color: var(--success); }
    .term-err { color: var(--error); }
    
    /* BRANDING */
    .brand { font-size: 1.5rem; font-weight: 900; }
    .brand span { color: var(--accent); }
    
</style>
""", unsafe_allow_html=True)

# --- 2. STATE & FILE SYSTEM ---
if "sys" not in st.session_state:
    st.session_state.sys = {
        "agents": {
            "ARCHITECT": {"status": "IDLE", "thought": "Standby", "logs": deque([], maxlen=50)},
            "ENGINEER":  {"status": "IDLE", "thought": "Standby", "logs": deque([], maxlen=50)},
            "QA_LEAD":   {"status": "IDLE", "thought": "Standby", "logs": deque([], maxlen=50)},
        },
        "queue": deque([]),
        "files": {}, # Cache of file structure
        "running": False,
        "active_file": "README.md",
        "mission": "Create a robust python script",
        "last_test_output": "No tests run yet."
    }

# Ensure Project Structure
PROJECT_ROOT = "project"
for d in ["src", "tests", "docs"]:
    os.makedirs(os.path.join(PROJECT_ROOT, d), exist_ok=True)

# Watchdog for Real-time Updates
class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            st.session_state.sys["active_file"] = event.src_path

observer = Observer()
observer.schedule(FileHandler(), path=PROJECT_ROOT, recursive=True)
observer.start()

# --- 3. TOOLBELT (REAL CAPABILITIES) ---

async def run_cmd(cmd):
    """Execute shell command."""
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode().strip() + stderr.decode().strip()
    except Exception as e: return str(e)

async def tool_write(path, content):
    """Smart File Write."""
    full_path = os.path.join(PROJECT_ROOT, path) if not path.startswith(PROJECT_ROOT) else path
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    async with aiofiles.open(full_path, "w") as f: await f.write(content)
    return f"Wrote {len(content)} bytes to {path}"

async def tool_read(path):
    """Smart File Read."""
    full_path = os.path.join(PROJECT_ROOT, path) if not path.startswith(PROJECT_ROOT) else path
    if os.path.exists(full_path):
        async with aiofiles.open(full_path, "r") as f: return await f.read()
    return ""

async def tool_test():
    """Run Pytest."""
    return await run_cmd(f"pytest {PROJECT_ROOT}/tests")

# --- 4. BRAIN (GROQ) ---

async def groq_call(system, user):
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    try:
        chat = await client.chat.completions.create(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            model="llama-3.3-70b-versatile", temperature=0.2
        )
        return chat.choices[0].message.content
    except Exception as e: return f"ERROR: {str(e)}"

def log(agent, msg, type="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    css = "term-cmd" if type=="CMD" else "term-err" if type=="ERR" else "term-success" if type=="OK" else ""
    st.session_state.sys["agents"][agent]["logs"].append(f"[{ts}] <span class='{css}'>{msg}</span>")

# --- 5. AGENT LOOPS ---

async def architect_loop():
    agent = "ARCHITECT"
    sys = st.session_state.sys
    
    # Trigger: Running, Queue Empty, No README
    if sys["running"] and not sys["queue"] and not os.path.exists(f"{PROJECT_ROOT}/README.md"):
        sys["agents"][agent]["status"] = "WORKING"
        sys["agents"][agent]["thought"] = "Designing System Architecture..."
        
        log(agent, f"Analyzing: {sys['mission']}")
        
        prompt = f"""
        MISSION: {sys['mission']}
        
        Design a PRODUCTION-READY Python architecture.
        1. Define the `src/` modules.
        2. Define the `tests/` modules.
        3. Define the tasks to build them.
        
        Return JSON ONLY:
        {{
            "files": {{
                "README.md": "# Project Title...",
                "src/main.py": "# Entry point",
                "src/utils.py": "# Helpers",
                "tests/test_main.py": "# Tests"
            }},
            "tasks": ["Implement src/utils.py", "Implement src/main.py", "Run Tests"]
        }}
        """
        res = await groq_call("You are a Senior Staff Engineer. Design robust systems.", prompt)
        
        try:
            data = json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
            
            # Create Skeleton
            for path, content in data["files"].items():
                await tool_write(path, content)
                sys["files"][path] = "Init"
            
            # Queue Tasks
            for t in data["tasks"]: sys["queue"].append(t)
            
            log(agent, "Architecture Locked.", "OK")
            sys["active_file"] = f"{PROJECT_ROOT}/README.md"
            
        except Exception as e:
            log(agent, f"Design Failed: {e}", "ERR")
            
    sys["agents"][agent]["status"] = "IDLE"

async def engineer_loop():
    agent = "ENGINEER"
    sys = st.session_state.sys
    
    if sys["running"] and sys["queue"]:
        task = sys["queue"].popleft()
        
        # Check if task is for QA
        if "test" in task.lower():
            sys["queue"].appendleft(task) # Put back for QA
            return

        sys["agents"][agent]["status"] = "WORKING"
        sys["agents"][agent]["thought"] = f"Engineering: {task}"
        log(agent, f"Starting: {task}", "CMD")
        
        # 1. Identify Target File
        target = "src/main.py" # Default
        if "utils" in task.lower(): target = "src/utils.py"
        
        # 2. Read Context
        current_code = await tool_read(target)
        project_tree = await run_cmd(f"find {PROJECT_ROOT} -maxdepth 2 -not -path '*/.*'")
        
        # 3. Write Code
        prompt = f"""
        TASK: {task}
        TARGET FILE: {target}
        PROJECT FILES:
        {project_tree}
        
        CURRENT CONTENT:
        {current_code}
        
        INSTRUCTION: Write production-grade code. No placeholders. Include docstrings.
        Return ONLY the full code in a ```python``` block.
        """
        code = await groq_call("You are a Principal Python Developer.", prompt)
        
        match = re.search(r"```python(.*?)```", code, re.DOTALL)
        if match:
            clean_code = match.group(1).strip()
            await tool_write(target, clean_code)
            log(agent, f"Committed to {target}", "OK")
            sys["active_file"] = f"{PROJECT_ROOT}/{target}"
            
            # 4. Auto-Queue Unit Test Creation
            test_file = target.replace("src", "tests").replace(".py", "_test.py")
            if not os.path.exists(f"{PROJECT_ROOT}/{test_file}"):
                sys["queue"].appendleft(f"Create unit tests for {target} in {test_file}")
                
        sys["agents"][agent]["status"] = "IDLE"

async def qa_loop():
    agent = "QA_LEAD"
    sys = st.session_state.sys
    
    if sys["running"] and sys["queue"]:
        task = sys["queue"][0] # Peek
        
        # QA only takes "Test" tasks
        if "test" not in task.lower() and "verify" not in task.lower():
            return
            
        sys["queue"].popleft() # Consume
        sys["agents"][agent]["status"] = "WORKING"
        sys["agents"][agent]["thought"] = "Running Test Suite..."
        
        log(agent, "Executing Pytest...", "CMD")
        output = await tool_test()
        sys["last_test_output"] = output
        
        if "failed" in output.lower() or "error" in output.lower():
            log(agent, "Tests FAILED. Rejecting code.", "ERR")
            sys["queue"].append(f"Fix failing tests: {output[-100:]}")
        else:
            log(agent, "Tests PASSED. Deployment Ready.", "OK")
            
        sys["agents"][agent]["status"] = "IDLE"

# --- 6. MAIN BRIDGE ---
async def main_loop():
    await asyncio.gather(architect_loop(), engineer_loop(), qa_loop())

def run_sync():
    asyncio.run(main_loop())

# --- 7. UI LAYOUT ---

c1, c2 = st.columns([1, 3])
with c1:
    st.markdown("<div class='brand'>dweebuild <span>31</span></div>", unsafe_allow_html=True)
with c2:
    st.session_state.sys["mission"] = st.text_input("DIRECTIVE", st.session_state.sys["mission"], label_visibility="collapsed")

# Control Bar
b1, b2, b3 = st.columns([1, 1, 4])
if b1.button("IGNITE SWARM", type="primary", use_container_width=True):
    st.session_state.sys["running"] = True
if b2.button("HALT", use_container_width=True):
    st.session_state.sys["running"] = False

# Main Dashboard
col_left, col_mid, col_right = st.columns([1.2, 2, 1.2])

# PANEL 1: ENGINEERING TEAM
with col_left:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>SWARM STATUS</div>", unsafe_allow_html=True)
    
    for name, data in st.session_state.sys["agents"].items():
        css = "agent-working" if data["status"] == "WORKING" else ""
        st.markdown(f"""
        <div class='agent-card {css}'>
            <div style='display:flex; justify-content:space-between; font-size:12px; font-weight:bold;'>
                <span>{name}</span>
                <span style='opacity:0.7'>{data['status']}</span>
            </div>
            <div style='font-size:11px; margin-top:4px; color:#a1a1aa;'>{data['thought']}</div>
        </div>
        """, unsafe_allow_html=True)
        # Log Window
        log_html = "<br>".join(list(data['logs']))
        st.markdown(f"<div class='terminal' style='height:80px;'>{log_html}</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# PANEL 2: CODEBASE
with col_mid:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    active_f = st.session_state.sys["active_file"]
    st.markdown(f"<div class='panel-header'>EDITOR // {active_f}</div>", unsafe_allow_html=True)
    
    content = "# File not found"
    full_path = active_f if active_f.startswith("project") else f"project/{active_f}"
    if os.path.exists(full_path):
        with open(full_path, "r") as f: content = f.read()
        
    st.code(content, language="python", line_numbers=True)
    st.markdown("</div>", unsafe_allow_html=True)

# PANEL 3: QA & TASKS
with col_right:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>QA TERMINAL</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='terminal'>{st.session_state.sys['last_test_output']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>TASK BACKLOG</div>", unsafe_allow_html=True)
    tasks = list(st.session_state.sys["queue"])
    if tasks:
        for i, t in enumerate(tasks):
            st.markdown(f"<div style='font-size:11px; border-bottom:1px solid #333; padding:4px;'>{i+1}. {t}</div>", unsafe_allow_html=True)
    else:
        st.caption("All tasks complete.")
    st.markdown("</div>", unsafe_allow_html=True)

# Runner
if st.session_state.sys["running"]:
    run_sync()
    time.sleep(1)
    st.rerun()

