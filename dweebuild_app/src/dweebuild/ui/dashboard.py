import streamlit as st
import asyncio
import os
import time
from collections import deque
from dweebuild.core.orchestrator import Orchestrator
from dweebuild.core.modes import WorkMode
from dweebuild.core.config import config
from dweebuild.core.persistence import SessionManager
from dweebuild.agents.architect import ArchitectAgent
from dweebuild.agents.engineer import EngineerAgent
from dweebuild.agents.qa import QAAgent
from dweebuild.tools.std_tools import *

# === CONFIGURATION ===
st.set_page_config(page_title="dweebuild // ORBIT", layout="wide", initial_sidebar_state="collapsed")

# === VIBRANT PREMIUM UI ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;900&display=swap');
    
    :root { 
        --bg: #0a0a0f; 
        --panel: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        --accent-start: #00d4ff; 
        --accent-end: #a855f7;
        --success: #84cc16; 
        --warning: #fbbf24;
        --error: #f43f5e; 
        --text: #f4f4f5;
    }
    
    .stApp { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    
    /* ANIMATED GRADIENT BACKGROUND */
    body {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0a0a0f 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* PANELS */
    .dwee-panel {
        background: linear-gradient(135deg, rgba(26,26,46,0.8) 0%, rgba(22,33,62,0.8) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
    }
    
    .panel-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        text-transform: uppercase;
        background: linear-gradient(90deg, var(--accent-start), var(--accent-end));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
        letter-spacing: 2px;
        font-weight: 700;
    }
    
    /* AGENT CARDS WITH AVATARS */
    .agent-card {
        background: rgba(0,0,0,0.6);
        border-left: 3px solid #333;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        opacity: 0;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .agent-idle { border-color: #444; }
    .agent-working { 
        border-color: var(--accent-start);
        background: rgba(0, 212, 255, 0.1);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    .agent-error { 
        border-color: var(--error); 
        background: rgba(244, 63, 94, 0.1); 
    }
    .agent-success {
        border-color: var(--success);
        background: rgba(132, 204, 22, 0.1);
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
        50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.6); }
    }
    
    .agent-avatar {
        font-size: 24px;
        display: inline-block;
        margin-right: 8px;
        filter: drop-shadow(0 0 10px currentColor);
    }
    
    /* TERMINAL */
    .terminal {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        background: #000;
        color: #a1a1aa;
        padding: 12px;
        height: 200px;
        overflow-y: auto;
        white-space: pre-wrap;
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 6px;
    }
    .term-cmd { color: #fbbf24; font-weight: bold; }
    .term-success { color: var(--success); }
    .term-err { color: var(--error); }
    .term-info { color: #00d4ff; }
    
    /* BRANDING */
    .brand { 
        font-size: 2rem; 
        font-weight: 900;
        background: linear-gradient(90deg, var(--accent-start), var(--accent-end));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* METRICS */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(168, 85, 247, 0.1));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(90deg, var(--accent-start), var(--accent-end));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 10px;
        text-transform: uppercase;
        color: #71717a;
        letter-spacing: 1px;
    }
    
    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, var(--accent-start), var(--accent-end)) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    
    /* MODE BADGES */
    .mode-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .mode-single { background: rgba(132, 204, 22, 0.2); color: var(--success); border: 1px solid var(--success); }
    .mode-autonomous { background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid #a855f7; }
    .mode-supervised { background: rgba(251, 191, 36, 0.2); color: var(--warning); border: 1px solid var(--warning); }
    
</style>
""", unsafe_allow_html=True)

# === STATE MANAGEMENT ===
if "orc" not in st.session_state:
    # Check environment
    is_valid, missing = config.validate()
    if not is_valid:
        st.error(f"⚠️ Missing required configuration: {', '.join(missing)}")
        st.info("💡 Please create a `.env` file with your API keys. See `.env.template` for reference.")
        st.stop()
    
    # Select mode
    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = WorkMode.SINGLE
    
    orc = Orchestrator(mode=st.session_state.selected_mode)
    product_root = os.path.abspath("product_build")
    
    # Initialize Agents with ALL tools
    arch = ArchitectAgent("Standby", product_root)
    eng = EngineerAgent("Standby", product_root)
    qa = QAAgent("Standby", product_root)
    
    # Equip additional tools
    for agent in [arch, eng, qa]:
        agent.equip(FileReadTool(product_root))
        agent.equip(GrepTool(product_root))
        agent.equip(GitTool(product_root))
        agent.equip(PipTool())
        agent.equip(WebSearchTool())
        agent.equip(DirectoryTool(product_root))
        agent.equip(LintTool(product_root))
        agent.equip(FormatTool(product_root))
        agent.equip(ComplexityTool(product_root))
        agent.equip(CoverageTool(product_root))
    
    orc.register_agent(arch)
    orc.register_agent(eng)
    orc.register_agent(qa)
    
    st.session_state.orc = orc
    st.session_state.session_manager = SessionManager()
    st.session_state.mission_input = ""
    st.session_state.is_running = False

# === HEADER ===
c1, c2 = st.columns([1, 5])
with c1:
    st.markdown("<div class='brand'>dweeb <span>⚡</span></div>", unsafe_allow_html=True)
with c2:
    mode_name = st.session_state.orc.mode_config.mode.value.upper()
    mode_class = f"mode-{st.session_state.orc.mode_config.mode.value}"
    st.markdown(f"<span class='mode-badge {mode_class}'>{mode_name} MODE</span>", unsafe_allow_html=True)

mission = st.text_input("🎯 MISSION DIRECTIVE", key="mission_input", placeholder="Build a Python CLI tool that...", label_visibility="collapsed")

# === CONTROL BAR ===
b1, b2, b3, b4, b5 = st.columns([1.5, 1, 1, 1, 3])

if b1.button("🚀 IGNITE SWARM", type="primary", use_container_width=True):
    if mission:
        st.session_state.orc.start()
        st.session_state.orc.agents["ARCHITECT"].mission = mission
        st.session_state.orc.add_task(f"Design: {mission}")
        st.session_state.is_running = True
    else:
        st.warning("Mission required.")

if b2.button("⏸️ HALT", use_container_width=True):
    st.session_state.orc.stop()
    st.session_state.is_running = False

mode_options = {"Single": WorkMode.SINGLE, "Auto": WorkMode.AUTONOMOUS, "Supervised": WorkMode.SUPERVISED}
selected = b3.selectbox("Mode", list(mode_options.keys()), label_visibility="collapsed")
if mode_options[selected] != st.session_state.orc.mode_config.mode:
    st.session_state.orc.mode_config.mode = mode_options[selected]
    st.rerun()

if b4.button("💾 SAVE", use_container_width=True):
    state = {
        "mode": st.session_state.orc.mode_config.mode.value,
        "agents": st.session_state.orc.agents,
        "tasks": list(st.session_state.orc.task_queue),
        "logs": st.session_state.orc.memory.get_logs(),
        "iteration_count": st.session_state.orc.iteration_count
    }
    path = st.session_state.session_manager.save_session("dweeb_session", state)
    st.success(f"Saved to {path}")

# === MAIN DASHBOARD === 
col_left, col_mid, col_right = st.columns([1.5, 2.5, 1.5])

# PANEL 1: SWARM STATUS
with col_left:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>⚡ Swarm Status</div>", unsafe_allow_html=True)
    
    avatars = {"ARCHITECT": "🏗️", "ENGINEER": "🛠️", "QA_LEAD": "🔬"}
    
    for name, agent in st.session_state.orc.agents.items():
        css = "agent-idle"
        if agent.status == "WORKING": css = "agent-working"
        elif agent.status == "ERROR": css = "agent-error"
        elif agent.status == "SUCCESS": css = "agent-success"
        
        avatar = avatars.get(name, "🤖")
        
        st.markdown(f"""
        <div class='agent-card {css}'>
            <div style='display:flex; align-items:center; justify-content:space-between;'>
                <div>
                    <span class='agent-avatar'>{avatar}</span>
                    <span style='font-weight:bold; font-size:13px;'>{name}</span>
                </div>
                <span style='font-size:10px; opacity:0.8; text-transform:uppercase;'>{agent.status}</span>
            </div>
            <div style='font-size:11px; margin-top:8px; color:#a1a1aa; font-style:italic;'>{agent.thought}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # METRICS
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>📊 Metrics</div>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{len(st.session_state.orc.task_queue)}</div>
            <div class='metric-label'>Tasks Queue</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{st.session_state.orc.iteration_count}</div>
            <div class='metric-label'>Iterations</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# PANEL 2: SYSTEM LOGS
with col_mid:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>📜 System Logs</div>", unsafe_allow_html=True)
    
    logs = st.session_state.orc.memory.get_logs(30)
    log_html = ""
    for entry in logs:
        color_class = "term-info"
        if entry['level'] == "SUCCESS": color_class = "term-success"
        if entry['level'] == "WARN": color_class = "term-cmd"
        if entry['level'] == "ERR": color_class = "term-err"
        
        log_html += f"<span class='{color_class}'>[{entry['timestamp']}] [{entry['source']}] {entry['message']}</span>\n"

    st.markdown(f"<div class='terminal'>{log_html}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# PANEL 3: TASK QUEUE & FILE TREE
with col_right:
    st.markdown("<div class='dwee-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>📋 Task Backlog</div>", unsafe_allow_html=True)
    
    tasks = list(st.session_state.orc.task_queue)
    if tasks:
        for i, t in enumerate(tasks):
            st.markdown(f"<div style='font-size:11px; border-bottom:1px solid #333; padding:6px; color:#a1a1aa;'>{i+1}. {t}</div>", unsafe_allow_html=True)
    else:
        st.caption("🎉 All tasks complete.")
    st.markdown("</div>", unsafe_allow_html=True)

# === ASYNC RUNNER ===
async def run_swarm():
    await st.session_state.orc.run_concurrent()
    st.session_state.orc.iteration_count += 1

if st.session_state.is_running and st.session_state.orc.should_continue():
    asyncio.run(run_swarm())
    time.sleep(0.5)
    st.rerun()
