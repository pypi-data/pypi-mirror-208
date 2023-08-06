"""tailwind utility classes as first class python objects
"""
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


from . import styClause
from .colors import *
from .common import conc_twtags
from .common import remove_from_twtag_list
from .common import tstr
from .dpathutils import dget
from .dpathutils import dnew
from .dpathutils import dpath_delete as ddelete
from .dpathutils import dpop
from .dpathutils import dsearch
from .dpathutils import walker as dictWalker
from .modifiers import focus
from .modifiers import hover
from .modifiers import placeholder
from .modifiers import selection
from .modifiers import variant
from .style_tags import *
from .style_values_noop import AlignContent as ac
from .style_values_noop import AlignItems as ai
from .style_values_noop import BackgroundAttachment as ba
from .style_values_noop import BorderRadius as bdr
from .style_values_noop import BorderStyle as bds
from .style_values_noop import BoxShadow as shadow
from .style_values_noop import BoxSizing as boxsz
from .style_values_noop import BoxTopo as bt
from .style_values_noop import ClearWrap as wc
from .style_values_noop import DisplayBox as db
from .style_values_noop import FlexLayout as flx
from .style_values_noop import FontFamily as ff
from .style_values_noop import FontSize as fz
from .style_values_noop import FontWeight as fw
from .style_values_noop import GridAuto as ga
from .style_values_noop import GridFlow as gf
from .style_values_noop import JustifyContent as jc
from .style_values_noop import JustifyItems as ji
from .style_values_noop import JustifySelf as js
from .style_values_noop import LetterSpace as ls
from .style_values_noop import LineHeight as lh
from .style_values_noop import ListItems as li
from .style_values_noop import ObjectFit as of
from .style_values_noop import ObjectPosition as op
from .style_values_noop import Outline as outline
from .style_values_noop import PlaceContent as pc
from .style_values_noop import PlaceItems as pi
from .style_values_noop import PlacementPosition as ppos
from .style_values_noop import PlaceSelf as ps
from .style_values_noop import Prose as prose
from .style_values_noop import Table as tbl
from .style_values_noop import TextAlign as ta
from .style_values_noop import TextTransform as tt
from .style_values_noop import VerticalAlign as va
from .style_values_noop import Visibility as visibility
from .style_values_noop import WrapAround as wa
from .utils import gradient
from .valuetags import *

__version__ = "1.0.3"
