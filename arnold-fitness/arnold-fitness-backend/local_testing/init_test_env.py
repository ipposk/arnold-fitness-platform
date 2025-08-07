"""
Script per inizializzare l'ambiente di test locale
"""
from pathlib import Path


def init_test_environment():
    """Crea le directory necessarie per i test locali"""
    base_dir = Path(__file__).parent

    directories = [
        base_dir / "test_sessions",
        base_dir / "test_logs",
        base_dir / "token_reports"
    ]

    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"✓ Created/verified directory: {directory}")

    # Crea un .gitignore per escludere i file di test
    gitignore_content = """
# Test data
test_sessions/
test_logs/
token_reports/
*.log
"""

    gitignore_path = base_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content.strip())
        print(f"✓ Created .gitignore file")

    print("\n✅ Test environment initialized successfully!")


if __name__ == "__main__":
    init_test_environment()