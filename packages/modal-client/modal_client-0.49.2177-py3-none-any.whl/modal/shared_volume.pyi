import __main__
import modal.object
import modal_proto.api_pb2
import pathlib
import typing

class _SharedVolumeHandle(modal.object._Handle):
    async def write_file(self, remote_path: str, fp: typing.BinaryIO) -> int:
        ...

    def read_file(self, path: str) -> typing.AsyncIterator[bytes]:
        ...

    def iterdir(self, path: str) -> typing.AsyncIterator[modal_proto.api_pb2.SharedVolumeListFilesEntry]:
        ...

    async def add_local_file(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[str, pathlib.PurePosixPath, None] = None):
        ...

    async def add_local_dir(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[str, pathlib.PurePosixPath, None] = None):
        ...

    async def listdir(self, path: str) -> typing.List[modal_proto.api_pb2.SharedVolumeListFilesEntry]:
        ...

    async def remove_file(self, path: str, recursive=False):
        ...


class SharedVolumeHandle(modal.object.Handle):
    def __init__(self):
        ...

    def write_file(self, remote_path: str, fp: typing.BinaryIO) -> int:
        ...

    def read_file(self, path: str) -> typing.Iterator[bytes]:
        ...

    def iterdir(self, path: str) -> typing.Iterator[modal_proto.api_pb2.SharedVolumeListFilesEntry]:
        ...

    def add_local_file(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[str, pathlib.PurePosixPath, None] = None):
        ...

    def add_local_dir(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[str, pathlib.PurePosixPath, None] = None):
        ...

    def listdir(self, path: str) -> typing.List[modal_proto.api_pb2.SharedVolumeListFilesEntry]:
        ...

    def remove_file(self, path: str, recursive=False):
        ...


class AioSharedVolumeHandle(modal.object.AioHandle):
    def __init__(self):
        ...

    async def write_file(self, *args, **kwargs) -> int:
        ...

    def read_file(self, path: str) -> typing.AsyncIterator[bytes]:
        ...

    def iterdir(self, path: str) -> typing.AsyncIterator[modal_proto.api_pb2.SharedVolumeListFilesEntry]:
        ...

    async def add_local_file(self, *args, **kwargs):
        ...

    async def add_local_dir(self, *args, **kwargs):
        ...

    async def listdir(self, *args, **kwargs) -> typing.List[modal_proto.api_pb2.SharedVolumeListFilesEntry]:
        ...

    async def remove_file(self, *args, **kwargs):
        ...


class _SharedVolume(modal.object._Provider[_SharedVolumeHandle]):
    def __init__(self, cloud: typing.Union[str, None] = None) -> None:
        ...


class SharedVolume(modal.object.Provider[SharedVolumeHandle]):
    def __init__(self, cloud: typing.Union[str, None] = None) -> None:
        ...


class AioSharedVolume(modal.object.AioProvider[AioSharedVolumeHandle]):
    def __init__(self, cloud: typing.Union[str, None] = None) -> None:
        ...
