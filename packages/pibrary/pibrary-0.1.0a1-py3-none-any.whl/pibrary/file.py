from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

from loguru import logger


class File:
    """
    Class to read and write files.
    """

    def __init__(self, path: str, *args, **kwargs) -> None:
        """
        Creates an instance of File with specified file path.

        Args:
            path: Path of the file for read/write.

        """
        self._mode = "r"
        self._path = Path(path)
        self._obj_file = None

    def read(self) -> File:
        """
        Sets the io mode to read, and path variable to read from.

        Returns: Class object to chain with other methods.

        """
        self._mode = "r"
        # Check if file exists
        if not self._path.exists():
            logger.exception(f"File not found at {self._path}")
            logger.critical("Terminating the process.")
            sys.exit()
        return self

    def write(self, obj_file: Any) -> File:
        """
        Sets the io mode to write, and path variable to write to.

        Args:
            obj_file: Object to save like dict for j

        Returns: Class object to chain with other methods.

        """
        self._mode = "w"
        self._obj_file = obj_file
        # Create parent directory if not exists for writing
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            logger.success(f"Created directory at {self._path.parent}.")
        return self

    def json(self, **kwargs) -> Optional[Dict[str, List[str]]]:
        """
        Reads or writes json file according to mode set by read/write method.

        Args:
            **kwargs: Keyword arguments for diff read/write like. Eg:nt=4 for json read.

        Returns: obj_file if read mode else nothing is returned.

        """
        try:
            if (self._mode == "w") and (self._obj_file is not None):
                json.dump(self._obj_file, open(self._path, "w"), **kwargs)
                logger.success(f"File written at {self._path}")
            elif self._mode == "r":
                self._obj_file = json.load(open(self._path, "r"))
                logger.success(f"File read from {self._path}")
                return self._obj_file
        except:
            if self._mode == "w":
                logger.exception(f"Cannot write file at {self._path}")
            else:
                logger.exception(f"Cannot read file from {self._path}")
            logger.critical("Terminating the process.")
            sys.exit()

    def pickle(self):
        """
        Reads or writes pickle file according to mode set by read/write method.

        Returns: obj_file if read mode else nothing is returned.

        """
        try:
            if (self._mode == "w") and (self._obj_file is not None):
                joblib.dump(self._obj_file, self._path)
                logger.success(f"File written at {self._path}")
            elif self._mode == "r":
                self._obj_file = joblib.load(self._path)
                logger.success(f"File read from {self._path}")
                return self._obj_file
        except:
            if self._mode == "w":
                logger.exception(f"Cannot write file at {self._path}")
            else:
                logger.exception(f"Cannot read file from {self._path}")
            logger.critical("Terminating the process.")
            sys.exit()

    def csv(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        Reads or writes csv file according to mode set by read/write method.

        Returns: Dataframe if read mode else nothing is returned.

        """
        try:
            if (self._mode == "w") and (self._obj_file is not None):
                self._obj_file.to_csv(self._path, index=False, **kwargs)
                logger.success(f"File written at {self._path}")
            elif self._mode == "r":
                self._obj_file = pd.read_csv(self._path, **kwargs)
                logger.success(f"File read from {self._path}")
                return self._obj_file
        except:
            if self._mode == "w":
                logger.exception(f"Cannot write file at {self._path}")
            else:
                logger.exception(f"Cannot read file from {self._path}")
            logger.critical("Terminating the process.")
            sys.exit()
