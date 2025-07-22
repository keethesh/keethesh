import re
import sys
from pathlib import Path
import os

# Configurable parameters
TIL_DIR = Path(os.environ.get('TIL_DIR', 'til'))
README_FILE = Path(os.environ.get('README_FILE', 'README.md'))
TIL_LIMIT = int(os.environ.get('TIL_LIMIT', 5))
START_MARKER = os.environ.get('TIL_START_MARKER', '<!-- TIL_START -->')
END_MARKER = os.environ.get('TIL_END_MARKER', '<!-- TIL_END -->')

def main():
    if not TIL_DIR.exists() or not TIL_DIR.is_dir():
        print(f"Directory {TIL_DIR} does not exist.")
        sys.exit(1)

    try:
        tils = sorted([f for f in TIL_DIR.glob('*.md')], reverse=True)
    except Exception as e:
        print(f"Error reading TIL directory: {e}")
        sys.exit(1)

    if not tils:
        print("No TILs found.")
        sys.exit(0)

    recent_tils_md = []
    for til_file in tils[:TIL_LIMIT]:
        clean_title = til_file.stem.replace('-', ' ')
        display_title = re.sub(r'^\d+\s*', '', clean_title).capitalize()
        recent_tils_md.append(f"* [{display_title}]({TIL_DIR}/{til_file.name})")

    new_content = "\n".join(recent_tils_md)

    try:
        readme_content = README_FILE.read_text()
    except Exception as e:
        print(f"Error reading {README_FILE}: {e}")
        sys.exit(1)

    if START_MARKER not in readme_content or END_MARKER not in readme_content:
        print(f"{README_FILE} does not contain TIL markers.")
        sys.exit(1)

    updated_readme = re.sub(
        rf'(?<={re.escape(START_MARKER)}\n).*(?=\n{re.escape(END_MARKER)})',
        new_content,
        readme_content,
        flags=re.DOTALL
    )

    try:
        README_FILE.write_text(updated_readme)
        print(f"{README_FILE} updated successfully.")
    except Exception as e:
        print(f"Error writing {README_FILE}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()