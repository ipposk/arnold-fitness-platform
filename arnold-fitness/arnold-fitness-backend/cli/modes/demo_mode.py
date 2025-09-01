"""
Arnold Fitness CLI - Demo Mode
Modern interface for demonstrations and general testing
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cli.ui.colors import ArnoldColors

def run_demo_mode(verbose=False, session_type="new"):
    """Run the modern demo interface"""
    
    print(f"{ArnoldColors.ARNOLD}🎪 Launching Demo Mode{ArnoldColors.RESET}")
    print(f"{ArnoldColors.INFO}   Session Type: {session_type}{ArnoldColors.RESET}")
    print(f"{ArnoldColors.INFO}   Verbose: {verbose}{ArnoldColors.RESET}\\n")
    print(f"{ArnoldColors.DIM}   Clean, modern interface for demonstrations and general testing{ArnoldColors.RESET}\\n")
    
    try:
        # Import and run the existing modern CLI
        from arnold_cli_modern import main as demo_main
        demo_main()
        
    except ImportError as e:
        print(f"{ArnoldColors.ERROR}❌ Cannot import modern CLI: {e}{ArnoldColors.RESET}")
        sys.exit(1)
        
    except Exception as e:
        print(f"{ArnoldColors.ERROR}❌ Error running demo mode: {e}{ArnoldColors.RESET}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)