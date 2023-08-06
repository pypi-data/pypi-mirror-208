# Copyright (C) 2021,2022,2023 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Abstract class for all supported formats."""

import argparse
import gettext
import io
import logging
from abc import ABC, abstractmethod
from importlib import import_module
from pathlib import Path
from typing import Any

from txt2ebook.helpers import lower_underscore
from txt2ebook.models import Book

logger = logging.getLogger(__name__)


class BaseWriter(ABC):
    """Base class for writing to ebook format."""

    def __init__(self, book: Book, opts: argparse.Namespace) -> None:
        """Create a Writer module.

        Args:
            book(Book): The book model which contains metadata and table of
            contents of volumes and chapters.
            opts(argparse.Namespace): The configs from the command-line.

        Returns:
            None
        """
        self.book = book
        self.config = opts

        config_lang = self.config.language.replace("-", "_")
        self.langconf = import_module(f"txt2ebook.languages.{config_lang}")

        self._load_translation()
        self.__post_init__()

    def __getattr__(self, key: str) -> Any:
        """Get a value of the config based on key name.

        Args:
            key(str): The key name of the config.

        Returns:
            Any: The value of a key, if found. Otherwise raise AttributeError
            exception.
        """
        if hasattr(self.config, key):
            return getattr(self.config, key)

        raise AttributeError(f"invalid config key: '{key}'!")

    def _load_translation(self):
        localedir = Path(Path(__file__).parent.parent, "locales")
        translation = gettext.translation(
            "txt2ebook", localedir=localedir, languages=[self.config.language]
        )
        self._ = translation.gettext

    def _output_filename(self, extension: str) -> Path:
        if self.config.filename_format:
            filename = self.book.filename_format(self.config.filename_format)
        else:
            filename = "default"

            if self.output_file:
                filename = str(self.output_file)
            elif isinstance(
                self.input_file, (io.TextIOWrapper, io.BufferedReader)
            ):
                if self.input_file.name != "<stdin>":
                    filename = self.input_file.name
            elif self.book.title:
                filename = self.book.title

        file = Path(filename)
        return Path(file.parent, lower_underscore(file.stem)).with_suffix(
            extension
        )

    @abstractmethod
    def write(self) -> None:
        """Generate text files."""

    def __post_init__(self) -> None:
        """Post init code for child class."""
