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


import inspect

from typing import Any
from typing import Callable


class Utils(object):
    """Implements various helper functions."""

    @staticmethod
    def fetch_args(func: Callable[..., Any]) -> tuple[list[str], list[str]]:
        """Retrieves the names of all args/kwargs of the given ``func``\ tion (or callable).

        Note:
            This method ignores starred ``*args`` or ``**kwargs``.

        Args:
            func: The function (or more generally, callable) that args/kwargs are retrieved of.

        Returns:
            required_args: The names of all required args, which do not have a default value.
            optional_args: The names of all optional args, which do have a default value.
        """

        # First, we retrieve a full arg-spec of the func using the Python's inspect package, which contains all
        # information we need.
        arg_spec = inspect.getfullargspec(func)

        # We partition the args specified in the arg_spec into required and optional (i.e., with default value) args.
        required_args = []
        optional_args = []

        # A full arg-spec distinguishes "normal" args and kwargs from kw-only args and starred *args and **kwargs. (We
        # completely ignore the latter.) To that end, all normal args and kwargs are stored as a single "args" tuple,
        # and the according default values are stored as tuple "defaults". This "defaults" describe values for a tail of
        # "args", which is possible, as kw-args with default values have to show up last in the "args" tuple.
        num_normal_args = len(arg_spec.args)
        num_normal_args_with_default = len(arg_spec.defaults or [])  # -> defaults can be None.
        required_args.extend(arg_spec.args[:num_normal_args - num_normal_args_with_default])
        optional_args.extend(arg_spec.args[len(required_args):])

        # Kw-only args are stored (in a full arg-spec) as tuple "kwonlyargs" and the according default values as dict
        # "kwonlydefaults", which maps parameter names to default values.
        for kw_only_arg in arg_spec.kwonlyargs:

            # Based on whether the arg has a default value, we decide whether to add it to the required or optional
            # args.
            if (
                    arg_spec.kwonlydefaults and  # -> NOTICE: this can be None.
                    kw_only_arg in arg_spec.kwonlydefaults
            ):  # -> The arg has a default value.

                optional_args.append(kw_only_arg)

            else:  # -> The arg does not have a default value.

                required_args.append(kw_only_arg)

        return required_args, optional_args

    @staticmethod
    def fetch_attributes(instance: Any) -> list[str]:
        """Retrieves the names of all public attributes of the given ``instance``.

        Note:
            In contrast to :meth:`~.fetch_properties`, this method expects an instance of a class as opposed to a
            :class:`type`.

        Args:
            instance: The instance that attributes are retrieved of.

        Returns:
            A :class:`list` of the names of all public attributes fo the provided ``instance``.
        """

        return [
                x
                for x in instance.__dict__
                if not x.startswith("_")  # -> We only consider public attributes.
        ]

    @classmethod
    def fetch_init_args(cls, target_type: type) -> tuple[list[str], list[str]]:
        """Retrieves the names of all args/kwargs of the ``__init__`` method of the given ``target_type``.

        Args:
            target_type: The class that contains the ``__init__`` method that args retrieved of.

        Returns:
            required_args: The names of all required args, which do not have a default value.
            optional_args: The names of all optional args, which do have a default value.
        """

        required_args, optional_args = cls.fetch_args(target_type.__init__)
        return (
                required_args[1:],  # -> [1:] to cut off the first arg "self".
                optional_args
        )

    @staticmethod
    def fetch_properties(target_type: type) -> list[str]:
        """Retrieves the names of all public properties of the given ``target_type``.

        Note:
            In contrast to :meth:`~.fetch_attributes`, this method expects a :class:`type` as opposed to an instance of
            a class.

        Args:
            target_type: The :class:`type` that properties are retrieved of.

        Returns:
            A :class:`list` of the names of all public attributes fo the provided ``target_type``.
        """

        property_names = []  # -> Used to store the names of all found public properties.

        for name, _ in inspect.getmembers(target_type, lambda f: isinstance(f, property)):

            # We only consider public properties (i.e., we ignore properties starting with an underscore).
            if name.startswith("_"):

                continue

            property_names.append(name)

        return property_names

    @staticmethod
    def fetch_type_annotations(func: Callable[..., Any]) -> dict[str, Any]:
        """Creates a :class:`dict` that maps the names of args of the given ``func`` to their type annotations.

        Args without type annotation are excluded.

        Args:
            func: The callable that the mapping is created for.

        Returns:
            The created :class:`dict`, mapping arg names to type annotations.
        """

        return {
                p.name: p.annotation
                for p in inspect.signature(func).parameters.values()
                if (
                        p.annotation is not None and                 # -> The arg has no type annotation.
                        p.annotation is not inspect.Parameter.empty  # -> The type of special args like self/cls.
                )
        }
