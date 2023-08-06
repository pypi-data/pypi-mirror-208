# This file is part of project py-tailwind-utils
#
# Copyright (c) [2023] by Monallabs.in.
# This file is released under the MIT License.
#
# Author(s): Kabira K. (webworks.monallabs.in).

# MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
constructs for what tailwind calls psuedo classes
"""

from .style_tags import noop
from aenum import Enum, EnumType


def modify(*args, modifier: str = ""):
    lc_args = []
    for arg in args:
        if isinstance(arg, Enum) or isinstance(arg, EnumType):
            lc_args.append(noop / arg)
        else:
            lc_args.append(arg)
    for arg in lc_args:
        try:
            arg.modifier_chain.insert(0, modifier)
        except:
            arg.modifier_chain = [modifier]
    return lc_args


def selection(*args):
    return modify(*args, modifier="selection")


def placeholder(*args):
    return modify(*args, modifier="placeholder")


def hover(*args):
    return modify(*args, modifier="hover")


def focus(*args):
    return modify(*args, modifier="focus")


# https://tailwindcss.com/docs/hover-focus-and-other-states#pseudo-class-reference
# focus-within
# focus-visible
# active (:active)
# visited
# target
# first
# last
# only
# odd
# even
# disable
# enabled
# checked
# default
# required
# valid
#
def variant(*args, rv: str):
    """
    rv: responsive variant, sm, md, lg, xl, 2xl

    """
    return modify(*args, modifier=rv)


modifier_fn_dict = {
    "hover": hover,
    "selection": selection,
    "placeholder": placeholder,
    "focus": focus,
}
