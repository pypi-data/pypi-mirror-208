import __main__
import modal.object
import typing

def _serialize_dict(data):
    ...


class _DictHandle(modal.object._Handle):
    async def get(self, key: typing.Any) -> typing.Any:
        ...

    async def contains(self, key: typing.Any) -> bool:
        ...

    async def len(self) -> int:
        ...

    async def __getitem__(self, key: typing.Any) -> typing.Any:
        ...

    async def update(self, **kwargs) -> None:
        ...

    async def put(self, key: typing.Any, value: typing.Any) -> None:
        ...

    async def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        ...

    async def pop(self, key: typing.Any) -> typing.Any:
        ...

    async def __delitem__(self, key: typing.Any) -> typing.Any:
        ...

    async def __contains__(self, key: typing.Any) -> bool:
        ...


class DictHandle(modal.object.Handle):
    def __init__(self):
        ...

    def get(self, key: typing.Any) -> typing.Any:
        ...

    def contains(self, key: typing.Any) -> bool:
        ...

    def len(self) -> int:
        ...

    def __getitem__(self, key: typing.Any) -> typing.Any:
        ...

    def update(self, **kwargs) -> None:
        ...

    def put(self, key: typing.Any, value: typing.Any) -> None:
        ...

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        ...

    def pop(self, key: typing.Any) -> typing.Any:
        ...

    def __delitem__(self, key: typing.Any) -> typing.Any:
        ...

    def __contains__(self, key: typing.Any) -> bool:
        ...


class AioDictHandle(modal.object.AioHandle):
    def __init__(self):
        ...

    async def get(self, *args, **kwargs) -> typing.Any:
        ...

    async def contains(self, *args, **kwargs) -> bool:
        ...

    async def len(self, *args, **kwargs) -> int:
        ...

    async def __getitem__(self, *args, **kwargs) -> typing.Any:
        ...

    async def update(self, *args, **kwargs) -> None:
        ...

    async def put(self, *args, **kwargs) -> None:
        ...

    async def __setitem__(self, *args, **kwargs) -> None:
        ...

    async def pop(self, *args, **kwargs) -> typing.Any:
        ...

    async def __delitem__(self, *args, **kwargs) -> typing.Any:
        ...

    async def __contains__(self, *args, **kwargs) -> bool:
        ...


class _Dict(modal.object._Provider[_DictHandle]):
    def __init__(self, data={}):
        ...


class Dict(modal.object.Provider[DictHandle]):
    def __init__(self, data={}):
        ...


class AioDict(modal.object.AioProvider[AioDictHandle]):
    def __init__(self, data={}):
        ...
