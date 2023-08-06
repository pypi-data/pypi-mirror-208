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


"""A library that implements serialization of any data objects as JSON data.

A common use case that Python's standard library does not provide a satisfying solution for yet is mapping data objects
to JSON data and vice versa. The package :mod:`anyjsonthing` implements an out-of-the-box solution for this task that
(with minor restrictions) allows for serializing/deserializing any data objects as/from JSON data and reading/writing
them from/to the disk.

This package is based on the assumption that data classes should **not** maintain any internal state, but only store a
collection of data points, exposed through public attributes and properties, respectively. Hence, :mod:`anyjsonthing`
considers all instances of any class that satisfies the following criteria as serializable data objects:

* the class is not a metaclass (i.e., a sub-type of :class:`type`),
* for each required argument (without default value) of the class' ``__init__`` method, there exists an eponymous
  **public** attribute/property that allows for retrieving the value that was provided to the constructor, and
* if an argument is a (nested) dataclass, then

  * that arg has to be type-annotated (i.e., have a type hint) and
  * the class it belongs to must satisfy the same criteria.

The reason why args that belong to a data class themselves have to be type annotated is that :mod:`anyjsonthing` has to
be able to determine their type during runtime to be able to deserialize JSON data as instances of that type.

With these assumptions in place, serializing data objects as JSON data is as simple as gathering all those values of the
considered instance (by means of the according attributes/properties) that are required by the ``__init__`` method of
its :class:`type`, and combining them into a single :class:`dict`. This is exactly what the class
:class:`~anyjsonthing.serializer.Serializer` does under the hood:

.. code-block:: python

   import anyjsonthing
   from dataclasses import dataclass

   @dataclass
   class NestedDataClass:
       x: str
       y: str = "Y"

   @dataclass
   class MyDataClass:
       a: str
       b: str
       c: NestedDataClass

   some_instance = MyDataClass("A", "B", NestedDataClass("X"))

   # Step 1: serialize the instance
   json_data = anyjsonthing.Serializer.to_json(some_instance)
   assert json_data == {"a": "A", "b": "B", "c": {"x": "X", "y": "Y"}}

   # Step 2: deserialize the JSON data
   reconstructed = anyjsonthing.Serializer.from_json(MyDataClass, json_data)
   assert reconstructed == some_instance

While :mod:`anyjsonthing` has been built with a focus on :mod:`dataclasses`, it can also be used with "normal" classes.
In this case, however, args of a class' ``__init__`` method do not necessarily have an according public attribute or
property that allows for retrieving their values for serialization. Typically, :mod:`anyjsonthing` will raise an error
in any such case, with one exception. If the ``__init__`` method has a keyword-arg with default value that does not have
a matching public attribute/property, then you can tell the :class:`~anyjsonthing.serializer.Serializer` to be
**non-strict**, which means that it will simply ignore this arg. The rationale behind this is that we can still
reconstruct **some** instance from the resulting JSON representation (as the missing arg has a default value), but we
can no longer guarantee that it is identical to the original one. However, this functionality is intended to cover
corner cases, and typically should not be required. The following example illustrates the described behavior:

.. code-block:: python

   import anyjsonthing

   class AnotherDataClass(object):

       def __init__(self, a, b, c="c"):
           self.a = a   # -> Public attribute.
           self._b = b  # -> Protected attribute, exposed through a public property.
           self._c = c  # -> Protected attribute, not exposed at all.

       def __str__(self):  # -> NOTICE: this exposes everything.
           return f"AnotherDataClass(a = <{self.a}>, b = <{self._b}>, c = <{self._c}>)"

       @property
       def b(self):  # -> Public property.
           return self._b

   some_instance = AnotherDataClass("A", "B", "C")

   # Step 1: serialize the instance
   json_data = anyjsonthing.Serializer.to_json(some_instance)  # -> ERROR!
   json_data = anyjsonthing.Serializer.to_json(some_instance, strict=False)
   assert json_data == {"a": "A", "b": "B"}

   # Step 2: deserialize the JSON data
   reconstructed = anyjsonthing.Serializer.from_json(AnotherDataClass, json_data)
   assert str(reconstructed) != str(some_instance)
   assert str(reconstructed) == str(AnotherDataClass("A", "B"))

Another issue that we frequently encounter in practice is that JSON data which needs to be deserialized contains
additional object properties that do not exist in the target dataclass or normal class, respectively. To handle this
specific use case, the :meth:`~anyjsonthing.serializer.Serializer.from_json` method has an optional parameter
``ignore_unknown_props``, which allows for specifying that such additional properties should simply be ignored. This is
illustrated in the following example:

.. code-block:: python

   import anyjsonthing
   from dataclasses import dataclass

   @dataclass
   class MyDataClass:
       a: str

   deserialized = anyjsonthing.Serializer.from_json(MyDataClass, {"a": "A", "b": "B"})  # -> ERROR!
   deserialized = anyjsonthing.Serializer.from_json(MyDataClass, {"a": "A", "b": "B"}, ignore_unknown_props=True)
   assert deserialized == MyDataClass("A")


Finally, the :mod:`anyjsonthing` library provides the class :class:`~anyjsonthing.io.IO`, which combines the
functionality implemented by the :class:`~anyjsonthing.serializer.Serializer` with read/write operations. This allows
for directly serializing data objects to the disk, and thus covers the main use case targeted by :mod:`anyjsonthing`.
The following example illustrates how to use the :class:`~anyjsonthing.io.IO` class (for additional details on all
available I/O methods, please have a look at the API docs of :class:`~anyjsonthing.io.IO`):

.. code-block:: python

   import anyjsonthing

   anyjsonthing.IO.dump(some_instance, "./outputs/my-data.json")
"""


from .io import IO
from .serializer import Serializer
from .utils import Utils
