from io import BytesIO
from typing import Dict, List, Tuple, Union
from zipfile import ZIP_DEFLATED, ZipFile

from msaFilesystem import msafs as fs
from msaFileWorker.utils.constans import CLIENT_ID, NFS_SHARE


class FileWorker:
    """
    Working with files

    Parameters:

        subdomain: tenant
        client_id: client id(user identifier).
        document_id: document identifier.
        path_to_filestorage: path to shared filestorage. Work directory default

    """

    def __init__(
        self, subdomain: str, document_id: str, client_id: str = CLIENT_ID, path_to_filestorage: str = "."
    ) -> None:
        self.client_folder_path = path_to_filestorage + f"/{NFS_SHARE}/{subdomain}/{client_id}/{document_id}"
        try:
            self.filesystem = fs.open_fs(self.client_folder_path)
        except fs.errors.CreateFailed:
            self.filesystem = fs.open_fs(".")
            self.filesystem.makedirs(self.client_folder_path)
            self.filesystem = fs.open_fs(self.client_folder_path)

    async def save_bytes_file(
        self,
        file_as_bytes: bytes,
        file_name: str,
        path_to_save: str = "",
    ) -> None:
        """
        Save bytes file.

        Parameters:

            file_as_bytes: file in bytes format
            file_name: name of file
            path_to_save: if you need another folder. Default: root
        """
        if path_to_save:
            await self._create_folders_if_not_exist(path_to_save)
        self.filesystem.writebytes(f"{path_to_save}/{file_name}", contents=file_as_bytes)

    async def save_many_bytes_as_files(
        self,
        list_of_data: List[Tuple[str, bytes]],
        path_to_save: str = "",
    ) -> None:
        """
        Save bytes multi files.

        Parameters:

            list_of_data: list of tuples with names and files in bytes
            path_to_save: if you need another folder. Default: root
        """
        for name, file_as_bytes in list_of_data:
            await self.save_bytes_file(file_as_bytes=file_as_bytes, file_name=name, path_to_save=path_to_save)

    async def save_text_as_file(
        self,
        text: Union[str, Dict],
        file_name: str,
        path_to_save: str = "",
        file_type: str = "txt",
    ) -> None:
        """
        Save text as file.

        Parameters:

            text: text which you need to save
            file_name: name of file
            path_to_save: if you need another folder. Default: root
            file_type: type of file. Default: txt
        """
        file_name_with_type = f"{file_name}.{file_type}"
        if path_to_save:
            await self._create_folders_if_not_exist(path_to_save)

        self.filesystem.writebytes(f"{path_to_save}/{file_name_with_type}", contents=bytes(str(text), "utf-8"))

    async def save_many_texts_as_files(
        self,
        list_of_data: List[Tuple[str, str, str]],
        path_to_save: str = "",
    ) -> None:
        """
        Save text as file.

        Parameters:

            list_of_data: list of tuples with names and texts
            path_to_save: if you need another folder. Default: root
        """
        for name, text, file_type in list_of_data:
            await self.save_text_as_file(text=text, file_name=name, path_to_save=path_to_save, file_type=file_type)

    async def get_file_as_zip(
        self,
        path_to_file: str,
    ) -> BytesIO:
        """
        Get 1 file as zip in bytes format.

        Parameters:

            path_to_file: If file inside a folder, specify it as: folder1/folder2/123.txt
                          Default: root

        Return:

            BytesIO

        """
        name, path = await self._split_path(path_to_file)
        file_as_bytes = self.filesystem.readbytes(f"{path}/" + name)
        return await self._get_zip_one_file(file_as_bytes, name)

    async def get_folder_as_zip(
        self,
        path_to_folder: str = ".",
    ) -> BytesIO:
        """
        Get folder as zip in bytes format.

        Parameters:

            path_to_folder: If folder inside another folder, specify it as: folder1/folder2

        Return:

            BytesIO

        """
        name, path = await self._split_path(path_to_folder)
        zip_buffer = BytesIO()
        return await self._zip_with_subfolders(zip_buffer=zip_buffer, folder=name, path=path)

    async def delete_file(
        self,
        path_to_file: str,
    ) -> None:
        """
        Delete file.

        Parameters:

            path_to_file: If file inside a folder, specify it as: folder1/folder2/123.txt
                          Default: root

        """
        name, path = await self._split_path(path_to_file)
        self.filesystem.remove(f"{path}/{name}")

    async def delete_folder(
        self,
        path_to_folder: str,
    ) -> None:
        """
        Delete folder.

        Parameters:

            path_to_folder: If folder inside another folder, specify it as: folder1/folder2
                            Default: root

        """
        name, path = await self._split_path(path_to_folder)
        self.filesystem.removetree(f"{path}/{name}")

    async def get_file_as_bytes(
        self,
        path_to_file: str,
    ) -> bytes:
        """
        Get file.

        Parameters:

            path_to_file: If file inside a folder, specify it as: folder1/folder2/12.txt
                          Default: root

        Return:

            file in bytes format
        """
        name, path = await self._split_path(path_to_file)
        return self.filesystem.readbytes(f"{path}/{name}")

    async def get_file_content(
        self,
        path_to_file: str,
    ) -> str:
        """
        Get file content.

        Parameters:

            path_to_file: If file inside a folder, specify it as: folder1/folder2/12.txt
                          Default: root

        Return:

            file content

        """
        name, path = await self._split_path(path_to_file)
        return (self.filesystem.open(f"{path}/{name}")).read()

    async def _get_zip_one_file(self, file: bytes, file_name: str) -> BytesIO:
        """
        Create zip

        Parameters:

            file: file in bytes
            file_name: name of file

        Return:

            BytesIO
        """
        zip_buffer = BytesIO()

        with ZipFile(zip_buffer, "a", ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr(f"{file_name}", file)
        return zip_buffer

    async def _create_folders_if_not_exist(self, path: str) -> None:
        """
        Creating folders if not exists

        Parameters:

            path: which path to create. Ex: folder/folder1/folder2
        """
        if not self.filesystem.exists(path):
            self.filesystem.makedirs(path)

    async def _zip_with_subfolders(self, zip_buffer: BytesIO, folder: str, path: str) -> BytesIO:
        """Create zip with all files(include all folders)

        Parameters:

            zip_buffer: BytesIO object
            folder: name of folder
            path: path to folder

        Returns:

            BytesIO
        """
        for item in self.filesystem.scandir(f"{path}/{folder}"):
            if item.is_dir:
                await self._zip_with_subfolders(
                    zip_buffer, item.name if folder == "." else f"{folder}/{item.name}", path=path
                )
            else:
                file = self.filesystem.readbytes(item.name if folder == "." else f"{path}/{folder}/{item.name}")
                with ZipFile(zip_buffer, "a", ZIP_DEFLATED, False) as zip_file:
                    zip_file.writestr((item.name) if folder == "." else (f"{folder}/{item.name}"), file)
        return zip_buffer

    async def _split_path(self, path_to_file: str) -> Tuple[str, str]:
        """
        Spliting path

        Parameters:

            path_to_file: the path to be splited

        Return:

            tuple with name and path to this file/folder
        """
        splited_path = path_to_file.split("/")
        name = str(splited_path[-1])
        path = "/".join(splited_path[:-1])
        return name, path
