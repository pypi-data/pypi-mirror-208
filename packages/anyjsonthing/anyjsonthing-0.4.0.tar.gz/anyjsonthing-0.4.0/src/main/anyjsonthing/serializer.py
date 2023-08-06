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


import collections
import copy
import itertools
import types
import typing

import anyjsonthing.utils as utils

from typing import Any
from typing import Optional
from typing import TypeVar
from typing import Union


_T = TypeVar("_T")


class Serializer(object):
    """Implements the logic for serializing/deserializing any data objects as/from JSON data.

    Note:
        This class is more conveniently accessible via ``anyjsonthing.Serializer``.

    For details on which classes are considered as valid providers of serializable data objects (in strict and
    non-strict mode), see :mod:`anyjsonthing`.
    """

    #  METHODS  ########################################################################################################

    @classmethod
    def is_serializable(cls, anything: Any, strict: bool = True) -> bool:
        """Evaluates whether ``anything`` is serializable+deserializable (by the :mod:`anyjsonthing` library).

        Warning:
            If you want to check whether a specific :class:`type` is serializable, then you have to provide ``anything``
            that is an **instance** of the same. The simple reason for this is that we cannot determine which attributes
            instances of the considered :class:`type` provide during runtime without having access to an actual instance
            of that :class:`type`.

        Note:
            If ``anything`` is a :class:`type` as opposed to an instance of a class, then this method returns ``False``,
            since :class:`type`\ s are not serializable.

        Args:
            anything: The evaluated instance.
            strict: Indicates whether strict mode is used.

        Returns:
            ``True`` if ``anything`` is serializable, and ``False`` otherwise.
        """

        # First, we check if the provided anything is a type as opposed to an instance of a class, which is never
        # serializable.
        if isinstance(anything, type):

            return False

        # None as well as the primitive types str, int, float, and bool are always serializable.
        if anything is None or isinstance(anything, (str, int, float, bool)):

            return True

        # Lists and tuples are serializable if and only if their elements are serializable.
        if isinstance(anything, (list, tuple)):

            return all(cls.is_serializable(x) for x in anything)

        # Dicts are serializable if and only if all their keys are strings and their values are serializable.
        if isinstance(anything, dict):

            return (
                    all(isinstance(x, str) for x in anything.keys()) and
                    all(cls.is_serializable(x) for x in anything.values())
            )

        # If we arrive at this point, then we have to check the details of the provided instance. To that end, we next
        # fetch the names of all args of the init method of anything's type as well as the names of all public
        # attributes and properties of anything.
        required_init_args, optional_args = utils.Utils.fetch_init_args(type(anything))
        attributes = utils.Utils.fetch_attributes(anything)
        properties = utils.Utils.fetch_properties(type(anything))

        # Before we can check if anything is serializable, we have to determine the args that need to have corresponding
        # attributes/properties. In strict mode, this is the case for all args. In non-strict mode, only required args
        # (i.e., those without default value) need to satisfy this criterion.
        args_to_check = required_init_args
        if strict:

            args_to_check.extend(optional_args)

        # We ensure that for every required arg of init there is an eponymous attribute/property that allows for
        # retrieving the value that is required for reconstructing instances.
        for arg in required_init_args:

            if arg not in attributes and arg not in properties:  # -> No attribute/property exists for the current arg.

                return False

        # If we arrive at this point, we successfully confirmed that there are attributes/properties for all args needed
        # to reconstruct anything.
        return True

    @staticmethod
    def from_json(cls: type[_T], json: dict[str, Any], ignore_unknown_props: bool = False) -> _T:
        """Deserializes the provided ``json`` data into an instance of the specified ``cls``.

        Args:
            cls: The :class:`type` of the instance that is described by the provided ``json`` data.
            json: The JSON representation of the instance that is deserialized.
            ignore_unknown_props: Indicates whether superfluous object properties in the given ``json`` data (which do
                not exist in the ``cls``) should be ignored as opposed to raising an error.

        Returns:
            The deserialized instance of ``cls``.

        Raises:
            ValueError: If the ``json`` data is missing a required arg of the ``__init__`` method of the target ``cls``
                (or any nested type) or if ``ignore_unknown_props`` is ``False`` and it specifies properties that are
                unknown to the latter.
        """

        return Serializer._dejsonify(json, type_annotation=cls, ignore_unknown_props=ignore_unknown_props)

    @classmethod
    def to_json(cls, anything: Any, strict: bool = True) -> Any:
        """Serializes ``anything``, creating a JSON representation of the same.

        Args:
            anything: The data object that is serialized as JSON data.
            strict: Indicates whether strict mode is used.

        Returns:
            The created JSON representation of ``anything``.

        Raises:
            ValueError: If ``anything`` cannot be serialized, as it is an instance of a class that is not considered as
                a valid provider of data objects.
        """

        # First and foremost, we ensure that the given instance is actually serializable.
        if not cls.is_serializable(anything, strict=strict):

            raise ValueError("The given <anything> is not serializable")

        return cls._jsonify(anything)

    @classmethod
    def _dejsonify(
            cls,
            anything: Any,
            type_annotation: Union[None, type, types.GenericAlias, typing._GenericAlias] = None,
            ignore_unknown_props: bool = False
    ) -> Any:
        """Maps ``anything`` describing JSON data to the according representation described by the ``type_annotation``.

        Args:
            anything: The JSON data that is mapped to the corresponding Python representation.
            type_annotation: Describes the target Python object to map ``anything`` to.
            ignore_unknown_props: Indicates whether superfluous JSON object properties encountered during processing of
                ``anything`` should be ignored as opposed to raising an error.

        Returns:
            The created Python representation of ``anything``.

        Raises:
            ValueError: If ``anything`` could not be mapped for some reason (e.g., due to ``anything`` not being valid
                JSON data).
        """

        # This method does not implement actual functionality, but only delegates to specialized methods based on the
        # type of anything as well as the type annotation.

        if anything is None or isinstance(anything, (str, int, float, bool)):

            return anything

        elif isinstance(anything, list):

            return cls._dejsonify_array(
                    anything,
                    type_annotation=type_annotation,
                    ignore_unknown_props=ignore_unknown_props
            )

        elif isinstance(anything, dict):

            # For dicts, we have to distinguish between those that should be mapped to Python dicts and those that
            # should be mapped to other class instances. To that end, we consider the type annotation, which may
            # provided additional information. If no type annotation is provided, then we always map to dicts.

            if type_annotation is None:  # -> No type annotation was provided.

                return cls._dejsonify_dict(anything, ignore_unknown_props=ignore_unknown_props)

            elif (
                    isinstance(type_annotation, types.GenericAlias) and
                    type_annotation.__origin__ == dict
            ):  # -> The type annotation is a generic type alias dict[_, _].

                return cls._dejsonify_dict(
                        anything,
                        type_annotation=type_annotation,
                        ignore_unknown_props=ignore_unknown_props
                )

            elif isinstance(type_annotation, typing._GenericAlias):  # -> The TA is a custom generic class.

                return cls._dejsonify_object(
                        anything,
                        target_type=type_annotation.__origin__,
                        ignore_unknown_props=ignore_unknown_props
                )

            else:  # -> The type annotation is not a generic type annotation, but an actual type.

                if type_annotation == dict:

                    return cls._dejsonify_dict(
                            anything,
                            type_annotation=type_annotation,
                            ignore_unknown_props=ignore_unknown_props
                    )

                else:
                    return cls._dejsonify_object(
                            anything,
                            target_type=type_annotation,
                            ignore_unknown_props=ignore_unknown_props
                    )

        else:

            raise ValueError(
                    "The provided <anything> could not be mapped to an equivalent Python object. "
                    "Are you sure it is valid JSON data?"
            )

    @classmethod
    def _dejsonify_array(
            cls,
            json_array: list,
            type_annotation: Union[None, type, types.GenericAlias] = None,
            ignore_unknown_props: bool = False
    ) -> Union[list, tuple]:
        """Maps the provided ``json_array`` to the according :class:`list` or :class:`tuple`.

        If no ``type_annotation`` is provided, then the ``json_array`` is always mapped to a :class:`list`.
        Technically, the ``json_array`` is of course already a :class:`list`. However, the optional arg
        ``type_annotation`` allows for specifying the exact target :class:`list` or :class:`tuple`, which in turn incurs
        required parsing of elements. An example of a such a ``type_annotation`` could look
        like this: ``list[MyClass]`` or ``tuple[dict[str, MyClass], ...]``.

        Args:
            json_array: The JSON array that is mapped to a :class:`list` or :class:`tuple`.
            type_annotation: A type annotation that describes the target :class:`type`.
            ignore_unknown_props: Indicates whether superfluous JSON object properties encountered during processing of
                the ``json_array`` should be ignored as opposed to raising an error.

        Returns:
            The created :class:`list` or :class:`tuple`.

        Raises:
            ValueError: If the ``type_annotation`` is specified (i.e., not ``None`` and not ``Any``), but
                is neither :class:`list`, nor `class:`tuple`, nor a generic type alias of these two :class:`type`\ s.
        """

        # If the type annotation is Any, then we simply set it to None. There is no need to treat this case separately.
        if type_annotation == Any:

            type_annotation = None

        # We ensure that the type annotation, if specified, actually describe a list or a tuple.
        if (
                type_annotation is not None and
                type_annotation != list and
                type_annotation != tuple and
                (
                        not isinstance(type_annotation, types.GenericAlias) or
                        (type_annotation.__origin__ != list and type_annotation.__origin__ != tuple)
                )
        ):

            raise ValueError(f"The given <type_annotation> does not describe a list or tuple: <{type_annotation}>")

        # We determine the target type based on the provided type hint, and use list as a default.
        if isinstance(type_annotation, types.GenericAlias):

            array_type = type_annotation.__origin__

        elif isinstance(type_annotation, type):

            array_type = type_annotation

        else:

            array_type = list

        # Next, we recursively parse the elements of the array, and combine them into a single list/tuple.
        element_type_annotation = (
                type_annotation.__args__[0]  # -> NOTICE: This also removes the "..." from tuples.
                if isinstance(type_annotation, types.GenericAlias) else
                None
        )
        return array_type(
                cls._dejsonify(x, type_annotation=element_type_annotation, ignore_unknown_props=ignore_unknown_props)
                for x in json_array
        )

    @classmethod
    def _dejsonify_dict(
            cls,
            json_object: dict,
            type_annotation: Optional[types.GenericAlias] = None,
            ignore_unknown_props: bool = False
    ) -> dict:
        """Maps the provided ``json_object`` to the according :class:`dict`.

        Technically, the ``json_object`` is of course already a :class:`dict`. However, the optional arg
        ``type_annotation`` allows for specifying types of the keys of target :class:`dict` (e.g., as instances of a
        specific class), which in turn incurs required parsing. An example of a such a ``type_annotation`` could look
        like this: ``dict[str, list[MyClass]]``.

        Args:
            json_object: The JSON object that is mapped to a :class:`dict`.
            type_annotation: A type annotation that describes the target :class:`dict`.
            ignore_unknown_props: Indicates whether superfluous JSON object properties encountered during processing of
                the ``json_object`` should be ignored as opposed to raising an error.

        Returns:
            The created :class:`dict`.

        Raises:
            ValueError: If the ``type_annotation`` is specified (i.e., not ``None`` and not ``Any``), but does not
                describe a :class:`dict`.
        """

        # If the type annotation is Any, then we simply set it to None. There is no need to treat this case separately.
        if type_annotation == Any:

            type_annotation = None

        # We ensure that the type annotation, if specified, actually describe a dict.
        if (
                type_annotation is not None and
                type_annotation.__origin__ != dict
        ):

            raise ValueError(f"The given <type_annotation> does not describe a dict: <{type_annotation}>")

        # Next, we recursively dejsonify the values of the dict.
        value_type_annotation = (
                None
                if type_annotation is None else
                type_annotation.__args__[1]  # -> That is the type hint for the values. ([0] describes keys.)
        )
        return {
                k: cls._dejsonify(v, type_annotation=value_type_annotation, ignore_unknown_props=ignore_unknown_props)
                for k, v in json_object.items()
        }

    @classmethod
    def _dejsonify_object(
            cls,
            json_object: dict[str, Any],
            target_type: type[_T],
            ignore_unknown_props: bool = False
    ) -> _T:
        """Maps the provided ``json_object`` to the according instance of the ``target_type``.

        Notice that this method is **not** supposed to be used for JSON objects that should be mapped to
        :class:`dict`\ s, which is implemented by the method :meth:`~._dejsonify_dict`.

        Args:
            json_object: The JSON object that is mapped to an instance of the ``target_type``.
            target_type: The :class:`type` that the ``json_object`` describes an instance of.
            ignore_unknown_props: Indicates whether superfluous JSON object properties encountered during processing of
                the ``json_object`` should be ignored as opposed to raising an error.

        Returns:
            The created instance of the ``target_type``.
        """

        # To be able to sanitize the provided JSON data, we first retrieve all args of the constructor of the given
        # type together with their type annotations.
        required_args, optional_args = utils.Utils.fetch_init_args(target_type)
        all_args = set(itertools.chain(required_args, optional_args))
        type_annotations = collections.defaultdict(
                lambda: None,
                utils.Utils.fetch_type_annotations(target_type.__init__)
        )

        # Now, we first ensure that all required args are specified.
        for some_arg in required_args:

            if some_arg not in json_object:

                raise ValueError(f"Missing required arg <{some_arg}> in the given <json_object>")

        # Next, we handle unknown args. If unknown args are ignored, then we remove them from considered JSON object.
        # Otherwise, we raise an error.
        json_object = copy.deepcopy(json_object)  # -> Ensures that deleting keys doesn't corrupt the original instance.
        for some_arg in list(json_object.keys()):

            if some_arg not in all_args:

                if ignore_unknown_props:

                    del json_object[some_arg]

                else:

                    raise ValueError(f"Encountered unknown arg <{some_arg}> in the given <json_object>")

        # Finally, we are ready to parse the args and create the needed instance.
        parsed_args = {
                k: cls._dejsonify(v, type_annotation=type_annotations[k], ignore_unknown_props=ignore_unknown_props)
                for k, v in json_object.items()
        }
        return target_type(**parsed_args)

    @classmethod
    def _jsonify(cls, anything: Any) -> Any:
        """Maps ``anything`` to the according JSON representation.

        Note:
            This method does **not** ensure that the resulting JSON data is deserializable, which must be manually
            evaluated by means of :meth:`~.is_serializable`.

        Args:
            anything: The data object that is mapped to the corresponding JSON representation.

        Returns:
            The created JSON representation of ``anything``.
        """

        if anything is None or isinstance(anything, (str, int, float, bool)):

            return anything

        elif isinstance(anything, (list, tuple)):

            return cls._jsonify_array(anything)

        elif isinstance(anything, dict):

            return cls._jsonify_dict(anything)

        else:

            return cls._jsonify_object(anything)

    @classmethod
    def _jsonify_array(cls, some_array: Union[list, tuple]) -> list:
        """Maps ``some_array`` to the according JSON array.

        To that end, the elements of ``some_array`` are recursively mapped to JSON data (by means of :meth:`~._jsonfy`)
        as well.

        Note:
            This method does **not** ensure that the resulting JSON array is deserializable, which must be manually
            evaluated by means of :meth:`~.is_serializable`.

        Args:
            some_array: The array that is mapped to a corresponding JSON array.

        Returns:
            The created JSON representation of ``some_array``.
        """

        return [cls._jsonify(x) for x in some_array]

    @classmethod
    def _jsonify_dict(cls, some_dict: dict[Any, Any]) -> dict[str, Any]:
        """Maps ``some_dict`` to the according JSON object.

        To that end, the keys of ``some_dict`` are converted into :class:`str`\ s and each value is recursively mapped
        to JSON data by means of :meth:`~._jsonify`.

        Note:
            This method does **not** ensure that the resulting JSON object is deserializable, which must be manually
            evaluated by means of :meth:`~.is_serializable`.

        Args:
            some_dict: The :class:`dict` that is mapped to a corresponding JSON object.

        Returns:
            The created JSON representation of ``some_dict``.
        """

        return {str(k): cls._jsonify(v) for k, v in some_dict.items()}

    @classmethod
    def _jsonify_object(cls, some_object: Any) -> dict[str, Any]:
        """Maps an object to the according JSON representation.

        Notice that this method is **not** supposed to be used for :class:`dict`\ s, which are mapped to JSON objects as
        well, but for instances of classes that (other than :class:`dict`) cannot be directly translated to JSON data.

        Note:
            This method does **not** ensure that the resulting JSON object is deserializable, which must be manually
            evaluated by means of :meth:`~.is_serializable`.

        Instead, this method takes a best-effort approach in that it includes as many constructor args in the created
        JSON object as are available via attributes and properties.

        Args:
            some_object: The instance that is mapped to a corresponding JSON object.

        Returns:
            The created JSON representation of ``some_object``.
        """

        # First, we fetch the names of all (public) attributes and properties of the provided instance as well as the
        # names of all init-args of the class that the object belongs to.
        attrs_and_props = utils.Utils.fetch_attributes(some_object) + utils.Utils.fetch_properties(type(some_object))
        init_args = itertools.chain.from_iterable(
                utils.Utils.fetch_init_args(type(some_object))
        )

        # Next, we serialize all needed attributes/properties and combine them into a single dict.
        return {
                arg: cls._jsonify(getattr(some_object, arg))
                for arg in init_args
                if arg in attrs_and_props  # -> This is needed if some args don't have a public attribute/property.
        }
