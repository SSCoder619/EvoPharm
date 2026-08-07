from pathlib import Path

ROOT = Path(__file__).parent

directories = [
    "tools",
]

files = [
    "tools/__init__.py",

    "tools/analyze_project.py",
    "tools/analyze_domain.py",
    "tools/analyze_architecture.py",
    "tools/analyze_typing.py",
    "tools/analyze_dependencies.py",
    "tools/analyze_tests.py",

    "tools/architecture_report.py",

    "tools/common.py",
    "tools/config.py",
    "tools/metrics.py",
    "tools/tree.py",
    "tools/parser.py",

    "tools/requirements.txt",
]

# Create directories
for directory in directories:
    path = ROOT / directory
    path.mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    path = ROOT / file
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()

print("=" * 60)
print("✅ EvoPharm Tools Structure Created Successfully")
print("=" * 60)
print(f"Directories Created : {len(directories)}")
print(f"Files Created       : {len(files)}")
print("=" * 60)

print("\nCreated Structure:\n")

for item in sorted((ROOT / "tools").rglob("*")):
    relative = item.relative_to(ROOT)
    prefix = "📄" if item.is_file() else "📁"
    print(f"{prefix} {relative}")