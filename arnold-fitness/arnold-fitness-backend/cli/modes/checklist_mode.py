"""
Arnold Fitness CLI - Enhanced Checklist Mode
Professional checklist-driven fitness coaching interface
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cli.ui.colors import ArnoldColors

def run_checklist_mode(verbose=False, session_type="new"):
    """Run the enhanced checklist-driven interface"""
    
    print(f"{ArnoldColors.SUCCESS}🎯 Launching Enhanced Checklist Mode{ArnoldColors.RESET}")
    print(f"{ArnoldColors.INFO}   Session Type: {session_type}{ArnoldColors.RESET}")
    print(f"{ArnoldColors.INFO}   Verbose: {verbose}{ArnoldColors.RESET}\\n")
    
    # Import and run the existing enhanced CLI
    try:
        # Import the existing enhanced CLI logic
        from arnold_cli_checklist_driven_enhanced import main as enhanced_main
        enhanced_main()
        
    except ImportError as e:
        print(f"{ArnoldColors.ERROR}❌ Cannot import enhanced CLI: {e}{ArnoldColors.RESET}")
        print(f"{ArnoldColors.INFO}💡 Using fallback basic checklist mode...{ArnoldColors.RESET}")
        
        try:
            from arnold_cli_checklist_driven import main as basic_main
            basic_main()
        except ImportError:
            print(f"{ArnoldColors.ERROR}❌ No checklist CLI available{ArnoldColors.RESET}")
            sys.exit(1)
            
    except Exception as e:
        print(f"{ArnoldColors.ERROR}❌ Error running checklist mode: {e}{ArnoldColors.RESET}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)