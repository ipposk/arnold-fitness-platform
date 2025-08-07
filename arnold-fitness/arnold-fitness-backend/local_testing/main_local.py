#!/usr/bin/env python3
"""
Penelope Local Testing Interface
================================
This script provides a clean interface for testing Penelope locally
using the exact same components that are deployed to AWS Lambda.

Usage:
    python main_local.py

Environment variables:
    PENELOPE_DEBUG=true  # Show full tracebacks
    GEMINI_API_KEY=...   # Required
    QDRANT_URL=...       # Required
    QDRANT_API_KEY=...   # Required
"""

import sys
from local_testing.config import check_environment
from local_testing.components import initialize_components
from local_testing.context_setup import create_initial_context
from local_testing.session import TestSession
from local_testing.ui import (
    print_header, print_context_summary, print_error,
    print_success, print_info, Colors
)


def show_help():
    """Show available commands"""
    print(f"\n{Colors.CYAN}Available Commands:{Colors.END}")
    print("  help     - Show this help")
    print("  status   - Show current context status")
    print("  save     - Save current context to file")
    print("  skip     - Skip current check")
    print("  exit     - Exit the session")
    print("\nOr type any observation/command for the penetration test")


def main():
    """Main entry point for local testing"""

    # Header
    print_header("PENELOPE LOCAL TESTING", Colors.CYAN)

    try:
        # Check environment
        check_environment()
        print_success("Environment check passed")

        # Initialize components
        components = initialize_components()

        # Create initial context
        initial_context = create_initial_context()
        test_id = initial_context['test_id']
        print_info(f"Test session ID: {test_id}")

        # Save initial context
        components['db_manager'].update_context_and_version(test_id, initial_context)

        # Create session
        session = TestSession(components, initial_context)

        # Show initial status
        print()
        print_context_summary(session.get_summary())

        # Show help
        show_help()

        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = input(
                    f"\n{Colors.BOLD}[{session.context.get('current_phase_id', 'PENELOPE')}] > {Colors.END}").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() == 'exit':
                    print("\nExiting session...")
                    break

                elif user_input.lower() == 'help':
                    show_help()
                    continue

                elif user_input.lower() == 'status':
                    print()
                    print_context_summary(session.get_summary())
                    continue

                elif user_input.lower() == 'save':
                    session.save_context()
                    continue

                # Process input through orchestrator
                print(f"\n{Colors.GRAY}Processing...{Colors.END}")
                session.process_input(user_input)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break

            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")

        # Final save
        session.save_context()
        print_success(f"Session completed. Context saved to context_{test_id}.json")

    except EnvironmentError as e:
        print_error(str(e))
        sys.exit(1)

    except Exception as e:
        print_error(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()