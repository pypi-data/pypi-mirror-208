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


from .style_tags import bg, from_, to_, via_
from .style_values import Outline as outlineEnum, BoxShadow as boxShadowEnum

from .style_tags import outline as outlineTag, boxshadow as boxShadowTag


def gradient(from_color_idvexpr, to_color_idivexpr, via_color_idivexpr=None):
    """
    for now only considering bg gradient
    """

    return [
        bg / "gradient-to-r",
        from_ / from_color_idvexpr,
        to_ / to_color_idivexpr,
        via_ / via_color_idivexpr,
    ]


class _Outline:
    @classmethod
    def __truediv__(cls, valprefix):
        return outlineTag / valprefix

    none = outlineEnum.none
    _ = outlineEnum._
    dashed = outlineEnum.dashed
    dotted = outlineEnum.dotted
    double = outlineEnum.double
    hidden = outlineEnum.hidden


Outline = _Outline()


class _BoxShadow:
    @classmethod
    def __truediv__(cls, valprefix):
        return boxShadowTag / valprefix

    sm = boxShadowEnum.sm
    _ = boxShadowEnum._
    md = boxShadowEnum.md
    lg = boxShadowEnum.lg
    xl = boxShadowEnum.xl
    xl2 = boxShadowEnum.xl2
    none = boxShadowEnum.none
    inner = boxShadowEnum.inner


BoxShadow = _BoxShadow()
