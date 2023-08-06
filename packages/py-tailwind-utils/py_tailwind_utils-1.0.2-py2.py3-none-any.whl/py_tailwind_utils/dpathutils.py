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


"""wrapper over dpath.util to 
"""
import logging
import os
if os:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)


from dpath.util import (get as dpath_get,
                        new as dpath_new,
                        delete as dpath_delete,
                        search as dsearch
                        )
from addict_tracking_changes import Dict


def dget(dictobj, dpath):
    return dpath_get(dictobj, dpath)


def dnew(dictobj, dpath, value):
    if '[' in dpath and ']' in dpath:
        raise ValueError(f"cannot process array in {dpath}")

    dpath_new(dictobj, dpath, value)

# def dpop(addict, dpath):
#     assert(dpath[-1] != '/')
#     pk = dpath.split("/")
#     ppath = "/".join(pk[:-1])
#     pkey = pk[-1]
#     pnode = addict
#     if ppath != "":
#         pnode = dget(addict, ppath)
#     pnode.pop(pkey, None)

def dpop(dictobj, dpath):
    if '[' in dpath and ']' in dpath:
        raise ValueError(f"cannot process array in {dpath}")

    dpath_delete(dictobj, dpath)


def list_walker(alist, ppath="", guards=None, internal=False):
    """
    to be used in conjuction with walker; navigates the list
    part of the dict.
    todo; make guards over list part
    """
    if internal:
        yield (f"{ppath}/__arr", len(alist))
    for i, value in enumerate(alist):
        if isinstance(value, dict):
            yield from walker(value, ppath + f"/{i}", guards=guards, internal=internal)
        elif isinstance(value, list):
            yield from list_walker(value,  ppath + f"/{i}", guards=guards, internal=internal)


def walker(adict, ppath="", guards=None, internal=False):
    """
    if internal is True; __arr path will be exposed

    """
    for key, value in adict.items():
        try:
            if guards:
                if f"{ppath}/{key}" in guards:
                    logger.debug(f"stoping at guard for {key}")
                    yield (f"{ppath}/{key}", value)
                    continue  # stop at the guard
            if isinstance(value, dict):
                yield from walker(value, ppath + f"/{key}", guards=guards, internal=internal)
            elif isinstance(value, list):
                yield from list_walker(value, ppath + f"/{key}", guards=guards, internal=internal)

            else:
                yield (f"{ppath}/{key}", value)
                pass

        except Exception as e:
            print(f"in walker exception {ppath} {key} {e}")
            raise e


def stitch_from_dictiter(from_iter):
    """create/stitch a dictionary back from paths obtained from from_dictwalker after applying
    filter
    """
    res_dict = Dict()
    # arr_kpaths = {}
    for kpath, val in from_iter:
        if "__arr" in kpath:

            # TODO: not the best approach; use list constructor
            logger.debug(f"arr_create {kpath[:-6]}")
            dnew(res_dict, kpath[:-6], [Dict() for _ in range(val)])
            # arr_kpaths[kpath] = dget(res_dict, kpath)
            logger.debug(f"saw __arr in {kpath}")
        else:
            if val is not None:
                # if kpath in arr_kpaths:
                #     ppath, idx = get_path_idx(kpath)
                #     arr_kpaths[ppath].apppend(val)
                dnew(res_dict, kpath, val)
    return res_dict

# def dupdate(addict, path, value):
#     # skip if path not already present
#     print (f"dupdate: updating {path} with {value}")
#     try:
#         dpop(addict, path)

#     except Exception as e:
#         logger.debug(f"path {path} not present..skipping")
#         #raise e
#     dnew(addict, path, value)
