from typing import Optional

from fabric import Connection


class Shell:
    @staticmethod
    def ssh_connection(host: str, username: str, port: int, password: Optional[str] = None) -> Optional[Connection]:
        return Connection(host=host, user=username, connect_kwargs={"password": password}, port=port,
                          connect_timeout=5)
