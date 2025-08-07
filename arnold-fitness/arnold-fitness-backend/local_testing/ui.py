"""
Simple UI helpers for local testing
"""

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'


def print_header(text, color=Colors.CYAN):
    """Print a formatted header"""
    print(f"\n{color}{'='*60}{Colors.END}")
    print(f"{color}{text.center(60)}{Colors.END}")
    print(f"{color}{'='*60}{Colors.END}\n")


def print_context_summary(summary):
    """Print context summary in a nice format"""
    print(f"{Colors.CYAN}Context Summary:{Colors.END}")
    print(f"  Test ID: {summary['test_id']}")
    print(f"  Type: {summary['pt_type']}")
    print(f"  Goal: {summary['goal']}")
    print(f"  Current Phase: {summary['current_phase']}")
    print(f"  Progress: {summary['done_checks']}/{summary['total_checks']} ({summary['progress_percentage']:.1f}%)")
    print(f"  Findings: {summary['findings_count']}")
    print(f"  Evidence: {summary['evidence_count']}")

    if summary['in_progress_checks']:
        print(f"\n{Colors.YELLOW}Active Checks:{Colors.END}")
        for check in summary['in_progress_checks']:
            print(f"  - [{check['check_id']}] {check['description']}")


def print_guidance(guidance_markdown):
    """Print guidance in a readable format"""
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}ASSISTANT GUIDANCE:{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    print(guidance_markdown)
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")


def print_error(error_message):
    """Print error message"""
    print(f"{Colors.RED}ERROR: {error_message}{Colors.END}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_token_usage(token_data):
    """Print token usage information"""
    if not token_data:
        return

    print(f"\n{Colors.GRAY}Token Usage:{Colors.END}")
    print(f"  Prompt tokens: {token_data.get('prompt_tokens', 0):,}")
    print(f"  Completion tokens: {token_data.get('completion_tokens', 0):,}")
    print(f"  Total tokens: {token_data.get('total_tokens', 0):,}")
    print(f"  Estimated cost: ${token_data.get('estimated_cost', 0):.6f}")

    # Session stats if available
    if 'session_total_tokens' in token_data:
        print(f"  Session total: {token_data.get('session_total_tokens', 0):,} tokens")
        print(f"  Session cost: ${token_data.get('session_total_cost_usd', 0):.4f}")