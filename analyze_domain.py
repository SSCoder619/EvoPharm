from pathlib import Path
import ast

# Change this if needed
DOMAIN_DIR = Path(
    r"E:\evopharm\EvoPharm\src\evopharm_retail_erp\domain"
)

EXPECTED_FILES = {
    "entities.py",
    "value_objects.py",
    "enums.py",
    "exceptions.py",
    "interfaces.py",
}


def analyze_python_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    classes = []
    dataclasses = []
    enums = []
    protocols = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(b.attr)

            if "Protocol" in bases:
                protocols.append(node.name)

            if "Enum" in bases:
                enums.append(node.name)

            for deco in node.decorator_list:
                if isinstance(deco, ast.Name):
                    if deco.id == "dataclass":
                        dataclasses.append(node.name)
                elif isinstance(deco, ast.Call):
                    if isinstance(deco.func, ast.Name):
                        if deco.func.id == "dataclass":
                            dataclasses.append(node.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

    return {
        "classes": classes,
        "dataclasses": dataclasses,
        "enums": enums,
        "protocols": protocols,
        "imports": imports,
    }


print("=" * 80)
print("DOMAIN ARCHITECTURE REPORT")
print("=" * 80)

if not DOMAIN_DIR.exists():
    print("Domain folder not found.")
    exit()

contexts = sorted(
    [d for d in DOMAIN_DIR.iterdir() if d.is_dir()]
)

total_files = 0
total_classes = 0

for context in contexts:

    print(f"\n{'='*80}")
    print(f"BOUNDED CONTEXT : {context.name}")
    print("=" * 80)

    files = sorted(context.glob("*.py"))
    existing = {f.name for f in files}

    missing = EXPECTED_FILES - existing

    print("\nFiles:")

    for f in files:
        print(f"   {f.name}")

    if missing:
        print("\nMissing expected files:")
        for m in sorted(missing):
            print(f"   {m}")

    print("\nDetails:\n")

    for py in files:

        total_files += 1

        info = analyze_python_file(py)

        total_classes += len(info["classes"])

        print("-" * 60)
        print(py.name)

        print(f"Classes      : {len(info['classes'])}")
        print(f"Dataclasses  : {len(info['dataclasses'])}")
        print(f"Enums        : {len(info['enums'])}")
        print(f"Protocols    : {len(info['protocols'])}")

        if info["classes"]:
            print("Class Names:")
            for c in info["classes"]:
                print(f"   {c}")

        if info["imports"]:
            print("Imports:")
            for imp in sorted(set(info["imports"])):
                print(f"   {imp}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"Bounded Contexts : {len(contexts)}")
print(f"Python Files     : {total_files}")
print(f"Classes          : {total_classes}")

print("\nDone.")