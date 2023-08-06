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
current_module = sys.modules[__name__]

from .style_tags import noop
from . import style_values as sv
from .style_tags import outline as outlineTag, boxshadow as boxShadowTag


class _DisplayBox:
    _sv_class = sv.DisplayBox

    @property
    def b(cls):
        return noop / sv.DisplayBox.b

    @property
    def bi(cls):
        return noop / sv.DisplayBox.bi

    @property
    def i(cls):
        return noop / sv.DisplayBox.i

    @property
    def f(cls):
        return noop / sv.DisplayBox.f

    @property
    def fi(cls):
        return noop / sv.DisplayBox.fi

    @property
    def t(cls):
        return noop / sv.DisplayBox.t

    @property
    def g(cls):
        return noop / sv.DisplayBox.g


DisplayBox = _DisplayBox()


class _BoxLayout:
    _sv_class = sv.BoxLayout

    @property
    def b(cls):
        return noop / sv.BoxLayout.b

    @property
    def bi(cls):
        return noop / sv.BoxLayout.bi

    @property
    def i(cls):
        return noop / sv.BoxLayout.i

    @property
    def f(cls):
        return noop / sv.BoxLayout.f

    @property
    def fi(cls):
        return noop / sv.BoxLayout.fi

    @property
    def t(cls):
        return noop / sv.BoxLayout.t

    @property
    def g(cls):
        return noop / sv.BoxLayout.g


BoxLayout = _BoxLayout()


class _WrapAround:
    _sv_class = sv.WrapAround

    @property
    def r(cls):
        return noop / sv.WrapAround.r

    @property
    def l(cls):
        return noop / sv.WrapAround.l

    @property
    def n(cls):
        return noop / sv.WrapAround.n


WrapAround = _WrapAround()


class _ClearWrap:
    _sv_class = sv.ClearWrap

    @property
    def l(cls):
        return noop / sv.ClearWrap.l

    @property
    def r(cls):
        return noop / sv.ClearWrap.r

    @property
    def b(cls):
        return noop / sv.ClearWrap.b

    @property
    def n(cls):
        return noop / sv.ClearWrap.n


ClearWrap = _ClearWrap()


class _ObjectFit:
    _sv_class = sv.ObjectFit

    @property
    def cn(cls):
        return noop / sv.ObjectFit.cn

    @property
    def cv(cls):
        return noop / sv.ObjectFit.cv

    @property
    def f(cls):
        return noop / sv.ObjectFit.f

    @property
    def n(cls):
        return noop / sv.ObjectFit.n

    @property
    def sd(cls):
        return noop / sv.ObjectFit.sd


ObjectFit = _ObjectFit()


class _ObjectPosition:
    _sv_class = sv.ObjectPosition

    @property
    def b(cls):
        return noop / sv.ObjectPosition.b

    @property
    def c(cls):
        return noop / sv.ObjectPosition.c

    @property
    def l(cls):
        return noop / sv.ObjectPosition.l

    @property
    def lb(cls):
        return noop / sv.ObjectPosition.lb

    @property
    def lt(cls):
        return noop / sv.ObjectPosition.lt

    @property
    def r(cls):
        return noop / sv.ObjectPosition.r

    @property
    def rb(cls):
        return noop / sv.ObjectPosition.rb

    @property
    def t(cls):
        return noop / sv.ObjectPosition.t


ObjectPosition = _ObjectPosition()


class _Visibility:
    _sv_class = sv.Visibility

    @property
    def v(cls):
        return noop / sv.Visibility.v

    @property
    def nv(cls):
        return noop / sv.Visibility.nv


Visibility = _Visibility()


class _FlexLayout:
    _sv_class = sv.FlexLayout

    @property
    def row(cls):
        return noop / sv.FlexLayout.row

    @property
    def rrow(cls):
        return noop / sv.FlexLayout.rrow

    @property
    def col(cls):
        return noop / sv.FlexLayout.col

    @property
    def rcol(cls):
        return noop / sv.FlexLayout.rcol

    @property
    def wrap(cls):
        return noop / sv.FlexLayout.wrap

    @property
    def rwrap(cls):
        return noop / sv.FlexLayout.rwrap

    @property
    def nowrap(cls):
        return noop / sv.FlexLayout.nowrap

    @property
    def one(cls):
        return noop / sv.FlexLayout.one

    @property
    def auto(cls):
        return noop / sv.FlexLayout.auto

    @property
    def initial(cls):
        return noop / sv.FlexLayout.initial

    @property
    def none(cls):
        return noop / sv.FlexLayout.none

    @property
    def grow(cls):
        return noop / sv.FlexLayout.grow

    @property
    def nogrow(cls):
        return noop / sv.FlexLayout.nogrow

    @property
    def shrink(cls):
        return noop / sv.FlexLayout.shrink

    @property
    def noshrink(cls):
        return noop / sv.FlexLayout.noshrink


FlexLayout = _FlexLayout()


class _JustifyContent:
    _sv_class = sv.JustifyContent

    @property
    def start(cls):
        return noop / sv.JustifyContent.start

    @property
    def end(cls):
        return noop / sv.JustifyContent.end

    @property
    def center(cls):
        return noop / sv.JustifyContent.center

    @property
    def between(cls):
        return noop / sv.JustifyContent.between

    @property
    def evenly(cls):
        return noop / sv.JustifyContent.evenly

    @property
    def around(cls):
        return noop / sv.JustifyContent.around


JustifyContent = _JustifyContent()


class _JustifyItems:
    _sv_class = sv.JustifyItems

    @property
    def start(cls):
        return noop / sv.JustifyItems.start

    @property
    def end(cls):
        return noop / sv.JustifyItems.end

    @property
    def center(cls):
        return noop / sv.JustifyItems.center

    @property
    def stretch(cls):
        return noop / sv.JustifyItems.stretch


JustifyItems = _JustifyItems()


class _JustifySelf:
    _sv_class = sv.JustifySelf

    @property
    def auto(cls):
        return noop / sv.JustifySelf.auto

    @property
    def start(cls):
        return noop / sv.JustifySelf.start

    @property
    def end(cls):
        return noop / sv.JustifySelf.end

    @property
    def center(cls):
        return noop / sv.JustifySelf.center

    @property
    def stretch(cls):
        return noop / sv.JustifySelf.stretch


JustifySelf = _JustifySelf()


class _AlignContent:
    _sv_class = sv.AlignContent

    @property
    def start(cls):
        return noop / sv.AlignContent.start

    @property
    def end(cls):
        return noop / sv.AlignContent.end

    @property
    def center(cls):
        return noop / sv.AlignContent.center

    @property
    def between(cls):
        return noop / sv.AlignContent.between

    @property
    def evenly(cls):
        return noop / sv.AlignContent.evenly

    @property
    def around(cls):
        return noop / sv.AlignContent.around


AlignContent = _AlignContent()


class _AlignItems:
    _sv_class = sv.AlignItems

    @property
    def start(cls):
        return noop / sv.AlignItems.start

    @property
    def end(cls):
        return noop / sv.AlignItems.end

    @property
    def center(cls):
        return noop / sv.AlignItems.center

    @property
    def stretch(cls):
        return noop / sv.AlignItems.stretch

    @property
    def baseline(cls):
        return noop / sv.AlignItems.baseline


AlignItems = _AlignItems()


class _PlaceContent:
    _sv_class = sv.PlaceContent

    @property
    def start(cls):
        return noop / sv.PlaceContent.start

    @property
    def end(cls):
        return noop / sv.PlaceContent.end

    @property
    def center(cls):
        return noop / sv.PlaceContent.center

    @property
    def between(cls):
        return noop / sv.PlaceContent.between

    @property
    def evenly(cls):
        return noop / sv.PlaceContent.evenly

    @property
    def around(cls):
        return noop / sv.PlaceContent.around

    @property
    def stretch(cls):
        return noop / sv.PlaceContent.stretch


PlaceContent = _PlaceContent()


class _PlaceItems:
    _sv_class = sv.PlaceItems

    @property
    def start(cls):
        return noop / sv.PlaceItems.start

    @property
    def end(cls):
        return noop / sv.PlaceItems.end

    @property
    def center(cls):
        return noop / sv.PlaceItems.center

    @property
    def stretch(cls):
        return noop / sv.PlaceItems.stretch


PlaceItems = _PlaceItems()


class _PlaceSelf:
    _sv_class = sv.PlaceSelf

    @property
    def auto(cls):
        return noop / sv.PlaceSelf.auto

    @property
    def start(cls):
        return noop / sv.PlaceSelf.start

    @property
    def end(cls):
        return noop / sv.PlaceSelf.end

    @property
    def center(cls):
        return noop / sv.PlaceSelf.center

    @property
    def stretch(cls):
        return noop / sv.PlaceSelf.stretch


PlaceSelf = _PlaceSelf()


class _FontFamily:
    _sv_class = sv.FontFamily

    @property
    def sans(cls):
        return noop / sv.FontFamily.sans

    @property
    def serif(cls):
        return noop / sv.FontFamily.serif

    @property
    def mono(cls):
        return noop / sv.FontFamily.mono


FontFamily = _FontFamily()


class _FontSize:
    _sv_class = sv.FontSize

    @property
    def xs(cls):
        return noop / sv.FontSize.xs

    @property
    def sm(cls):
        return noop / sv.FontSize.sm

    @property
    def _(cls):
        return noop / sv.FontSize._

    @property
    def lg(cls):
        return noop / sv.FontSize.lg

    @property
    def xl(cls):
        return noop / sv.FontSize.xl

    @property
    def xl2(cls):
        return noop / sv.FontSize.xl2

    @property
    def xl3(cls):
        return noop / sv.FontSize.xl3

    @property
    def xl4(cls):
        return noop / sv.FontSize.xl4

    @property
    def xl5(cls):
        return noop / sv.FontSize.xl5

    @property
    def xl6(cls):
        return noop / sv.FontSize.xl6


FontSize = _FontSize()


class _FontWeight:
    _sv_class = sv.FontWeight

    @property
    def thin(cls):
        return noop / sv.FontWeight.thin

    @property
    def extralight(cls):
        return noop / sv.FontWeight.extralight

    @property
    def light(cls):
        return noop / sv.FontWeight.light

    @property
    def normal(cls):
        return noop / sv.FontWeight.normal

    @property
    def medium(cls):
        return noop / sv.FontWeight.medium

    @property
    def bold(cls):
        return noop / sv.FontWeight.bold

    @property
    def extrabold(cls):
        return noop / sv.FontWeight.extrabold

    @property
    def black(cls):
        return noop / sv.FontWeight.black

    @property
    def semibold(cls):
        return noop / sv.FontWeight.semibold


FontWeight = _FontWeight()


class _LetterSpace:
    _sv_class = sv.LetterSpace

    @property
    def tighter(cls):
        return noop / sv.LetterSpace.tighter

    @property
    def tight(cls):
        return noop / sv.LetterSpace.tight

    @property
    def normal(cls):
        return noop / sv.LetterSpace.normal

    @property
    def wide(cls):
        return noop / sv.LetterSpace.wide

    @property
    def wider(cls):
        return noop / sv.LetterSpace.wider

    @property
    def widest(cls):
        return noop / sv.LetterSpace.widest


LetterSpace = _LetterSpace()


class _LineHeight:
    _sv_class = sv.LineHeight

    @property
    def none(cls):
        return noop / sv.LineHeight.none

    @property
    def tight(cls):
        return noop / sv.LineHeight.tight

    @property
    def snug(cls):
        return noop / sv.LineHeight.snug

    @property
    def normal(cls):
        return noop / sv.LineHeight.normal

    @property
    def relaxed(cls):
        return noop / sv.LineHeight.relaxed

    @property
    def loose(cls):
        return noop / sv.LineHeight.loose


LineHeight = _LineHeight()


class _ListItems:
    _sv_class = sv.ListItems

    @property
    def none(cls):
        return noop / sv.ListItems.none

    @property
    def disc(cls):
        return noop / sv.ListItems.disc

    @property
    def decimal(cls):
        return noop / sv.ListItems.decimal

    @property
    def inside(cls):
        return noop / sv.ListItems.inside

    @property
    def outside(cls):
        return noop / sv.ListItems.outside


ListItems = _ListItems()


class _TextAlign:
    _sv_class = sv.TextAlign

    @property
    def left(cls):
        return noop / sv.TextAlign.left

    @property
    def center(cls):
        return noop / sv.TextAlign.center

    @property
    def right(cls):
        return noop / sv.TextAlign.right

    @property
    def justify(cls):
        return noop / sv.TextAlign.justify

    @property
    def start(cls):
        return noop / sv.TextAlign.start

    @property
    def end(cls):
        return noop / sv.TextAlign.end


TextAlign = _TextAlign()


class _TextTransform:
    _sv_class = sv.TextTransform

    @property
    def u(cls):
        return noop / sv.TextTransform.u

    @property
    def l(cls):
        return noop / sv.TextTransform.l

    @property
    def c(cls):
        return noop / sv.TextTransform.c

    @property
    def n(cls):
        return noop / sv.TextTransform.n


TextTransform = _TextTransform()


class _VerticalAlign:
    _sv_class = sv.VerticalAlign

    @property
    def top(cls):
        return noop / sv.VerticalAlign.top

    @property
    def middle(cls):
        return noop / sv.VerticalAlign.middle

    @property
    def bottom(cls):
        return noop / sv.VerticalAlign.bottom


VerticalAlign = _VerticalAlign()


class _BackgroundAttachment:
    _sv_class = sv.BackgroundAttachment

    @property
    def f(cls):
        return noop / sv.BackgroundAttachment.f

    @property
    def l(cls):
        return noop / sv.BackgroundAttachment.l

    @property
    def s(cls):
        return noop / sv.BackgroundAttachment.s


BackgroundAttachment = _BackgroundAttachment()


class _BorderRadius:
    _sv_class = sv.BorderRadius

    @property
    def sm(cls):
        return noop / sv.BorderRadius.sm

    @property
    def md(cls):
        return noop / sv.BorderRadius.md

    @property
    def lg(cls):
        return noop / sv.BorderRadius.lg

    @property
    def full(cls):
        return noop / sv.BorderRadius.full

    @property
    def none(cls):
        return noop / sv.BorderRadius.none


BorderRadius = _BorderRadius()


class _BorderStyle:
    _sv_class = sv.BorderStyle

    @property
    def solid(cls):
        return noop / sv.BorderStyle.solid

    @property
    def dashed(cls):
        return noop / sv.BorderStyle.dashed

    @property
    def dotted(cls):
        return noop / sv.BorderStyle.dotted

    @property
    def double(cls):
        return noop / sv.BorderStyle.double

    @property
    def none(cls):
        return noop / sv.BorderStyle.none

    @property
    def collapse(cls):
        return noop / sv.BorderStyle.collapse

    @property
    def separate(cls):
        return noop / sv.BorderStyle.separate


BorderStyle = _BorderStyle()


class _Outline:
    _sv_class = sv.Outline

    @classmethod
    def __truediv__(cls, valprefix):
        return outlineTag / valprefix

    @property
    def none(cls):
        return noop / sv.Outline.none

    @property
    def _(cls):
        return noop / sv.Outline._

    @property
    def dashed(cls):
        return noop / sv.Outline.dashed

    @property
    def dotted(cls):
        return noop / sv.Outline.dotted

    @property
    def double(cls):
        return noop / sv.Outline.double

    @property
    def hidden(cls):
        return noop / sv.Outline.hidden


Outline = _Outline()


class _BoxShadow:
    _sv_class = sv.BoxShadow

    @classmethod
    def __truediv__(cls, valprefix):
        return boxShadowTag / valprefix

    @property
    def sm(cls):
        return noop / sv.BoxShadow.sm

    @property
    def _(cls):
        return noop / sv.BoxShadow._

    @property
    def md(cls):
        return noop / sv.BoxShadow.md

    @property
    def lg(cls):
        return noop / sv.BoxShadow.lg

    @property
    def xl(cls):
        return noop / sv.BoxShadow.xl

    @property
    def xl2(cls):
        return noop / sv.BoxShadow.xl2

    @property
    def none(cls):
        return noop / sv.BoxShadow.none

    @property
    def inner(cls):
        return noop / sv.BoxShadow.inner


BoxShadow = _BoxShadow()


class _Table:
    _sv_class = sv.Table

    @property
    def auto(cls):
        return noop / sv.Table.auto

    @property
    def fixed(cls):
        return noop / sv.Table.fixed


Table = _Table()


class _BoxTopo:
    _sv_class = sv.BoxTopo

    @property
    def bd(cls):
        return noop / sv.BoxTopo.bd

    @property
    def container(cls):
        return noop / sv.BoxTopo.container


BoxTopo = _BoxTopo()


class _PlacementPosition:
    _sv_class = sv.PlacementPosition

    @property
    def static(cls):
        return noop / sv.PlacementPosition.static

    @property
    def fixed(cls):
        return noop / sv.PlacementPosition.fixed

    @property
    def absolute(cls):
        return noop / sv.PlacementPosition.absolute

    @property
    def relative(cls):
        return noop / sv.PlacementPosition.relative

    @property
    def sticky(cls):
        return noop / sv.PlacementPosition.sticky


PlacementPosition = _PlacementPosition()


class _BoxSizing:
    _sv_class = sv.BoxSizing

    @property
    def b(cls):
        return noop / sv.BoxSizing.b

    @property
    def c(cls):
        return noop / sv.BoxSizing.c


BoxSizing = _BoxSizing()


class _Prose:
    _sv_class = sv.Prose

    @property
    def sm(cls):
        return noop / sv.Prose.sm

    @property
    def _(cls):
        return noop / sv.Prose._

    @property
    def lg(cls):
        return noop / sv.Prose.lg

    @property
    def xl(cls):
        return noop / sv.Prose.xl

    @property
    def xl2(cls):
        return noop / sv.Prose.xl2


Prose = _Prose()


class _GridFlow:
    _sv_class = sv.GridFlow

    @property
    def row(cls):
        return noop / sv.GridFlow.row

    @property
    def col(cls):
        return noop / sv.GridFlow.col

    @property
    def rowd(cls):
        return noop / sv.GridFlow.rowd

    @property
    def cold(cls):
        return noop / sv.GridFlow.cold


GridFlow = _GridFlow()


class _GridAuto:
    _sv_class = sv.GridAuto

    @property
    def cauto(cls):
        return noop / sv.GridAuto.cauto

    @property
    def cmin(cls):
        return noop / sv.GridAuto.cmin

    @property
    def cmax(cls):
        return noop / sv.GridAuto.cmax

    @property
    def cfr(cls):
        return noop / sv.GridAuto.cfr

    @property
    def rauto(cls):
        return noop / sv.GridAuto.rauto

    @property
    def rmin(cls):
        return noop / sv.GridAuto.rmin

    @property
    def rmax(cls):
        return noop / sv.GridAuto.rmax

    @property
    def rfr(cls):
        return noop / sv.GridAuto.rfr


GridAuto = _GridAuto()



def filter(name):
    if hasattr(current_module, "_" + name):
        if isinstance(getattr(current_module, "_" + name), type):
            return True

    return False


styValueDict = dict(
    [(name, ins) for name, ins in current_module.__dict__.items() if filter(name)]
)
