import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def main() -> int:
    default_path = SCRIPT_DIR / "resume.md"

    if default_path.exists():
        md_path = default_path
    else:
        user_input = input("resume.md not found. Enter Markdown file path: ").strip()
        if not user_input:
            print("ERROR: No Markdown file path provided.")
            return 1
        md_path = Path(user_input)
        if not md_path.exists():
            print(f"ERROR: File not found: {md_path}")
            return 1

    from src.parser import parse_file
    from src.validator import validate
    from src.renderer import render

    document = parse_file(md_path)
    errors, warnings = validate(document)

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    dist_dir = SCRIPT_DIR / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    output_path = dist_dir / "resume.pdf"
    render(document, output_path)
    print("Generated: dist/resume.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
