#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
#===============================================================================
# Copyright Notice
# ----------------
# Copyright (c) 2021, National Technology & Engineering Solutions of Sandia, LLC (NTESS).
#    Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
#    certain rights in this software.
# Copyright (c) 2022 William McLendon
# All rights reserved.
#
# License (3-Clause BSD)
# ----------------------
# Copyright 2021 National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.
# Copyright (c) 2022, William McLendon.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================
"""
"""
import copy
import traceback
import typing
import sys



class SENTINEL:
    """ Internal class used to indicate ``default`` is not set."""
    pass



class NO_VALIDATOR:
    """ Internal class used to indicate ``validator`` is not set."""
    pass



def strongly_typed_property(
    name: str,
    expected_type=(int, str),
    default=SENTINEL,
    default_factory=lambda: None,
    req_assign_before_use=False,
    internal_type=None,
    validator=NO_VALIDATOR,
    transform=None
):
    """
    Implements a strongly typed property in a class using the pattern
    `"9.21 Avoiding Repetitive Property Methods" from the O'Reilly
    Python Cookbook, 3rd Edition <https://learning.oreilly.com/library/view/python-cookbook-3rd/9781449357337/>`_.

    Args:
        name (str): The name of the property to create.
        expected_type (type,tuple): The *type* or a *tuple of types* enumerating allowable
            types to be assigned to the property. Default is ``(int,str)``
        default: A default value to be assigned to the tuple. Default is ``None``.
            This will be assigned without type checking.
        default_factory: Default factory method. This must be callable but is used
            when we need a complex type that can't use ``deepcopy``. Default: ``lambda: None``.
        req_assign_before_use (bool): If ``True`` then raise an exception if the value is
            used before assigned. Otherwise, the *default* value is used. Default: ``False``
        internal_type (<type>): Sets the ``<type>`` that the value is stored as (via typecast)
            internally. This is done during *assignment*.
        validator (func): A special validation function that can be called during assignment
            to provide additional checks such as list size, allowable values, etc.
            If the validator's return value is *truthy* the check suceeds, otherwise
            the check has failed and a ``ValueError`` will be raised.
            Default=None (i.e., no extra validation).
        transform (func): A function that can be used to transform the value before assignment.

    Raises:
        TypeError: if the assigned value is of the wrong type on assigmment.
        ValueError: if a *validator* is provided and the check fails (is Falsy).
        UnboundLocalError: If ``req_assign_before_use`` is True and an attempt to read
            the property is made before it's been assigned.

    """
    varname = "_" + name
    varname_set = varname + "_is_set"
    expected_type = expected_type
    validator = validator

    # Check that the validator is callable, if not then we should raise an
    # error when the property is being defined.
    if (validator is not NO_VALIDATOR) and (not callable(validator)):
        raise TypeError(f"Validator `{validator}` for property `{name}` is not callable.")

    @property
    def prop(self):
        if not hasattr(self, varname_set):
            setattr(self, varname_set, False)
        if req_assign_before_use == True and getattr(self, varname_set) == False:
            raise UnboundLocalError("Property `{}` was used before assignment.".format(name))
        if not hasattr(self, varname):
            if default is not SENTINEL:
                setattr(self, varname, copy.deepcopy(default))
            else:
                if not callable(default_factory):
                    raise TypeError(
                        "default_factory `{}` in `{}` must be callable.".format(default_factory, name)
                    )
                setattr(self, varname, default_factory())
        return getattr(self, varname)

    @prop.setter
    def prop(self, value):
        _expected_type = copy.deepcopy(expected_type)
        if not isinstance(_expected_type, typing.Iterable):
            _expected_type = (_expected_type, )
        for expected_type_i in _expected_type:
            if isinstance(value, expected_type_i):
                break
        else:
            type_names = [i.__name__ for i in _expected_type]
            #try:
            raise TypeError(
                "Invalid type assigned to `{}`, must be one of ({})".format(name, ",".join(type_names))
            )
            #except TypeError as err:
            #msg = f"!ERR> The error occurred in: "
            #for line in traceback.format_stack()[:-1]:
            #line = line.strip()
            #line = line.replace("\n", f"\n!ERR> ")
            #msg += f"!ERR> {line.strip()}\n"
            #msg += f"!ERR> TypeError: {err}"
            #raise TypeError(msg)

        if internal_type is not None:
            value = internal_type(value)

        if transform is not None:
            if callable(transform):
                value = transform(value)
                if internal_type is not None:
                    value = internal_type(value)
            else:
                raise TypeError(f"transform `{transform}` for property `{name}` is not callable.")

        if validator is not NO_VALIDATOR:
            if not validator(value):
                #try:
                raise ValueError(
                    f"Assignment of `{value}` to property `{name}` " +
                    f"failed validation check in `{validator}`."
                )
                #except ValueError as err:
                #print(f"!ERR> Traceback (most recent call last):")
                #for line in traceback.format_stack()[:-1]:
                #line = line.strip()
                #line = line.replace("\n", f"\n!ERR> ")
                #print(f"!ERR> {line.strip()}")
                #print(f"!ERR> ValueError: {err}")
                #raise err

        # Assign the value to the property
        setattr(self, varname, value)

        # Save that we've assigned the value to something
        setattr(self, varname_set, True)

    @prop.deleter
    def prop(self):
        if hasattr(self, varname):
            delattr(self, varname)
        if hasattr(self, varname_set):
            delattr(self, varname_set)

    return prop
