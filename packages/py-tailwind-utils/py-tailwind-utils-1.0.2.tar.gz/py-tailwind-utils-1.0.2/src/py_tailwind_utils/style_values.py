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


import sys
from aenum import Enum

#################################################
# block	display: block;                         #
# inline-block	display: inline-block;          #
# inline	display: inline;                #
# flex	display: flex;                          #
# inline-flex	display: inline-flex;           #
# table                                         #
#################################################

###############################################################
# inline-table	display: inline-table;                        #
# table-caption	display: table-caption;                       #
# table-cell	display: table-cell;                          #
# table-column	display: table-column;                        #
# table-column-group	display: table-column-group;          #
# table-footer-group	display: table-footer-group;          #
# table-header-group	display: table-header-group;          #
# table-row-group	display: table-row-group;             #
# table-row	display: table-row;                           #
# flow-root	display: flow-root;                           #
# grid	display: grid;                                        #
# inline-grid	display: inline-grid;                         #
# contents	display: contents;                            #
# list-item	display: list-item;                           #
# hidden	display: none;                                #
###############################################################


class DisplayBox(Enum):
    b = "block"
    bi = "inline-block"
    i = "inline"
    f = "flex"
    fi = "inline-flex"
    t = "table"
    g = "grid"
    # TBD: add more docs/display
    pass


BoxLayout = DisplayBox

# docs/float


class WrapAround(Enum):
    r = "float-right"
    l = "float-left"
    n = "float-none"


class ClearWrap(Enum):
    l = "clear-left"
    r = "clear-right"
    b = "clear-both"
    n = "clear-none"


# TBD: docs/isolation


# TBD: docs/overscroll-behaviour
class ObjectFit(Enum):
    cn = "object-contain"
    cv = "object-cover"
    f = "object-fill"
    n = "object-none"
    sd = "object-scale-down"


# TODO: top, bottom permutation combination missing


class ObjectPosition(Enum):
    b = "object-bottom"
    c = "object-center"
    l = "object-left"
    lb = "object-left-bottom"
    lt = "object-left-top"
    r = "object-right"
    rb = "object-right-bottom"
    t = "object-top"


class Visibility(Enum):
    v = "visible"
    nv = "invisible"


class FlexLayout(Enum):
    row = "flex-row"
    rrow = "flex-row-reverse"
    col = "flex-col"
    rcol = "flex-col-reverse"
    wrap = "flex-wrap"
    rwrap = "flex-wrap-reverse"
    nowrap = "flex-nowrap"
    one = "flex-1"
    auto = "flex-auto"
    initial = "flex-initial"
    none = "flex-none"
    grow = "flex-grow"
    nogrow = "flex-grow-0"
    shrink = "flex-shrink"
    noshrink = "flex-shrink-0"


class JustifyContent(Enum):
    start = "justify-start"
    end = "justify-end"
    center = "justify-center"
    between = "justify-between"
    evenly = "justify-evenly"
    around = "justify-around"


class JustifyItems(Enum):
    start = "justify-items-start"
    end = "justify-items-end"
    center = "justify-items-center"
    stretch = "justify-items-stretch"


class JustifySelf(Enum):
    auto = "justify-self-auto"
    start = "justify-self-start"
    end = "justify-self-end"
    center = "justify-self-center"
    stretch = "justify-self-stretch"


class AlignContent(Enum):
    start = "content-start"
    end = "content-end"
    center = "content-center"
    between = "content-between"
    evenly = "content-evenly"
    around = "content-around"


class AlignItems(Enum):
    start = "items-start"
    end = "items-end"
    center = "items-center"
    stretch = "items-stretch"
    baseline = "items-baseline"


# TBD docs/align-self


class PlaceContent(Enum):
    start = "place-content-start"
    end = "place-content-end"
    center = "place-content-center"
    between = "place-content-between"
    evenly = "place-content-evenly"
    around = "place-content-around"
    stretch = "place-content-stretch"


class PlaceItems(Enum):
    start = "place-items-start"
    end = "place-items-end"
    center = "place-items-center"
    stretch = "place-items-stretch"


class PlaceSelf(Enum):
    auto = "place-self-auto"
    start = "place-self-start"
    end = "place-self-end"
    center = "place-self-center"
    stretch = "place-self-stretch"


class FontFamily(Enum):
    sans = "font-sans"
    serif = "font-serif"
    mono = "font-mono"
    pass


class FontSize(Enum):
    xs = "text-xs"
    sm = "text-sm"
    _ = "text-base"
    lg = "text-lg"
    xl = "text-xl"
    xl2 = "text-2xl"
    xl3 = "text-3xl"
    xl4 = "text-4xl"
    xl5 = "text-5xl"
    xl6 = "text-6xl"
    # TBD ixl
    pass


# TDB docs/font-smoothing
# TBD docs/font-style


class FontWeight(Enum):
    thin = "font-thin"
    extralight = "font-extralight"
    light = "font-light"
    normal = "font-normal"
    medium = "font-medium"
    bold = "font-bold"
    extrabold = "font-extrabold"
    black = "font-black"
    semibold = "font-semibold"

    def __call__(self, *args):
        return self.value(*args)


# TBD: docs/font-variant-numeric


class LetterSpace(Enum):
    tighter = "tracking-tighter"
    tight = "tracking-tight"
    normal = "tracking-normal"
    wide = "tracking-wide"
    wider = "tracking-wider"
    widest = "tracking-widest"


class LineHeight(Enum):
    none = "leading-none"
    tight = "leading-tight"
    snug = "leading-snug"
    normal = "leading-normal"
    relaxed = "leading-relaxed"
    loose = "leading-loose"


class ListItems(Enum):
    none = "list-none"
    disc = "list-disc"
    decimal = "list-decimal"
    inside = "list-inside"
    outside = "list-outside"


class TextAlign(Enum):
    left = "text-left"
    center = "text-center"
    right = "text-right"
    justify = "text-justify"
    start = "text-start"
    end = "text-end"
    pass


# https://tailwindcss.com/docs/text-transform
class TextTransform(Enum):
    u = "uppercase"
    l = "lowercase"
    c = "capitalize"
    n = "normal-case"


class VerticalAlign(Enum):
    top = "align-top"
    middle = "align-middle"
    bottom = "align-bottom"
    # few others left out

    pass


# TBD docs/text-decoratio
# TBD docs/text-transform
# TBD docs/text-overflow
# TBD docs/vertical-align
# TBD docs/whitespace
# TBD docs/wordbreak


class BackgroundAttachment(Enum):
    f = "bg-fixed"
    l = "bg-local"
    s = "bg-scroll"


# TBD docs/background-clip
# TBD docs/backgrond-origin
# TBD docs/backgrond-position
# TBD docs/backgrond-repeat
# TBD docs/backgrond-size
# TBD docs/backgrond-image
# TBD docs/gradient-color-stops


class BorderRadius(Enum):
    sm = "rounded-sm"
    md = "rounded-md"
    lg = "rounded-lg"
    full = "rounded-full"
    none = "rounded-none"
    pass


class BorderStyle(Enum):
    solid = "border-solid"
    dashed = "border-dashed"
    dotted = "border-dotted"
    double = "border-double"
    none = "border-none"
    collapse = "border-collapse"  # for table
    separate = "border-separate"


class Outline(Enum):
    none = "outline-none"
    _ = "outline"
    dashed = "outline-dashed"
    dotted = "outline-dotted"
    double = "outline-double"
    hidden = "outline-hidden"


class BoxShadow(Enum):
    sm = "shadow-sm"
    _ = "shadow"
    md = "shadow-md"
    lg = "shadow-lg"
    xl = "shadow-xl"
    xl2 = "shadow-2xl"
    none = "shadow-none"
    inner = "shadow-inner"
    pass


class Table(Enum):
    auto = "table-auto"
    fixed = "table-fixed"


# class Transition(Enum):
#     none="transition-none"

# TBD:   docs/transition-timing-function, transition-delay, animation, transform, transform-origin, tranform-scale, transform-rotate, translate, skew,

# TBD: appreance
# TBD: cursor,


# class Outline(Enum):
#     n = "outline-none"
#     w = "outline-white"
#     b = "outline-black"


# TBD: user-select, fill-current, stroke, stroke-width, screen-readers, typography(proces),

# here--


# Layout
class BoxTopo(Enum):
    bd = "border"
    container = "container"
    pass


class PlacementPosition(Enum):
    static = "static"
    fixed = "fixed"
    absolute = "absolute"
    relative = "relative"
    sticky = "sticky"
    pass


class BoxSizing(Enum):
    b = "box-border"
    c = "box-content"
    pass


class Prose(Enum):
    sm = "prose-sm"
    _ = "prose-base"
    lg = "prose-lg"
    xl = "prose-xl"
    xl2 = "prose-2xl"
    pass


class GridFlow(Enum):
    row = "grid-flow-row"
    col = "grid-flow-col"
    rowd = "grid-flow-row-dense"
    cold = "grid-flow-col-dense"
    pass


class GridAuto(Enum):
    cauto = "grid-cols-auto"
    cmin = "grid-cols-min"
    cmax = "grid-cols-max"
    cfr = "grid-cols-fr"
    rauto = "grid-rows-auto"
    rmin = "grid-ros-min"
    rmax = "grid-rows-max"
    rfr = "grid-rows-fr"


current_module = sys.modules[__name__]
styValueDict = dict(
    [
        (name, cls)
        for name, cls in current_module.__dict__.items()
        if isinstance(cls, type) and name != "Enum"
    ]
)
# for varName in dir():
#     try:
#         res = getattr(current_module, varName)
#         styValueDict[varName] = res

#     except:

#         pass
