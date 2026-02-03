#!/usr/bin/env python3
"""
Extended test runner - Build until complete
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dweebuild_app', 'src'))

from dweebuild.core.orchestrator import Orchestrator
from dweebuild.core.modes import WorkMode
from dweebuild.core.config import config
from dweebuild.agents.architect import ArchitectAgent
from dweebuild.agents.engineer import EngineerAgent
from dweebuild.agents.qa import QAAgent
from dweebuild.tools.std_tools import *

async def main():
    print("🚀 DWEEBUILD v31.2 - FULL AUTONOMOUS BUILD")
    print("=" * 60)
    print("MISSION: Build complete monkey-banana physics game")
    print("MODE: AUTONOMOUS (unlimited iterations)")
    print("=" * 60)
    
    # Validate config
    is_valid, missing = config.validate()
    if not is_valid:
        print(f"❌ Missing config: {', '.join(missing)}")
        return
    
    mission = """
Build a chaotic monkey-banana physics game with:
- GTA-style 3D neighborhood with 10 detailed houses
- Player controls a monkey searching for bananas
- Funny physics: speed boost on banana collection, destructible houses
- Use Panda3D for 3D rendering (NOT Pygame)
- Include collision detection, scoring, HUD
- Comprehensive physics system
- Make it CHAOTIC and FUN
"""
    
    # Setup orchestrator in AUTONOMOUS mode
    orc = Orchestrator(mode=WorkMode.AUTONOMOUS)
    orc.mode_config.max_iterations = 50  # Extended for full build
    
    product_root = os.path.abspath("product_build")
    os.makedirs(product_root, exist_ok=True)
    
    # Initialize agents
    print("\n🤖 Initializing intelligent agent swarm...")
    arch = ArchitectAgent(mission, product_root)
    eng = EngineerAgent(mission, product_root)
    qa = QAAgent(mission, product_root)
    
    # Equip full toolbelt
    for agent in [arch, eng, qa]:
        agent.equip(FileReadTool(product_root))
        agent.equip(GrepTool(product_root))
        agent.equip(GitTool(product_root))
        agent.equip(PipTool())
        agent.equip(WebSearchTool())
        agent.equip(DirectoryTool(product_root))
        agent.equip(LintTool(product_root))
        agent.equip(FormatTool(product_root))
    
    orc.register_agent(arch)
    orc.register_agent(eng)
    orc.register_agent(qa)
    
    print("✅ Agents equipped with TechStackAdvisor and full toolbelt")
    
    # Display tech recommendation
    print(f"\n{arch.tech_recommendation}")
    
    # Start orchestration
    orc.start()
    orc.add_task(f"Design professional 3D game architecture: {mission}")
    
    print("\n🔥 Starting autonomous build (monitoring until complete)...\n")
    
    start_time = time.time()
    iteration = 0
    
    while orc.should_continue() and iteration < 50:
        iteration += 1
        elapsed = int(time.time() - start_time)
        
        print(f"\n{'='*60}")
        print(f"⚡ ITERATION {iteration} | Elapsed: {elapsed}s")
        print(f"{'='*60}")
        
        # Run concurrent execution
        await orc.run_concurrent()
        
        # Status summary
        print(f"\n📊 AGENT STATUS:")
        for name, agent in orc.agents.items():
            emoji = {"IDLE": "💤", "WORKING": "⚡", "ERROR": "❌", "SUCCESS": "✅"}.get(agent.status, "🤖")
            print(f"  {emoji} {name:12s} ({agent.status:8s}): {agent.thought[:50]}...")
        
        print(f"\n📋 Queue: {len(orc.task_queue)} tasks pending")
        
        # Recent activity
        logs = orc.memory.get_logs(3)
        if logs:
            print(f"\n📜 Recent Activity:")
            for log in logs:
                level_emoji = {"SUCCESS": "✅", "ERR": "❌", "WARN": "⚠️", "INFO": "ℹ️"}.get(log['level'], "•")
                print(f"  {level_emoji} [{log['source']}] {log['message'][:70]}...")
        
        # Check for completion
        all_idle = all(a.status in ["IDLE", "SUCCESS"] for a in orc.agents.values())
        if all_idle and len(orc.task_queue) == 0:
            print("\n✅ All agents idle and queue empty!")
            break
        
        await asyncio.sleep(2)
    
    elapsed = int(time.time() - start_time)
    print(f"\n{'='*60}")
    print(f"🎉 BUILD COMPLETE | Total time: {elapsed}s | Iterations: {iteration}")
    print(f"{'='*60}")
    
    # Summary
    print(f"\n📁 Output: {product_root}")
    print(f"\n🔍 Files created:")
    os.system(f"find {product_root} -type f | head -30")
    
    print(f"\n\n🎮 GAME STATUS:")
    if os.path.exists(f"{product_root}/requirements.txt"):
        print("  ✅ requirements.txt found")
        with open(f"{product_root}/requirements.txt") as f:
            deps = f.read()
            if "panda3d" in deps.lower():
                print("  ✅ Panda3D confirmed (intelligent tech selection!)")
            else:
                print("  ⚠️ No Panda3D in requirements")
    
    if os.path.exists(f"{product_root}/README.md"):
        print("  ✅ README.md found")
    
    python_files = len([f for f in os.listdir(product_root) if f.endswith('.py')]) if os.path.exists(product_root) else 0
    print(f"  ✅ {python_files} Python files created")

if __name__ == "__main__":
    asyncio.run(main())
