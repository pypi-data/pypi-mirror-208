import os
from io import BytesIO
from typing import AsyncGenerator

import pytest
from msaFilesystem import msafs as fs
from msaFileWorker.utils.file_worker import FileWorker
from pytest_asyncio import fixture
from tests import constants as C


@fixture(autouse=True)
async def worker() -> AsyncGenerator[FileWorker, None]:
    worker = FileWorker(
        subdomain=C.SUBDOMAIN,
        client_id=C.CLIENT_ID,
        path_to_filestorage=C.FILE_STORAGE_PATH,
        document_id=C.DOCUMENT_ID,
    )
    yield worker
    filesystem = fs.open_fs(C.FILE_STORAGE_PATH)
    filesystem.removetree(C.NFS_SHARE)


local_path = f"{C.NFS_SHARE}/{C.SUBDOMAIN}/{C.CLIENT_ID}/{C.DOCUMENT_ID}/"


class TestFileWorker:
    """Testing FileWoker functions"""

    @pytest.mark.asyncio
    async def test_save_bytes_file(self, worker) -> None:
        """Testing saving bytes as file"""
        with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
            file_as_bytes = bytesfile.read()
        await worker.save_bytes_file(file_as_bytes=file_as_bytes, file_name=C.FILE_NAME)
        assert os.path.isfile(f"{local_path}{C.FILE_NAME}") == True

    @pytest.mark.asyncio
    async def test_save_many_bytes_as_files(self, worker) -> None:
        """Testing saving many bytes as files"""
        list_files = []
        for x in range(4):
            with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
                file_as_bytes = bytesfile.read()
            list_files.append((f"{x}.pdf", file_as_bytes))
        await worker.save_many_bytes_as_files(list_of_data=list_files)
        for x in range(4):
            assert os.path.isfile(f"{local_path}{x}.pdf") == True

    @pytest.mark.asyncio
    async def test_save_text_as_file(self, worker) -> None:
        """Testing saving text as file"""
        await worker.save_text_as_file(text=C.TEST_TEXT, file_name=C.TEST_NAME, file_type=C.FILE_TYPE)
        assert os.path.isfile(f"{local_path}{C.TEST_NAME}.{C.FILE_TYPE}") == True

    @pytest.mark.asyncio
    async def test_save_many_texts_as_files(self, worker) -> None:
        """Testing saving many texts as files"""
        list_files = []
        for x in range(4):
            list_files.append((f"{x}", C.TEST_TEXT, C.FILE_TYPE))
        await worker.save_many_texts_as_files(list_of_data=list_files)
        for x in range(4):
            assert os.path.isfile(f"{local_path}{x}.{C.FILE_TYPE}") == True

    @pytest.mark.asyncio
    async def test_get_file_as_zip(self, worker) -> None:
        """Testing getting file as zip"""
        with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
            file_as_bytes = bytesfile.read()
        await worker.save_bytes_file(file_as_bytes=file_as_bytes, file_name=C.FILE_NAME)
        res = await worker.get_file_as_zip(path_to_file=C.FILE_NAME)
        assert type(res) == BytesIO

    @pytest.mark.asyncio
    async def test_get_folder_as_zip(self, worker) -> None:
        """Testing getting folder as zip"""
        with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
            file_as_bytes = bytesfile.read()
        await worker.save_bytes_file(file_as_bytes=file_as_bytes, file_name=C.FILE_NAME)
        res = await worker.get_folder_as_zip()
        assert type(res) == BytesIO

    @pytest.mark.asyncio
    async def test_delete_file(self, worker) -> None:
        """Testing deleting file"""
        with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
            file_as_bytes = bytesfile.read()
        await worker.save_bytes_file(file_as_bytes=file_as_bytes, file_name=C.FILE_NAME)
        assert os.path.isfile(f"{local_path}{C.FILE_NAME}") == True

        await worker.delete_file(C.FILE_NAME)
        assert os.path.isfile(f"{local_path}{C.FILE_NAME}") == False

    @pytest.mark.asyncio
    async def test_delete_folder(self, worker) -> None:
        """Testing deleting folder"""
        with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
            file_as_bytes = bytesfile.read()
        await worker.save_bytes_file(file_as_bytes=file_as_bytes, file_name=C.FILE_NAME, path_to_save=C.PATH_TO_SAVE)
        assert os.path.exists(f"{local_path}{C.PATH_TO_SAVE}") == True
        await worker.delete_folder(C.PATH_TO_SAVE)
        assert os.path.exists(f"{local_path}{C.PATH_TO_SAVE}") == False

    @pytest.mark.asyncio
    async def test_get_file_as_byte(self, worker) -> None:
        """Testing getting file as bytes"""
        with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
            file_as_bytes = bytesfile.read()
        await worker.save_bytes_file(file_as_bytes=file_as_bytes, file_name=C.FILE_NAME)
        assert os.path.isfile(f"{local_path}{C.FILE_NAME}") == True
        res = await worker.get_file_as_bytes(C.FILE_NAME)
        assert type(res) == bytes

    @pytest.mark.asyncio
    async def test_get_file_content(self, worker) -> None:
        """Testing getting file content"""
        await worker.save_text_as_file(text=C.TEST_TEXT, file_name=C.TEST_NAME, file_type=C.FILE_TYPE)
        assert os.path.isfile(f"{local_path}{C.TEST_NAME}.{C.FILE_TYPE}") == True
        res = await worker.get_file_content(f"{C.TEST_NAME}.{C.FILE_TYPE}")
        assert res == str(C.TEST_TEXT)


class TestFileWorkerFailed:
    """Testing FileWoker functions failed"""

    @pytest.mark.asyncio
    async def test_save_bytes_file(self, worker) -> None:
        """Testing saving bytes as file. The same filename"""
        with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
            file_as_bytes = bytesfile.read()
        await worker.save_bytes_file(file_as_bytes=file_as_bytes, file_name=C.FILE_NAME)

    @pytest.mark.asyncio
    async def test_save_many_bytes_as_files(self, worker) -> None:
        """Testing saving many bytes as files. The same filename"""
        list_files = []
        for x in range(2):
            with open(f"{C.PATH_TO_TEST_FILE}{C.FILE_NAME}", "rb") as bytesfile:
                file_as_bytes = bytesfile.read()
            list_files.append((f"{C.FILE_NAME}.pdf", file_as_bytes))

    @pytest.mark.asyncio
    async def test_get_file_as_zip(self, worker) -> None:
        """Testing getting file as zip. Not found"""
        with pytest.raises(fs.errors.ResourceNotFound):
            await worker.get_file_as_zip(path_to_file=C.FILE_NAME)

    @pytest.mark.asyncio
    async def test_get_folder_as_zip(self, worker) -> None:
        """Testing getting folder as zip. Not found"""
        with pytest.raises(fs.errors.ResourceNotFound):
            await worker.get_folder_as_zip("test")

    @pytest.mark.asyncio
    async def test_delete_file(self, worker) -> None:
        """Testing deleting file. Not found"""
        with pytest.raises(fs.errors.ResourceNotFound):
            await worker.delete_file(C.FILE_NAME)

    @pytest.mark.asyncio
    async def test_delete_folder(self, worker) -> None:
        """Testing deleting folder. Not found"""
        with pytest.raises(fs.errors.ResourceNotFound):
            await worker.delete_folder(C.PATH_TO_SAVE)

    @pytest.mark.asyncio
    async def test_get_file_as_byte(self, worker) -> None:
        """Testing getting file as bytes. Not found"""
        with pytest.raises(fs.errors.ResourceNotFound):
            await worker.get_file_as_bytes(C.FILE_NAME)

    @pytest.mark.asyncio
    async def test_get_file_content(self, worker) -> None:
        """Testing getting file content. Not found"""
        with pytest.raises(fs.errors.ResourceNotFound):
            await worker.get_file_content(C.TEST_FILENAME)
