import streamlit as st
import asyncio
import os
import time
from collections import deque
from dweebuild.core.orchestrator import Orchestrator
from dweebuild.agents.architect import ArchitectAgent
from dweebuild.agents.engineer import EngineerAgent
from dweebuild.agents.qa import QAAgent

# --- CONFIGURATION ---
st.set_page_config(page_title="dweebuild // ORBIT", layout="wide", initial_sidebar_state="collapsed")

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
        min-height: 200px;
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
    .agent-success { border-color: var(--success); background: #064e3b; }
    
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

# --- STATE MANAGEMENT ---
if "orc" not in st.session_state:
    # Initialize Orchestrator and Agents
    orc = Orchestrator()
    
    # Define where the 'product' will be built
    product_root = os.path.abspath("product_build")
    
    # Initialize Agents
    architect = ArchitectAgent("Standby", product_root)
    engineer = EngineerAgent("Standby", product_root)
    qa = QAAgent("Standby", product_root)
    
    orc.register_agent(architect)
    orc.register_agent(engineer)
    orc.register_agent(qa)
    
    st.session_state.orc = orc
    st.session_state.mission_input = ""
    st.session_state.is_running = False

# --- UI LAYOUT ---

c1, c2 = st.columns([1, 4])
with c1:
    st.markdown("<div class='brand'>dweebuild <span>31</span></div>", unsafe_allow_html=True)
with c2:
    mission = st.text_input("DIRECTIVE", key="mission_input", placeholder="Build a python app that...", label_visibility="collapsed")

# Control Bar
b1, b2, b3 = st.columns([1, 1, 4])
if b1.button("IGNITE SWARM", type="primary", use_container_width=True):
    if mission:
        st.session_state.orc.start()
        # Initial Kickoff: Send mission to Architect
        # In a real app, Orchestrator routes this. Here we force it for the MVP loop.
        st.session_state.orc.agents["ARCHITECT"].mission = mission
        st.session_state.orc.add_task(f"Design: {mission}")
        st.session_state.is_running = True
    else:
        st.error("Mission required.")

if b2.button("HALT", use_container_width=True):
    st.session_state.orc.stop()
    st.session_state.is_running = False

# Main Dashboard
col_left, col_mid, col_right = st.columns([1.5, 2, 1.5])

# PANEL 1: AGENT STATUS
with col_left:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>SWARM STATUS</div>", unsafe_allow_html=True)
    
    for name, agent in st.session_state.orc.agents.items():
        css = ""
        if agent.status == "WORKING": css = "agent-working"
        elif agent.status == "ERROR": css = "agent-error"
        elif agent.status == "SUCCESS": css = "agent-success"
        
        st.markdown(f"""
        <div class='agent-card {css}'>
            <div style='display:flex; justify-content:space-between; font-size:12px; font-weight:bold;'>
                <span>{name}</span>
                <span style='opacity:0.7'>{agent.status}</span>
            </div>
            <div style='font-size:11px; margin-top:4px; color:#a1a1aa;'>{agent.thought}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mini Log
        logs = list(agent.logs)[-3:]
        for l in logs:
             st.markdown(f"<div style='font-size:9px; color:#666;'>{l}</div>", unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)

# PANEL 2: LIVE SYSTEM LOGS
with col_mid:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown(f"<div class='panel-header'>SYSTEM LOGS</div>", unsafe_allow_html=True)
    
    # Combine logs from memory
    logs = st.session_state.orc.memory.get_logs(20)
    log_html = ""
    for entry in logs:
        color = "#a1a1aa"
        if entry['level'] == "SUCCESS": color = "#22c55e"
        if entry['level'] == "WARN": color = "#facc15"
        if entry['level'] == "ERR": color = "#ef4444"
        
        log_html += f"<div style='color:{color}; margin-bottom:2px;'>[{entry['timestamp']}] <b>[{entry['source']}]</b> {entry['message']}</div>"

    st.markdown(f"<div class='terminal' style='height:400px;'>{log_html}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# PANEL 3: TASK QUEUE
with col_right:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>TASK BACKLOG</div>", unsafe_allow_html=True)
    
    tasks = list(st.session_state.orc.task_queue)
    if tasks:
        for i, t in enumerate(tasks):
            st.markdown(f"<div style='font-size:11px; border-bottom:1px solid #333; padding:4px;'>{i+1}. {t}</div>", unsafe_allow_html=True)
    else:
        st.caption("No pending tasks.")
        
    st.markdown("</div>", unsafe_allow_html=True)

# --- ASYNC RUNNER ---
async def run_swarm_step():
    # This is a very simplified 'tick' that would normally belong in the Orchestrator
    # For Streamlit, we manually drive the agents so we can update the UI
    
    orc = st.session_state.orc
    # 1. Architect Logic 
    # If Architect sent us tasks, catch them
    arch = orc.agents["ARCHITECT"]
    if arch.status == "IDLE" and orc.task_queue and "Design" in orc.task_queue[0]:
        task = orc.task_queue.popleft()
        res = await arch.run(task)
        orc.memory.add_log("ARCHITECT", res, "SUCCESS")
        # Parse 'tasks' from result? In this MVP we just hardcode the flow:
        # After Design, add 'Build' tasks
        if "Tasks generated" in res:
             # Hacky: Just assume we need to build src/main.py for demo
             orc.add_task("Implement src/main.py")

    # 2. Engineer Logic
    eng = orc.agents["ENGINEER"]
    if eng.status == "IDLE" and orc.task_queue and ("Implement" in orc.task_queue[0] or "Fix" in orc.task_queue[0]):
        task = orc.task_queue.popleft()
        res = await eng.run(task)
        orc.memory.add_log("ENGINEER", res, "SUCCESS")
        # After Build, add QA task
        orc.add_task("Verify build")

    # 3. QA Logic
    qa_agent = orc.agents["QA_LEAD"]
    if qa_agent.status == "IDLE" and orc.task_queue and "Verify" in orc.task_queue[0]:
        task = orc.task_queue.popleft()
        res = await qa_agent.run(task)
        
        if "FAILURE" in res:
            orc.memory.add_log("QA", res, "ERR")
            orc.add_task("Fix failing tests") # Loop back to Engineer
        else:
            orc.memory.add_log("QA", res, "SUCCESS")
            # Done!

if st.session_state.is_running:
    asyncio.run(run_swarm_step())
    time.sleep(1) # Pace the loop
    st.rerun()
