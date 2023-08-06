import grpclib.exceptions
import typing

def _get_metadata(client_type: int, credentials: typing.Union[typing.Tuple[str, str], None], version: str) -> typing.Dict[str, str]:
    ...


async def _http_check(url: str, timeout: float) -> str:
    ...


async def _grpc_exc_string(exc: grpclib.exceptions.GRPCError, method_name: str, server_url: str, timeout: float) -> str:
    ...


class _Client:
    def __init__(self, server_url, client_type, credentials, version='0.49.2182', *, no_verify=False):
        ...

    @property
    def stub(self):
        ...

    async def _open(self):
        ...

    async def _close(self):
        ...

    def set_pre_stop(self, pre_stop: typing.Callable[[], None]):
        ...

    async def _verify(self):
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc, tb):
        ...

    @classmethod
    async def verify(cls, server_url, credentials):
        ...

    @classmethod
    async def unauthenticated_client(cls, env: str, server_url: str):
        ...

    async def start_token_flow(self) -> typing.Tuple[str, str]:
        ...

    async def finish_token_flow(self, token_flow_id) -> typing.Tuple[str, str]:
        ...

    @classmethod
    async def from_env(cls, _override_config=None) -> _Client:
        ...

    @classmethod
    def set_env_client(cls, client):
        ...


class Client:
    def __init__(self, server_url, client_type, credentials, version='0.49.2182', *, no_verify=False):
        ...

    @property
    def stub(self):
        ...

    def _open(self):
        ...

    def _close(self):
        ...

    def set_pre_stop(self, pre_stop: typing.Callable[[], None]):
        ...

    def _verify(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc, tb):
        ...

    @classmethod
    def verify(cls, server_url, credentials):
        ...

    @classmethod
    def unauthenticated_client(cls, env: str, server_url: str):
        ...

    def start_token_flow(self) -> typing.Tuple[str, str]:
        ...

    def finish_token_flow(self, token_flow_id) -> typing.Tuple[str, str]:
        ...

    @classmethod
    def from_env(cls, _override_config=None) -> Client:
        ...

    @classmethod
    def set_env_client(cls, client):
        ...


class AioClient:
    def __init__(self, server_url, client_type, credentials, version='0.49.2182', *, no_verify=False):
        ...

    @property
    def stub(self):
        ...

    async def _open(self, *args, **kwargs):
        ...

    async def _close(self, *args, **kwargs):
        ...

    def set_pre_stop(self, pre_stop: typing.Callable[[], None]):
        ...

    async def _verify(self, *args, **kwargs):
        ...

    async def __aenter__(self, *args, **kwargs):
        ...

    async def __aexit__(self, *args, **kwargs):
        ...

    @classmethod
    async def verify(cls, *args, **kwargs):
        ...

    @classmethod
    async def unauthenticated_client(cls, *args, **kwargs):
        ...

    async def start_token_flow(self, *args, **kwargs) -> typing.Tuple[str, str]:
        ...

    async def finish_token_flow(self, *args, **kwargs) -> typing.Tuple[str, str]:
        ...

    @classmethod
    async def from_env(cls, *args, **kwargs) -> AioClient:
        ...

    @classmethod
    def set_env_client(cls, client):
        ...


HEARTBEAT_INTERVAL: float

HEARTBEAT_TIMEOUT: float

CLIENT_CREATE_ATTEMPT_TIMEOUT: float

CLIENT_CREATE_TOTAL_TIMEOUT: float