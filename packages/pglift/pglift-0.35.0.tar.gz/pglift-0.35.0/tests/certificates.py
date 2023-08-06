import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from typing_extensions import Self


@dataclass
class CA:
    name: str
    crt: Path
    key: Path

    @classmethod
    def make(cls, path: Path, name: str) -> Self:
        crt = path / f"{name}.crt"
        key = path / f"{name}.key"
        key.touch(mode=0o600)
        subprocess.run(
            [
                "openssl",
                "req",
                "-new",
                "-x509",
                "-nodes",
                "-out",
                crt,
                "-keyout",
                key,
                "-subj",
                f"/CN={name}",
            ],
            capture_output=True,
            check=True,
        )
        return cls(name, crt, key)


@dataclass
class Certificate:
    name: str
    key: bytes
    crt: bytes

    @classmethod
    def make(cls, ca_cert: Path, ca_key: Path, cn: str, **extensions: str) -> Self:
        with tempfile.NamedTemporaryFile(
            prefix="openssl", suffix=".cnf", mode="w"
        ) as openssl_cnf, tempfile.NamedTemporaryFile(
            suffix=".key"
        ) as key, tempfile.NamedTemporaryFile(
            suffix=".crt"
        ) as crt:
            opts: dict[str, list[str]] = {"req": [], "x509": []}
            if extensions:
                openssl_cnf.write(
                    "\n".join(
                        [
                            "[req]",
                            "req_extensions = myexts",
                            "",
                            "[ myexts ]",
                        ]
                    )
                    + "\n"
                )
                for extname, extvalue in extensions.items():
                    extkv = f"{extname} = {extvalue}"
                    opts["req"] += ["-addext", extkv]
                    openssl_cnf.write(f"{extkv}\n")
                openssl_cnf.flush()
                opts["x509"] += ["-extfile", openssl_cnf.name, "-extensions", "myexts"]
            with subprocess.Popen(
                [
                    "openssl",
                    "req",
                    "-new",
                    "-nodes",
                    "-keyout",
                    key.name,
                    "-subj",
                    f"/CN={cn}",
                ]
                + opts["req"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ) as req:
                subprocess.run(
                    [
                        "openssl",
                        "x509",
                        "-req",
                        "-CA",
                        str(ca_cert),
                        "-CAkey",
                        str(ca_key),
                        "-CAcreateserial",
                        "-out",
                        crt.name,
                    ]
                    + opts["x509"],
                    stdin=req.stdout,
                    check=True,
                    capture_output=True,
                )
            if req.returncode:
                raise subprocess.CalledProcessError(req.returncode, req.args)

            return cls(cn, key.read(), crt.read())

    def install(self, where: Path) -> tuple[Path, Path]:
        keyfile = where / f"{self.name}.key"
        keyfile.touch(mode=0o600)
        keyfile.write_bytes(self.key)
        certfile = where / f"{self.name}.crt"
        certfile.write_bytes(self.crt)
        return keyfile, certfile
