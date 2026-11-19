import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
PREIMAGE = ROOT / "common" / "preimage.data"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_urn_example(filename: str, cesr: str) -> None:
    urn = f"urn:cesr:said:{cesr}"
    write_text(ROOT / "urn" / f"{filename}.urn", urn + "\n")
    write_text(ROOT / "urn" / f"{filename}.json", json.dumps(urn) + "\n")


def write_cbor(filename: str, cbor: bytes) -> None:
    (ROOT / "cbor" / f"{filename}.cbor").write_bytes(cbor)
    pretty = subprocess.run(
        ["cbor2pretty.rb"],
        input=cbor,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    (ROOT / "cbor" / f"{filename}.pretty").write_bytes(pretty)


def encode_cbor_text(cesr: str, filename: str) -> None:
    diagnostic = json.dumps(cesr) + " / CESR text SAID /\n"
    write_text(ROOT / "cbor" / f"{filename}.diag", diagnostic)
    cbor = subprocess.run(
        ["diag2cbor.rb"],
        input=diagnostic.encode("utf-8"),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    write_cbor(filename, cbor)


def main() -> None:
    digest = subprocess.run(
        ["openssl", "dgst", "-sha256", "-binary"],
        input=PREIMAGE.read_bytes(),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    digest_b64url = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    cesr = f"I{digest_b64url}"
    digest_hex = digest.hex()

    write_text(ROOT / "cesr" / "said-cesr.cesr", cesr + "\n")
    write_text(
        ROOT / "cesr" / "said-cesr-text.json",
        json.dumps(cesr) + "\n",
    )
    write_urn_example("said-urn-sha-256", cesr)
    write_text(
        ROOT / "json" / "said-json-alg-digest.json",
        json.dumps(
            {"hash-alg-id": "sha-256", "hash-value": digest_b64url},
            indent=2,
        )
        + "\n",
    )

    diagnostic = (
        "[\n"
        "  1 / IANA SHA-256 hash algorithm identifier /,\n"
        f"  h'{digest_hex}' / raw SHA-256 digest /\n"
        "]\n"
    )
    write_text(ROOT / "cbor" / "said-cbor-alg-digest.diag", diagnostic)
    cbor = subprocess.run(
        ["diag2cbor.rb"],
        input=diagnostic.encode("utf-8"),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    write_cbor("said-cbor-alg-digest", cbor)

    encode_cbor_text(cesr, "said-cbor-cesr")

    blake2b_digest = subprocess.run(
        ["openssl", "dgst", "-blake2b512", "-binary"],
        input=PREIMAGE.read_bytes(),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    blake2b_b64url = base64.urlsafe_b64encode(blake2b_digest).decode("ascii").rstrip("=")
    blake2b_cesr = f"0E{blake2b_b64url}"
    write_text(ROOT / "cesr" / "said-blake2b-512.cesr", blake2b_cesr + "\n")
    write_text(
        ROOT / "cesr" / "said-blake2b-512-text.json",
        json.dumps(blake2b_cesr) + "\n",
    )
    write_urn_example("said-urn-blake2b-512", blake2b_cesr)
    write_text(
        ROOT / "json" / "said-json-blake2b-512-alg-digest.json",
        json.dumps(
            {"hash-alg-id": "blake2b-512", "hash-value": blake2b_b64url},
            indent=2,
        )
        + "\n",
    )
    encode_cbor_text(blake2b_cesr, "said-cbor-blake2b-512-cesr")


if __name__ == "__main__":
    main()
