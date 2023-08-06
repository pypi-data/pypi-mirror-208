import os
import os.path
import socket
import tempfile
import urllib.error
from typing import Optional
from urllib.parse import urlparse
from urllib.request import urlretrieve
from uuid import uuid4

import gdown  # type: ignore[import]

DOWNLOAD_MODEL_TIMEOUT_SECONDS = 5 * 60


class FileDownloadFailedException(Exception):
    pass


class FileCreationFailedException(Exception):
    pass


class FilesDataInterface:
    @staticmethod
    def create_temporary_file(content: str) -> str:
        try:
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "w") as tmp:
                tmp.write(content)
        except Exception as e:
            msg = f"Failed to create temporary file with error {e}"
            raise FileCreationFailedException(msg) from e
        return path

    @staticmethod
    def download_temporary_file(
        file_url: str,
        temp_file_prefix: str = "",
        temp_file_suffix: str = "",
        timeout_seconds: Optional[int] = DOWNLOAD_MODEL_TIMEOUT_SECONDS,
    ) -> str:
        """
        Downloads a file to /tempfile.gettempdir/.

        Args:
        :param file_url: The url to downlaod from
        :param temp_file_prefix: The predix to add to the file in the temporary folder
        :param temp_file_suffix: The suffix to add to the file in the temporary folder
        :param timeout_seconds: The timeout in seconds to pass to urllib.setdefaulttimeout. Pass None for no timeout.
        The default timeout is DOWNLOAD_MODEL_TIMEOUT_SECONDS;
        :return: The file's path.
        :raises: FileDownloadFailedException
        """
        tmp_dir = tempfile.gettempdir()
        file_name = temp_file_prefix + str(uuid4()) + temp_file_suffix
        file_path = tmp_dir + os.path.sep + file_name

        # GET THE URL'S FILE EXTENSION
        parsed_url = urlparse(file_url)
        _, file_extension = os.path.splitext(parsed_url.path)

        if file_extension:
            file_path = file_path + file_extension

        # Proprietary downloads
        if "drive.google.com" in file_url:
            FilesDataInterface._download_google_drive_file(file_url, file_path)
        else:
            # TODO: Use requests with stream and limit the file size and timeouts.
            socket.setdefaulttimeout(timeout_seconds)
            try:
                urlretrieve(file_url, file_path)  # nosec: B310
            except urllib.error.ContentTooShortError as ex:
                raise FileDownloadFailedException("File download did not finish correctly " + str(ex))

        return file_path

    @staticmethod
    def save_bytes_to_file(file_bytes: bytes, file_name: Optional[str] = None, mode: str = "wb") -> str:
        """
        Writes a buffer to a local file.
        :param file_bytes: The bytes to write.
        :param file_name: The name of the file to create. Defaults to /tempfile.gettempdir/{uuid4} if not specified.
        :param mode: The write open mode.
        """
        file_name = file_name or tempfile.gettempdir() + os.path.sep + str(uuid4())
        with open(file_name, mode) as new_file:
            new_file.write(file_bytes)
        return file_name

    @staticmethod
    def _download_google_drive_file(google_drive_url: str, destination_file_name: str) -> None:
        """
        Wraps gdown package to download files
        :param google_drive_url: The google drive file url.
        :param destination_file_name: The full path the file to save the google drive file into.
        :return:
        """
        try:
            gdown.download(google_drive_url, destination_file_name, quiet=False)
        except Exception as ex:
            raise FileDownloadFailedException("File download did not finish correctly " + str(ex))
