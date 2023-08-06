import modal._resolver
import modal.client
import modal.object
import typing

Tree = typing.TypeVar("Tree")

class _App:
    _tag_to_object: typing.Dict[str, modal.object._Handle]
    _tag_to_existing_id: typing.Dict[str, str]
    _client: modal.client._Client
    _app_id: str
    _app_page_url: str
    _resolver: typing.Union[modal._resolver.Resolver, None]
    _function_invocations: int

    def __init__(self, client: modal.client._Client, app_id: str, app_page_url: str, tag_to_object: typing.Union[typing.Dict[str, modal.object._Handle], None] = None, tag_to_existing_id: typing.Union[typing.Dict[str, str], None] = None, stub_name: typing.Union[str, None] = None):
        ...

    @property
    def client(self) -> modal.client._Client:
        ...

    @property
    def app_id(self) -> str:
        ...

    async def _create_all_objects(self, blueprint: typing.Dict[str, modal.object._Provider], output_mgr, new_app_state: int):
        ...

    async def disconnect(self):
        ...

    async def stop(self):
        ...

    def log_url(self):
        ...

    def __getitem__(self, tag: str) -> modal.object._Handle:
        ...

    def __getattr__(self, tag: str) -> modal.object._Handle:
        ...

    def track_function_invocation(self):
        ...

    @property
    def function_invocations(self):
        ...

    async def _init_container(self, client: modal.client._Client, app_id: str, stub_name: str):
        ...

    @staticmethod
    async def init_container(client: modal.client._Client, app_id: str, stub_name: str = '') -> _App:
        ...

    @staticmethod
    async def _init_existing(client: modal.client._Client, existing_app_id: str) -> _App:
        ...

    @staticmethod
    async def _init_new(client: modal.client._Client, description: typing.Union[str, None] = None, detach: bool = False, deploying: bool = False) -> _App:
        ...

    @staticmethod
    async def _init_from_name(client: modal.client._Client, name: str, namespace):
        ...

    async def create_one_object(self, provider: modal.object._Provider) -> modal.object._Handle:
        ...

    async def deploy(self, name: str, namespace, object_entity: str) -> str:
        ...

    @staticmethod
    def _reset_container():
        ...


class App:
    _tag_to_object: typing.Dict[str, modal.object.Handle]
    _tag_to_existing_id: typing.Dict[str, str]
    _client: modal.client.Client
    _app_id: str
    _app_page_url: str
    _resolver: typing.Union[modal._resolver.Resolver, None]
    _function_invocations: int

    def __init__(self, client: modal.client.Client, app_id: str, app_page_url: str, tag_to_object: typing.Union[typing.Dict[str, modal.object.Handle], None] = None, tag_to_existing_id: typing.Union[typing.Dict[str, str], None] = None, stub_name: typing.Union[str, None] = None):
        ...

    @property
    def client(self) -> modal.client.Client:
        ...

    @property
    def app_id(self) -> str:
        ...

    def _create_all_objects(self, blueprint: typing.Dict[str, modal.object.Provider], output_mgr, new_app_state: int):
        ...

    def disconnect(self):
        ...

    def stop(self):
        ...

    def log_url(self):
        ...

    def __getitem__(self, tag: str) -> modal.object.Handle:
        ...

    def __getattr__(self, tag: str) -> modal.object.Handle:
        ...

    def track_function_invocation(self):
        ...

    @property
    def function_invocations(self):
        ...

    def _init_container(self, client: modal.client.Client, app_id: str, stub_name: str):
        ...

    @staticmethod
    def init_container(client: modal.client.Client, app_id: str, stub_name: str = '') -> App:
        ...

    @staticmethod
    def _init_existing(client: modal.client.Client, existing_app_id: str) -> App:
        ...

    @staticmethod
    def _init_new(client: modal.client.Client, description: typing.Union[str, None] = None, detach: bool = False, deploying: bool = False) -> App:
        ...

    @staticmethod
    def _init_from_name(client: modal.client.Client, name: str, namespace):
        ...

    def create_one_object(self, provider: modal.object.Provider) -> modal.object.Handle:
        ...

    def deploy(self, name: str, namespace, object_entity: str) -> str:
        ...

    @staticmethod
    def _reset_container():
        ...


class AioApp:
    _tag_to_object: typing.Dict[str, modal.object.AioHandle]
    _tag_to_existing_id: typing.Dict[str, str]
    _client: modal.client.AioClient
    _app_id: str
    _app_page_url: str
    _resolver: typing.Union[modal._resolver.Resolver, None]
    _function_invocations: int

    def __init__(self, client: modal.client.AioClient, app_id: str, app_page_url: str, tag_to_object: typing.Union[typing.Dict[str, modal.object.AioHandle], None] = None, tag_to_existing_id: typing.Union[typing.Dict[str, str], None] = None, stub_name: typing.Union[str, None] = None):
        ...

    @property
    def client(self) -> modal.client.AioClient:
        ...

    @property
    def app_id(self) -> str:
        ...

    async def _create_all_objects(self, *args, **kwargs):
        ...

    async def disconnect(self, *args, **kwargs):
        ...

    async def stop(self, *args, **kwargs):
        ...

    def log_url(self):
        ...

    def __getitem__(self, tag: str) -> modal.object.AioHandle:
        ...

    def __getattr__(self, tag: str) -> modal.object.AioHandle:
        ...

    def track_function_invocation(self):
        ...

    @property
    def function_invocations(self):
        ...

    async def _init_container(self, *args, **kwargs):
        ...

    @staticmethod
    async def init_container(*args, **kwargs) -> AioApp:
        ...

    @staticmethod
    async def _init_existing(*args, **kwargs) -> AioApp:
        ...

    @staticmethod
    async def _init_new(*args, **kwargs) -> AioApp:
        ...

    @staticmethod
    async def _init_from_name(*args, **kwargs):
        ...

    async def create_one_object(self, *args, **kwargs) -> modal.object.AioHandle:
        ...

    async def deploy(self, *args, **kwargs) -> str:
        ...

    @staticmethod
    def _reset_container():
        ...


_container_app: _App

container_app: App

aio_container_app: AioApp

def is_local() -> bool:
    ...
