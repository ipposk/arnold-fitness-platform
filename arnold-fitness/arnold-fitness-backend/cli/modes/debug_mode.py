"""
Arnold Fitness CLI - Debug Mode
Legacy debugging interface for development troubleshooting
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cli.ui.colors import ArnoldColors

def run_debug_mode(verbose=False, session_type="new"):
    """Run the legacy debugging interface"""
    
    print(f"{ArnoldColors.WARNING}🔧 Launching Debug Mode{ArnoldColors.RESET}")
    print(f"{ArnoldColors.INFO}   Session Type: {session_type}{ArnoldColors.RESET}")
    print(f"{ArnoldColors.INFO}   Verbose: {verbose}{ArnoldColors.RESET}\\n")
    print(f"{ArnoldColors.DIM}   This mode provides detailed debugging output for development{ArnoldColors.RESET}\\n")
    
    try:
        # Import and run the existing legacy CLI
        from arnold_main_local import main as debug_main
        debug_main()
        
    except ImportError as e:
        print(f"{ArnoldColors.ERROR}❌ Cannot import debug CLI: {e}{ArnoldColors.RESET}")
        sys.exit(1)
        
    except Exception as e:
        print(f"{ArnoldColors.ERROR}❌ Error running debug mode: {e}{ArnoldColors.RESET}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)