"""
Arnold Fitness CLI - Orchestrator Selector
Interactive orchestrator selection for CLI modes
"""

from typing import Dict, Optional
from src.orchestrator.orchestrator_factory import OrchestratorFactory, OrchestratorType
from .colors import ArnoldColors


class OrchestratorSelector:
    """Interactive selector for choosing orchestrator type in CLI modes"""
    
    @staticmethod
    def interactive_select() -> str:
        """
        Interactive orchestrator selection with user-friendly descriptions
        
        Returns:
            Selected orchestrator type as string
        """
        print(f"{ArnoldColors.HEADER}🎯 Select Orchestrator Mode{ArnoldColors.RESET}\\n")
        
        # Get available orchestrators with descriptions
        orchestrators = OrchestratorFactory.list_available_orchestrators()
        
        options = []
        for i, (orch_type, description) in enumerate(orchestrators.items(), 1):
            color = ArnoldColors.SUCCESS if orch_type == "checklist" else ArnoldColors.INFO
            print(f"{color}{i}.{ArnoldColors.RESET} {ArnoldColors.BRIGHT}{orch_type.title()}{ArnoldColors.RESET}")
            print(f"   {ArnoldColors.DIM}{description}{ArnoldColors.RESET}")
            if orch_type == "checklist":
                print(f"   {ArnoldColors.ARNOLD_ACCENT}(Recommended for structured fitness coaching){ArnoldColors.RESET}")
            print()
            options.append(orch_type)
        
        while True:
            try:
                choice = input(f"{ArnoldColors.PROMPT}Enter your choice (1-{len(options)}): {ArnoldColors.RESET}")
                index = int(choice) - 1
                if 0 <= index < len(options):
                    selected = options[index]
                    print(f"{ArnoldColors.SUCCESS}✓ Selected: {selected.title()} Orchestrator{ArnoldColors.RESET}\\n")
                    return selected
                else:
                    print(f"{ArnoldColors.ERROR}Invalid choice. Please enter a number between 1 and {len(options)}.{ArnoldColors.RESET}")
            except ValueError:
                print(f"{ArnoldColors.ERROR}Invalid input. Please enter a number.{ArnoldColors.RESET}")
            except KeyboardInterrupt:
                print(f"\\n{ArnoldColors.WARNING}Selection cancelled. Using default (checklist).{ArnoldColors.RESET}")
                return "checklist"
    
    @staticmethod
    def get_recommendations(user_type: str = "beginner") -> Dict[str, str]:
        """
        Get orchestrator recommendations based on user type
        
        Args:
            user_type: Type of user
            
        Returns:
            Dict with recommendation and reason
        """
        recommended_type = OrchestratorFactory.get_recommended_orchestrator(user_type)
        
        reasons = {
            "beginner": "Provides structured, step-by-step guidance perfect for fitness newcomers",
            "intermediate": "Adapts to your context and experience level automatically",
            "advanced": "Offers natural conversation flow for experienced users",
            "trainer": "Professional-grade conversation interface for fitness professionals",
            "debug": "Development interface with detailed logging and debugging features"
        }
        
        return {
            "recommended": recommended_type.value,
            "reason": reasons.get(user_type.lower(), "Balanced approach suitable for most users")
        }
    
    @staticmethod
    def display_recommendation(user_type: str = "beginner"):
        """Display recommendation for user type"""
        rec = OrchestratorSelector.get_recommendations(user_type)
        
        print(f"{ArnoldColors.INFO}💡 Recommendation for {user_type} users:{ArnoldColors.RESET}")
        print(f"   {ArnoldColors.ARNOLD}{rec['recommended'].title()}{ArnoldColors.RESET} - {rec['reason']}")
        print()
    
    @staticmethod
    def quick_select_with_recommendation(user_type: str = "beginner", 
                                       interactive: bool = True) -> str:
        """
        Quick orchestrator selection with recommendation
        
        Args:
            user_type: User type for recommendation
            interactive: Whether to allow interactive selection
            
        Returns:
            Selected orchestrator type
        """
        OrchestratorSelector.display_recommendation(user_type)
        
        if not interactive:
            rec = OrchestratorSelector.get_recommendations(user_type)
            return rec["recommended"]
        
        print(f"{ArnoldColors.PROMPT}Would you like to:{ArnoldColors.RESET}")
        print(f"  1. Use recommended orchestrator")
        print(f"  2. Choose different orchestrator")
        print(f"  3. Use auto-selection")
        
        while True:
            try:
                choice = input(f"{ArnoldColors.PROMPT}Your choice (1-3): {ArnoldColors.RESET}")
                
                if choice == "1":
                    rec = OrchestratorSelector.get_recommendations(user_type)
                    selected = rec["recommended"]
                    print(f"{ArnoldColors.SUCCESS}✓ Using recommended: {selected.title()}{ArnoldColors.RESET}\\n")
                    return selected
                
                elif choice == "2":
                    return OrchestratorSelector.interactive_select()
                
                elif choice == "3":
                    print(f"{ArnoldColors.SUCCESS}✓ Using auto-selection{ArnoldColors.RESET}\\n")
                    return "auto"
                
                else:
                    print(f"{ArnoldColors.ERROR}Invalid choice. Please enter 1, 2, or 3.{ArnoldColors.RESET}")
                    
            except KeyboardInterrupt:
                print(f"\\n{ArnoldColors.WARNING}Using auto-selection.{ArnoldColors.RESET}")
                return "auto"