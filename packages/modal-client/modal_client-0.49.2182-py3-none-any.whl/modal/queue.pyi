import __main__
import modal.object
import typing

class _QueueHandle(modal.object._Handle):
    async def _get_nonblocking(self, n_values: int) -> typing.List[typing.Any]:
        ...

    async def _get_blocking(self, timeout: typing.Union[float, None], n_values: int) -> typing.List[typing.Any]:
        ...

    async def get(self, block: bool = True, timeout: typing.Union[float, None] = None) -> typing.Union[typing.Any, None]:
        ...

    async def get_many(self, n_values: int, block: bool = True, timeout: typing.Union[float, None] = None) -> typing.List[typing.Any]:
        ...

    async def put(self, v: typing.Any) -> None:
        ...

    async def put_many(self, vs: typing.List[typing.Any]) -> None:
        ...


class QueueHandle(modal.object.Handle):
    def __init__(self):
        ...

    def _get_nonblocking(self, n_values: int) -> typing.List[typing.Any]:
        ...

    def _get_blocking(self, timeout: typing.Union[float, None], n_values: int) -> typing.List[typing.Any]:
        ...

    def get(self, block: bool = True, timeout: typing.Union[float, None] = None) -> typing.Union[typing.Any, None]:
        ...

    def get_many(self, n_values: int, block: bool = True, timeout: typing.Union[float, None] = None) -> typing.List[typing.Any]:
        ...

    def put(self, v: typing.Any) -> None:
        ...

    def put_many(self, vs: typing.List[typing.Any]) -> None:
        ...


class AioQueueHandle(modal.object.AioHandle):
    def __init__(self):
        ...

    async def _get_nonblocking(self, *args, **kwargs) -> typing.List[typing.Any]:
        ...

    async def _get_blocking(self, *args, **kwargs) -> typing.List[typing.Any]:
        ...

    async def get(self, *args, **kwargs) -> typing.Union[typing.Any, None]:
        ...

    async def get_many(self, *args, **kwargs) -> typing.List[typing.Any]:
        ...

    async def put(self, *args, **kwargs) -> None:
        ...

    async def put_many(self, *args, **kwargs) -> None:
        ...


class _Queue(modal.object._Provider[_QueueHandle]):
    def __init__(self):
        ...


class Queue(modal.object.Provider[QueueHandle]):
    def __init__(self):
        ...


class AioQueue(modal.object.AioProvider[AioQueueHandle]):
    def __init__(self):
        ...
