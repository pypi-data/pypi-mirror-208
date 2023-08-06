# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                     #
#   Copyright (c) 2023, Patrick Hohenecker                                            #
#                                                                                     #
#   All rights reserved.                                                              #
#                                                                                     #
#   Redistribution and use in source and binary forms, with or without                #
#   modification, are permitted provided that the following conditions are met:       #
#                                                                                     #
#       * Redistributions of source code must retain the above copyright notice,      #
#         this list of conditions and the following disclaimer.                       #
#       * Redistributions in binary form must reproduce the above copyright notice,   #
#         this list of conditions and the following disclaimer in the documentation   #
#         and/or other materials provided with the distribution.                      #
#                                                                                     #
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS               #
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT                 #
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR             #
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER       #
#   OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,          #
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,               #
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR                #
#   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF            #
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING              #
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS                #
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                      #
#                                                                                     #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import json
import os
import pathlib

import anyjsonthing.serializer as serializer

from typing import Any
from typing import Iterable
from typing import TypeVar


_T = TypeVar("_T")


class IO(object):
    """Implements direct serialization/deserialization of any data objects as JSON data to/from the disk.

    Note:
        This class is more conveniently accessible via ``anyjsonthing.IO``.

    Under the hood, the methods of this class simply invoke the functionality implemented by the
    :class:`~.serializer.Serializer`, and combine the same with the required read/write operations.
    """

    #  METHODS  ########################################################################################################

    @staticmethod
    def dump(anything: Any, path: os.PathLike) -> None:
        """Serializes ``anything`` and writes it as JSON file to the specified ``path``.

        Args:
            anything: The instance to serialize.
            path: The path that the created JSON representation of ``anything`` is written to.
        """

        json_data = json.dumps(
                serializer.Serializer.to_json(anything)
        )
        target_path = pathlib.Path(path)
        target_path.write_text(json_data)

    @staticmethod
    def dump_all(anything: Iterable[Any], path: os.PathLike) -> None:
        """Serializes all elements of ``anything`` and writes them as single JSON file to the specified ``path``.

        Args:
            anything: The instances to serialize .
            path: The path that the created JSON representation of ``anything`` is written to.
        """

        json_data = json.dumps(
                [serializer.Serializer.to_json(x) for x in anything]
        )

        target_path = pathlib.Path(path)
        target_path.write_text(json_data)

    @staticmethod
    def load(cls: type[_T], path: os.PathLike, ignore_unknown_props: bool = False) -> _T:
        """Loads and deserialized the JSON representation a single instance of ``cls`` from the specified ``path``.

        Args:
            cls: The :class:`type` of the deserialized instance.
            path: The path that the deserialized JSON representation is loaded from.
            ignore_unknown_props: Indicates whether superfluous JSON object properties encountered during
                deserialization of the loaded JSON data should be ignored as opposed to raising an error.

        Returns:
            The created instance of the specified ``cls``.
        """

        source_path = pathlib.Path(path)
        json_data = json.loads(source_path.read_text())
        return serializer.Serializer.from_json(cls, json_data, ignore_unknown_props=ignore_unknown_props)

    @staticmethod
    def load_all(cls: type[_T], path: os.PathLike, ignore_unknown_props: bool = False) -> list[_T]:
        """Loads and deserialized the JSON representation of multiple instances of ``cls`` from the specified ``path``.

        Args:
            cls: The :class:`type` of the deserialized instance.
            path: The path that the deserialized JSON representation is loaded from.
            ignore_unknown_props: Indicates whether superfluous JSON object properties encountered during
                deserialization of the loaded JSON data should be ignored as opposed to raising an error.

        Returns:
            A :class:`list` of all created instances of the specified ``cls``.
        """

        source_path = pathlib.Path(path)
        json_data = json.loads(source_path.read_text())
        return [
                serializer.Serializer.from_json(cls, x, ignore_unknown_props=ignore_unknown_props)
                for x in json_data
        ]
