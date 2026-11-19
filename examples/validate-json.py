import base64
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft7Validator


ROOT = Path(__file__).parent


def validate_shared_digest() -> None:
    diagnostic = (
        ROOT / "cbor" / "said-cbor-alg-digest.diag"
    ).read_text(encoding="utf-8").strip()

    match = re.fullmatch(
        r"\[\s*1\s*/.*?/\s*,\s*h'([0-9a-f]{64})'\s*/.*?/\s*\]",
        diagnostic,
        re.DOTALL,
    )
    if not match:
        raise SystemExit("CBOR diagnostic example is not a SHA-256 tuple")

    sha256_cesr = (ROOT / "cesr" / "said-cesr.cesr").read_text(encoding="utf-8").strip()
    sha256_instance = json.loads(
        (ROOT / "cesr" / "said-cesr-text.json").read_text(encoding="utf-8")
    )
    sha256_json = json.loads(
        (ROOT / "json" / "said-json-alg-digest.json").read_text(encoding="utf-8")
    )
    if sha256_instance != sha256_cesr or not sha256_cesr.startswith("I"):
        raise SystemExit("SHA-256 CESR wire value and JSON instance differ")
    if sha256_json != {"hash-alg-id": "sha-256", "hash-value": sha256_cesr[1:]}:
        raise SystemExit("SHA-256 JSON digest object and CESR digest differ")

    digest = base64.urlsafe_b64decode(sha256_cesr[1:] + "=")
    if digest.hex() != match.group(1):
        raise SystemExit("SHA-256 CBOR tuple and CESR digests differ")

    blake2b_cesr = (ROOT / "cesr" / "said-blake2b-512.cesr").read_text(
        encoding="utf-8"
    ).strip()
    blake2b_instance = json.loads(
        (ROOT / "cesr" / "said-blake2b-512-text.json").read_text(encoding="utf-8")
    )
    blake2b_json = json.loads(
        (ROOT / "json" / "said-json-blake2b-512-alg-digest.json").read_text(
            encoding="utf-8"
        )
    )
    if blake2b_instance != blake2b_cesr or not blake2b_cesr.startswith("0E"):
        raise SystemExit("BLAKE2b-512 CESR wire value and JSON instance differ")
    if blake2b_json != {
        "hash-alg-id": "blake2b-512",
        "hash-value": blake2b_cesr[2:],
    }:
        raise SystemExit("BLAKE2b-512 JSON digest object and CESR digest differ")

    blake2b_diagnostic = (
        ROOT / "cbor" / "said-cbor-blake2b-512-cesr.diag"
    ).read_text(encoding="utf-8").strip()
    diagnostic_value, separator, _ = blake2b_diagnostic.partition(" /")
    if not separator or json.loads(diagnostic_value) != blake2b_cesr:
        raise SystemExit("BLAKE2b-512 CBOR CESR value and CESR digest differ")

    for name, cesr in (
        ("said-urn-sha-256", sha256_cesr),
        ("said-urn-blake2b-512", blake2b_cesr),
    ):
        urn = (ROOT / "urn" / f"{name}.urn").read_text(encoding="utf-8").strip()
        instance = json.loads(
            (ROOT / "urn" / f"{name}.json").read_text(encoding="utf-8")
        )
        if urn != f"urn:cesr:said:{cesr}" or instance != urn:
            raise SystemExit(f"{name} URN does not match its CESR value")


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: validate-json.py schema.json instance.json ...")

    schema_path = Path(sys.argv[1])
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    for instance_path in map(Path, sys.argv[2:]):
        instance = json.loads(instance_path.read_text(encoding="utf-8"))
        validator.validate(instance)

    validate_shared_digest()


if __name__ == "__main__":
    main()
