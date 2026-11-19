import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: stream.py output.json fragment.json ...")

    output = Path(sys.argv[1])
    fragments = [Path(path) for path in sys.argv[2:]]
    schema = json.loads(fragments[0].read_text(encoding="utf-8"))
    definitions = schema.get("definitions")
    if not isinstance(definitions, dict):
        raise SystemExit(f"{fragments[0]} must define a definitions object")

    for path in fragments[1:]:
        fragment = json.loads(path.read_text(encoding="utf-8"))
        fragment_definitions = fragment.get("definitions")
        if not isinstance(fragment_definitions, dict):
            raise SystemExit(f"{path} must define a definitions object")

        duplicates = definitions.keys() & fragment_definitions.keys()
        if duplicates:
            names = ", ".join(sorted(duplicates))
            raise SystemExit(f"{path} repeats definitions: {names}")
        definitions.update(fragment_definitions)

    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)


if __name__ == "__main__":
    main()
