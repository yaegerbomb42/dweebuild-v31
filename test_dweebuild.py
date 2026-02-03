#!/usr/bin/env python3
"""
Test runner for Dweebuild - Direct Python execution
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dweebuild_app', 'src'))

from dweebuild.core.orchestrator import Orchestrator
from dweebuild.core.modes import WorkMode
from dweebuild.core.config import config
from dweebuild.agents.architect import ArchitectAgent
from dweebuild.agents.engineer import EngineerAgent
from dweebuild.agents.qa import QAAgent
from dweebuild.tools.std_tools import *

async def main():
    print("🚀 DWEEBUILD v31.1 - Direct Test Mode")
    print("=" * 60)
    
    # Validate config
    is_valid, missing = config.validate()
    if not is_valid:
        print(f"❌ Missing config: {', '.join(missing)}")
        return
    
    print("✅ Configuration valid")
    print(f"📡 Using Groq with key: {config.groq_api_key[:20]}...")
    
    # Mission
    mission = """
Build a chaotic monkey-banana physics game:
- GTA-style neighborhood with 10 houses
- Player controls a monkey searching for bananas
- Funny physics: speed boost on banana eat, destructible houses
- Use Pygame for 2D or Panda3D for 3D
- Include collision, scoring, HUD
- Make it CHAOTIC and FUN
"""
    
    print(f"\n📋 MISSION:\n{mission}")
    print("=" * 60)
    
    # Setup orchestrator in AUTONOMOUS mode
    orc = Orchestrator(mode=WorkMode.AUTONOMOUS)
    orc.mode_config.max_iterations = 20  # Limit for testing
    
    product_root = os.path.abspath("product_build")
    os.makedirs(product_root, exist_ok=True)
    
    # Initialize agents with ALL tools
    print("\n🤖 Initializing agents...")
    arch = ArchitectAgent(mission, product_root)
    eng = EngineerAgent(mission, product_root)
    qa = QAAgent(mission, product_root)
    
    # Equip tools
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
    
    print("✅ Agents registered with full toolbelt")
    
    # Start orchestration
    orc.start()
    orc.add_task(f"Design architecture: {mission}")
    
    print("\n🔥 Starting autonomous build...\n")
    
    # Main loop
    iteration = 0
    while orc.should_continue():
        iteration += 1
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}")
        print(f"{'='*60}")
        
        # Run concurrent execution
        await orc.run_concurrent()
        
        # Print status
        print("\n📊 STATUS:")
        for name, agent in orc.agents.items():
            status_emoji = {
                "IDLE": "💤",
                "WORKING": "⚡",
                "ERROR": "❌",
                "SUCCESS": "✅"
            }.get(agent.status, "🤖")
            print(f"  {status_emoji} {name}: {agent.status} - {agent.thought[:60]}...")
        
        print(f"\n📋 Tasks in queue: {len(orc.task_queue)}")
        
        # Print recent logs
        logs = orc.memory.get_logs(5)
        if logs:
            print("\n📜 Recent logs:")
            for log in logs:
                print(f"  [{log['level']}] {log['source']}: {log['message'][:80]}...")
        
        # Small delay to avoid hammering the API
        await asyncio.sleep(2)
        
        # Safety: stop if stuck
        if iteration > orc.mode_config.max_iterations:
            print("\n⚠️ Max iterations reached. Stopping.")
            break
    
    print("\n" + "="*60)
    print("🎉 BUILD COMPLETE")
    print("="*60)
    print(f"\n📁 Output directory: {product_root}")
    print("\n🔍 Final agent status:")
    for name, agent in orc.agents.items():
        print(f"  • {name}: {agent.status}")

if __name__ == "__main__":
    asyncio.run(main())
