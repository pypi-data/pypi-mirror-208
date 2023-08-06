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


"""styClause to json and vice versa
"""
from addict_tracking_changes import Dict
from .style_tags import styTagDict
from aenum import Enum
from .colors import _ColorBase
from .common import _IDivExpr, TagBase
from .modifiers import modifier_fn_dict
from .style_values_noop import styValueDict
from .dpathutils import dsearch

import functools


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(*g(x)), functions, lambda x: x)


def to_json(*args, prefix=""):
    """
    convert styClause from list of IDivExpr to json/dict
    """
    if len(args) > 0:
        if isinstance(args[0], list):
            raise ValueError("error in to_json argument passing")

    # print("=============begin tstr============")
    res = Dict()
    # keep all directives that are specified as string
    res.passthrough = []
    for arg in args:
        if isinstance(arg, Enum):
            print("R")
            res[arg.__class__.__name__]["_val"] = arg.name
            try:
                res[arg.__class__.__name__]["_modifier_chain"] = arg.modifier_chain

            except:
                pass
        if isinstance(arg, _IDivExpr):
            kv = arg.keyvaleval()
            if isinstance(kv[1], tuple):
                if isinstance(kv[1][1], tuple):
                    print("get_styReport:Warning: too many nested tuple = ", arg)
                    raise ValueError
                else:
                    if not res[kv[0]]:
                        res[kv[0]] = []

                    tt = Dict(
                        {
                            "_val": kv[1][1],
                        }
                    )
                    res[kv[0]].append(
                        Dict({kv[1][0]: tt, "_modifier_chain": arg.modifier_chain})
                    )
            else:
                if not res[kv[0]]:
                    # create list to store all utility directives for a feature.
                    # for e.g. feature='bg' utility directives= "blue-100'
                    res[kv[0]] = []
                res[kv[0]].append(
                    Dict({"_val": kv[1], "_modifier_chain": arg.modifier_chain})
                )
                # res[kv[0]]= ['_val'] = kv[1]
            # try:
            #     res[kv[0]]['_modifier_chain'] = arg.modifier_chain
            #     print ("how come")

            # except:
            #     print ("scenario 4")
            #     assert False
            #     res[kv[0]]['_modifier_chain'] = [None]
            #     pass
        if isinstance(arg, TagBase):
            kv = arg.keyvaleval()
            res[kv[0]]["_val"] = kv[1]
            try:
                res[kv[0]]["_modifier_chain"] = arg.modifier_chain
            except:
                pass
        if isinstance(arg, str):
            print("get_styReport:Warning: skipping sty attr = ", arg)
            res.passthrough.append(arg)
    return res


# ================================ end ===============================


# ============== from json styreport to tstr expression ==============


def to_clause(styreport):
    """
    builds styclause from styreport
    """

    def json_to_clause(key, val):
        """
        resolve json expression of type :'ObjectPosition': {'_val': 't'}}
        to styclause

        """

        try:
            modifier_fn = compose(
                *[modifier_fn_dict[modifier] for modifier in val._modifier_chain]
            )
        except:
            print("hitting exceptins")

            def modifier_fn(x):
                return x

            pass

        if key in styValueDict:
            return modifier_fn(getattr(styValueDict[key], val._val))
        elif isinstance(val, _IDivExpr):
            return modifier_fn(styTagDict[key].__truediv__(val))

        elif "_val" in val:
            return modifier_fn(styTagDict[key].__truediv__(val._val))

        elif "_color" in val:
            colstr = val._color._val
            cc, cv = colstr.replace("00", "").split("-")  # gray-400 --> gray, 400"
            return modifier_fn((styTagDict[key].__truediv__(f"{cc}-{cv}00"),))
        elif (
            len(list(dsearch(val, "*/_val"))) == 1
        ):  # case: pd/x/4==> key=pd val={'x': {'_val': '4'}}
            [k, v] = list(val.items())[0]
            x1 = styTagDict[k].__truediv__(v._val)
            x2 = styTagDict[key].__truediv__(x1)
            return modifier_fn(x2)
            # return styTagDict[k].__truediv__(v._val)
            # breturn styTagDict[key].__truediv__(styTagDict[k].__truediv__(v._val))
        else:
            print("unable to resolve ", key, val, len(val.items()))
            raise ValueError

    res = []
    for k, v in styreport.items():
        # print ("k ===> v ", k, v)
        if k in ["hctype", "spath"]:
            continue

        if k == "passthrough":
            if v:
                [res.append(_) for _ in v]
                # res.append(v)
        elif isinstance(v, list):
            # multiple psuedo class entries
            for pe in v:
                res.append(json_to_clause(k, pe))
        elif "_val" in v or "_color" in v or len(v.items()) == 1:
            # [res.append(_) for _ in json_to_clause(k, v)]
            res.append(json_to_clause(k, v))
        elif len(v.items()) > 1:
            for sk, sv in v.items():
                # Following is valid jsonification
                # dict_items([('sl', {'_val': '2'}), ('_modifier_chain', None)])
                # ignore sk when sv == None
                if sv is not None:
                    res.append(json_to_clause(k, json_to_clause(sk, sv)))
        else:
            print("Unable to parse ")
            raise ValueError("unable to parse sty json to sty clause")

    return res


# ================================ end ===============================
