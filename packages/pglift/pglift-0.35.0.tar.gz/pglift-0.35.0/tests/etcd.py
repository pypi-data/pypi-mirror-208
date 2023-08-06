import socket
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed


@dataclass
class Etcd:
    execpath: str
    datadir: Path
    client_port: int
    peer_port: int
    host: str = "127.0.0.1"

    def __str__(self) -> str:
        return f"{self.host}:{self.client_port}"

    @retry(
        retry=retry_if_exception_type(ConnectionRefusedError),
        wait=wait_fixed(1),
        stop=stop_after_attempt(5),
    )
    def try_connect(self) -> None:
        with socket.socket() as s:
            s.connect(("localhost", self.client_port))

    @contextmanager
    def running(self) -> Iterator[None]:
        client_url = f"http://{self.host}:{self.client_port}"
        cmd = [
            self.execpath,
            "--data-dir",
            str(self.datadir),
            "--listen-peer-urls",
            f"http://{self.host}:{self.peer_port}",
            "--listen-client-urls",
            client_url,
            "--advertise-client-urls",
            client_url,
        ]
        with subprocess.Popen(cmd) as proc:
            self.try_connect()
            yield None
            proc.terminate()
