import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import asn1tools


ROOT = Path(__file__).resolve().parent
DIGEST = bytes.fromhex(
    "edeaaff3f1774ad2888673770c6d64097e391bc362d7d6fb34982ddf0efd18cb"
)
CESR = "I7eqv8_F3StKIhnN3DG1kCX45G8Ni19b7NJgt3w79GMs"


class SaidDerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codec = asn1tools.compile_files(str(ROOT.parent / "asn1" / "said.asn"), "der")

    def assert_cbor_valid(self, der):
        cbor = subprocess.run(
            ["diag2cbor.rb"],
            input=f"h'{der.hex()}'".encode("ascii"),
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "said.cbor"
            path.write_bytes(cbor)
            for schema in (ROOT / "cbor" / "said-cbor-test.cddl", ROOT.parent / "exports" / "said.cddl"):
                subprocess.run(
                    [os.environ.get("CDDL", "cddl"), str(schema), "validate", str(path)],
                    check=True,
                    stdout=subprocess.PIPE,
                )

    def test_algorithm_digest(self):
        value = ("algDigest", {"hashAlgorithm": "2.16.840.1.101.3.4.2.1", "digest": DIGEST})
        der = self.codec.encode("SAID", value)
        self.assertEqual(
            der,
            bytes.fromhex("302d06096086480165030402010420") + DIGEST,
        )
        self.assertEqual(self.codec.decode("SAID", der), value)
        self.assert_cbor_valid(der)

    def test_cesr(self):
        value = ("cesr", CESR)
        der = self.codec.encode("SAID", value)
        self.assertEqual(der, b"\x16\x2c" + CESR.encode("ascii"))
        self.assertEqual(self.codec.decode("SAID", der), value)
        self.assert_cbor_valid(der)

    def test_truncated_der_is_rejected(self):
        der = self.codec.encode("SAID", ("cesr", CESR))
        self.assert_cbor_valid(der[:-1])
        with self.assertRaises(asn1tools.DecodeError):
            self.codec.decode("SAID", der[:-1])


if __name__ == "__main__":
    unittest.main()
