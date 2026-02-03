"""
Tech Stack Advisor - Helps agents choose appropriate technology based on project scope
"""
from typing import Dict, List, Tuple
from enum import Enum

class ProjectScope(Enum):
    SIMPLE = "simple"           # CLI tools, scripts
    MODERATE = "moderate"       # 2D games, web apps
    COMPLEX = "complex"         # 3D games, ML systems
    ENTERPRISE = "enterprise"   # Large-scale distributed systems

class TechStackAdvisor:
    """
    Analyzes project requirements and recommends optimal tech stacks.
    Prevents agents from using weak tools for big projects.
    """
    
    def __init__(self):
        self.stack_db = self._build_stack_database()
    
    def _build_stack_database(self) -> Dict:
        return {
            "3d_game": {
                "scope": ProjectScope.COMPLEX,
                "recommended": [
                    {
                        "name": "Panda3D",
                        "reason": "Full-featured 3D engine with Python support, physics, shaders",
                        "pros": ["Native Python", "Built-in physics", "MIT license"],
                        "cons": ["Steeper learning curve than Pygame"],
                        "score": 95
                    },
                    {
                        "name": "Godot + GDNative Python",
                        "reason": "Professional game engine with robust 3D rendering and physics",
                        "pros": ["Visual editor", "Advanced physics", "Cross-platform"],
                        "cons": ["Python bindings are experimental"],
                        "score": 90
                    },
                    {
                        "name": "Ursina Engine",
                        "reason": "Python 3D engine built on Panda3D, easier API",
                        "pros": ["Simpler than Panda3D", "Good for prototypes", "Active development"],
                        "cons": ["Less mature"],
                        "score": 85
                    }
                ],
                "avoid": [
                    {
                        "name": "Pygame",
                        "reason": "2D only, no 3D rendering capabilities, would require custom OpenGL"
                    }
                ]
            },
            "2d_game": {
                "scope": ProjectScope.MODERATE,
                "recommended": [
                    {
                        "name": "Pygame",
                        "reason": "Mature 2D game library with good community",
                        "score": 90
                    },
                    {
                        "name": "Arcade",
                        "reason": "Modern 2D game framework with better API than Pygame",
                        "score": 85
                    }
                ]
            },
            "web_app": {
                "scope": ProjectScope.MODERATE,
                "recommended": [
                    {
                        "name": "FastAPI + React",
                        "reason": "Modern async backend with professional frontend",
                        "score": 95
                    },
                    {
                        "name": "Django",
                        "reason": "Batteries-included framework for full-stack apps",
                        "score": 85
                    }
                ]
            },
            "cli_tool": {
                "scope": ProjectScope.SIMPLE,
                "recommended": [
                    {
                        "name": "Click",
                        "reason": "Modern CLI framework with decorators",
                        "score": 95
                    },
                    {
                        "name": "Typer",
                        "reason": "FastAPI-style CLI framework with type hints",
                        "score": 90
                    }
                ]
            }
        }
    
    def analyze_requirements(self, mission: str) -> Tuple[str, ProjectScope, List[Dict]]:
        """
        Analyze project requirements and return category, scope, and recommendations.
        
        Returns:
            (category, scope, recommended_stacks)
        """
        mission_lower = mission.lower()
        
        # Detect 3D game
        if any(keyword in mission_lower for keyword in ["3d", "gta", "neighborhood", "houses", "detailed"]):
            if "game" in mission_lower or "physics" in mission_lower:
                return ("3d_game", ProjectScope.COMPLEX, self.stack_db["3d_game"]["recommended"])
        
        # Detect 2D game
        if any(keyword in mission_lower for keyword in ["2d", "platformer", "sprite"]):
            if "game" in mission_lower:
                return ("2d_game", ProjectScope.MODERATE, self.stack_db["2d_game"]["recommended"])
        
        # Detect web app
        if any(keyword in mission_lower for keyword in ["web", "api", "rest", "website"]):
            return ("web_app", ProjectScope.MODERATE, self.stack_db["web_app"]["recommended"])
        
        # Detect CLI
        if any(keyword in mission_lower for keyword in ["cli", "command", "terminal"]):
            return ("cli_tool", ProjectScope.SIMPLE, self.stack_db["cli_tool"]["recommended"])
        
        # Default to moderate scope
        return ("general", ProjectScope.MODERATE, [])
    
    def get_recommendation_prompt(self, mission: str) -> str:
        """
        Generate a recommendation prompt to inject into agent planning.
        """
        category, scope, stacks = self.analyze_requirements(mission)
        
        if not stacks:
            return ""
        
        prompt = f"\n🎯 TECH STACK RECOMMENDATION (Project Scope: {scope.value.upper()}):\n"
        
        for i, stack in enumerate(stacks[:3], 1):
            prompt += f"\n{i}. **{stack['name']}** (Score: {stack['score']}/100)\n"
            prompt += f"   Reason: {stack['reason']}\n"
            if "pros" in stack:
                prompt += f"   Pros: {', '.join(stack['pros'])}\n"
        
        # Add warnings for avoided tech
        if category in self.stack_db and "avoid" in self.stack_db[category]:
            prompt += "\n⚠️ AVOID:\n"
            for avoid in self.stack_db[category]["avoid"]:
                prompt += f"   ❌ {avoid['name']}: {avoid['reason']}\n"
        
        prompt += f"\n💡 Recommendation: Use {stacks[0]['name']} for best results.\n"
        
        return prompt
