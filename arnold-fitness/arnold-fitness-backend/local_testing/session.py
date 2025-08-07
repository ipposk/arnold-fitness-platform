"""
Session management for local testing
"""
import traceback
from .ui import print_error, print_success, print_guidance, print_token_usage, Colors
from .context_setup import get_context_summary


class TestSession:
    """Manages a testing session"""

    def __init__(self, components, initial_context):
        self.components = components
        self.context = initial_context
        self.test_id = initial_context['test_id']
        self.cycle_count = 0

    def process_input(self, user_input):
        """Process user input through the orchestrator"""
        self.cycle_count += 1

        try:
            # Process through orchestrator (same as Lambda)
            result_context = self.components['orchestrator'].process_single_input(
                self.test_id,
                user_input
            )

            # Update context
            self.context = result_context

            # Show token usage
            if hasattr(self.components['gemini_client'], 'get_token_usage'):
                token_data = self.components['gemini_client'].get_token_usage()
                print_token_usage(token_data)

            # Display guidance if available
            if "last_output" in result_context:
                guidance = result_context["last_output"].get("guidance_markdown", "")
                if guidance:
                    print_guidance(guidance)
                else:
                    print_error("No guidance generated")

            return True

        except Exception as e:
            print_error(f"Processing failed: {str(e)}")
            if self._is_debug_mode():
                traceback.print_exc()
            return False

    def get_summary(self):
        """Get current session summary"""
        return get_context_summary(self.context)

    def save_context(self, filename=None):
        """Save current context to file"""
        import json

        if not filename:
            filename = f"context_{self.test_id}.json"

        with open(filename, 'w') as f:
            json.dump(self.context, f, indent=2)

        print_success(f"Context saved to {filename}")

    def _is_debug_mode(self):
        """Check if we're in debug mode"""
        import os
        return os.getenv("PENELOPE_DEBUG", "false").lower() == "true"