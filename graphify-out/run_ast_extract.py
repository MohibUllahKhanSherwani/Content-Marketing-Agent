import json
import multiprocessing
from pathlib import Path

from graphify.extract import collect_files, extract


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    detect_path = root / "graphify-out" / ".graphify_detect.json"
    detect = json.loads(detect_path.read_text(encoding="utf-8"))

    code_files: list[Path] = []
    for file_name in detect.get("files", {}).get("code", []):
        file_path = root / file_name
        if file_path.is_dir():
            code_files.extend(collect_files(file_path))
        else:
            code_files.append(file_path)

    if code_files:
        result = extract(code_files)
    else:
        result = {"nodes": [], "edges": [], "input_tokens": 0, "output_tokens": 0}

    (root / "graphify-out" / ".graphify_ast.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    (root / ".graphify_ast.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"AST: {len(result['nodes'])} nodes, {len(result['edges'])} edges")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
