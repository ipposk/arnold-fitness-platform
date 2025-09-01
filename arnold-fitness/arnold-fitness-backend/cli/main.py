#!/usr/bin/env python3
"""
Arnold Fitness Platform - Unified CLI Entry Point
Single interface for all development and testing modes
"""

import sys
import argparse
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.ui.colors import ArnoldColors


def main():
    """Main CLI entry point with mode selection"""
    
    # Clear screen and show logo
    print("\033[2J\033[H")
    ArnoldColors.print_logo()
    
    parser = argparse.ArgumentParser(
        description="Arnold Fitness Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{ArnoldColors.INFO}Available Modes:{ArnoldColors.RESET}
  
  {ArnoldColors.SUCCESS}checklist{ArnoldColors.RESET}  - Enhanced checklist-driven interface (recommended)
  {ArnoldColors.INFO}debug{ArnoldColors.RESET}      - Legacy debugging interface  
  {ArnoldColors.WARNING}demo{ArnoldColors.RESET}       - Modern demo interface

{ArnoldColors.ARNOLD}Examples:{ArnoldColors.RESET}
  python cli/main.py checklist
  python cli/main.py debug --verbose
  python cli/main.py demo --session new
        """
    )
    
    parser.add_argument(
        "mode", 
        choices=["checklist", "debug", "demo"],
        help="CLI mode to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--session", 
        choices=["new", "resume"],
        default="new",
        help="Session mode (default: new)"
    )
    
    args = parser.parse_args()
    
    print(f"{ArnoldColors.INFO}🚀 Starting Arnold CLI in {ArnoldColors.BRIGHT}{args.mode}{ArnoldColors.RESET}{ArnoldColors.INFO} mode...{ArnoldColors.RESET}\\n")
    
    try:
        if args.mode == "checklist":
            from cli.modes.checklist_mode import run_checklist_mode
            run_checklist_mode(verbose=args.verbose, session_type=args.session)
            
        elif args.mode == "debug":
            from cli.modes.debug_mode import run_debug_mode
            run_debug_mode(verbose=args.verbose, session_type=args.session)
            
        elif args.mode == "demo":
            from cli.modes.demo_mode import run_demo_mode
            run_demo_mode(verbose=args.verbose, session_type=args.session)
            
    except KeyboardInterrupt:
        print(f"\\n{ArnoldColors.WARNING}👋 Session terminated by user{ArnoldColors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{ArnoldColors.ERROR}❌ Error: {e}{ArnoldColors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()