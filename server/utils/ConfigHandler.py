import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from utils.Logger import LoggerClass

logger = LoggerClass.getSubLogger(__name__)
logger.setLevel(logger.INFO)  # type: ignore


class IConfigHandler(ABC):
    @abstractmethod
    def __init__(self, file: str, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def write(self, data: dict) -> bool:
        pass

    @abstractmethod
    def read(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def hasData(self) -> bool:
        pass

    @abstractmethod
    def initializeConfig(self) -> None:
        pass

    @abstractmethod
    def createBackup(self) -> None:
        pass


class FileHelper(IConfigHandler):
    """A simple helper class to read and save json from files."""

    def __init__(self, file: str, *args, **kwargs) -> None:
        """Initialize the file helper class.

        Args:
            file (Path): A pathlib.Path object to the config file.
        """
        self._file = Path(file)
        self._tempfile = self._file.with_suffix(self._file.suffix + ".tmp")

    def write(self, data: dict) -> bool:
        """Write all data into the configuration file.
        Avoids config corruption by writing into a temp file first.

        Args:
            data (dict): The data to write to the file.

        Returns:
            bool: True if the write was sucessful.
        """
        try:
            with open(self._tempfile, mode="w") as f:
                json.dump(data, f, indent=4)
        except Exception as E:
            logger.exception(E)
            if self._tempfile.exists():
                self._tempfile.unlink()
            return False
        else:
            self._tempfile.replace(self._file)
            return True

    def read(self) -> dict[str, Any]:
        """Read all configration options from file.

        Raises:
            E (Exception): If there was an error while reading the file.

        Returns:
            dict: The data that was read from the file.
        """
        try:
            with open(self._file, mode="r") as f:
                return json.load(f)
        except Exception as E:
            logger.exception(E)
            raise E

    def hasData(self) -> bool:
        """Check if the file exists and can be read.

        Returns:
            bool: True if the file exists and can be read,
                False otherwise.
        """
        return self._file.is_file() and bool(self.read())

    def initializeConfig(self) -> None:
        pass

    def createBackup(self) -> None:
        """Create a duplicate of the file."""
        backupFile = self._file.with_suffix(self._file.suffix + ".backup")
        backupFile.write_bytes(self._file.read_bytes())
        logger.info(f"Backup of {self._file} created at {backupFile}")


if __name__ == "__main__":
    print("There is no point running this file directly")
