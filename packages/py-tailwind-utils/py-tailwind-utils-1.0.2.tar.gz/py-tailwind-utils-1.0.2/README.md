# [py-tailwind-utils](https://github.com/Monallabs-org/py-tailwind-utils)
[![Python versions](https://img.shields.io/badge/Python-3.11-green)](https://pypi.python.org/pypi/py-tailwind-utils)
[![Tests Status](https://github.com/ofjustpy/py-tailwind-utils/blob/main/badge_tests.svg)](https://github.com/ofjustpy/py-tailwind-utils/actions)
[![Coverage Status](https://github.com/ofjustpy/py-tailwind-utils/blob/main/badge_coverage.svg)](https://github.com/ofjustpy/py-tailwind-utils/actions)
[![Flake8 Status](https://github.com/ofjustpy/py-tailwind-utils/blob/main/badge_flake8.svg)](https://github.com/ofjustpy/py-tailwind-utils/actions)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://ofjustpy.github.io/py-tailwind-utils/)
[![PyPI](https://img.shields.io/pypi/v/py-tailwind-utils.svg)](https://pypi.python.org/pypi/py-tailwind-utils)
[![Downloads](https://pepy.tech/badge/py-tailwind-utils)](https://pepy.tech/project/py-tailwind-utils)
[![Downloads per week](https://pepy.tech/badge/py-tailwind-utils/week)](https://pepy.tech/project/py-tailwind-utils)
[![GitHub stars](https://img.shields.io/github/stars/ofjustpy/py-tailwind-utils.svg)](https://github.com/ofjustpy/py-tailwind-utils/stargazers)

A library that makes working with Tailwind CSS in python easier. It provides
set of operators, functions, and python native objects that make it easier 
to express and manipulate tailwind directives. 

Instead of styling a component of with a long string such "bg-pink-400 ring-offset-red-200 justify-content-start text-black-800", using
this library you would instead write the same as first class python statement:
```python
tstr(bg/pink/4, ring/offset/red/2, jc.start, fc/black/8)
```
This has several advantages:  
- makes manipulation of styles such as   
  -- passing style directives to functions,   
  -- substitution of style through variable assignment a lot easier.
- makes it feasible to do bookkeeping and analyis of style used across various components of an webpage  
- is basis for theme manipulation, i.e., bulk modify styles of several components using a single command.  


A word of caution: 
This library does pollute the namespace of your python file/module, so be careful if using "from py_tailwind_utils  import *". 
Also, not all construct of tailwind is available here. 



## Usage

### Tailwind constructs as python objects
To begin with the library exports name that reflect various tailwind constructs. For, e.g. `bg`
reflects tailwind utility class `bg`, `bd` reflects `border` and so on. See table for 
mapping between python constructs and tailwind constructs. 


### Tailwind expression builder
The above python-tailwind constructs support division operator using which one can create tailwind styling expression 
such as "bg-green-100", "ring-offset-red-200", etc. In py-tailwind-utils, these are expressed
as first class python objects as `bg/green/1` and `ring/offset/red/2`. 

### Tailwind utility as python enums
The library provides enum classes that encapsulate options for a tailwind utility. 
For e.g. for various options for justify content, the library provides enum class
`JustifyContent` (or `jc`) as follows:
```
class JustifyContent(Enum):
    start = "justify-start"
    end = "justify-end"
    center = "justify-center"
    between = "justify-between"
    evenly = "justify-evenly"
    around = "justify-around"
```
The helps group directives or identify duplicates in a style definition. 

### Tailwind modifier functions 
modifiers are expressed using functions over tailwind expression. 
For example, 
```
hover(jc.end, bg/green/1, fc/blue/8)
```

```
*hover(*focus(bg/green/400), *focus(*placeholder(noop/fw.bold), fc/pink/100))
```

### Convert python style expression to tailwind class expression
The `tstr` function converts python tailwind style expression to 
string value containing tailwind directives. 
In the example,
```
from py_tailwind_utils import tstr
tstr(bg/pink/4, ring/offset/red/2, jc.start, fc/pink/8)
```
`tstr` will convert to proper tailwind definition:
```
bg-pink-400 ring-offset-red-200 justify-start text-pink-800
```
### Append/merge tailwind directive to an existing style list
Provides `conc_twtags` function to add/merge/append new directive  to an exisiting 
list of styles. 
For e.g.  if 
```python 
mytags = [
        bg / green / 1,
        fc / blue / 1,
        flx.row,
    ]
```
is an exisiting set of styles, and if we add `bg/blue/1` using 
`conc_twtags`, then it  will perform
a smart merge, i.e., it will override the exisiting directive
that belong to the same utility class. 
So, 
```python
classes  = tstr(conc_twtags(*mytags, bg/blue/1))
```
will result in:
```
bg-blue-100 text-blue-100 flex-row
```

This feature of `py-tailwind-tags` comes in very useful for theme customization. 

### Remove a tailwind directive
Use `remove_from_twtag_list` to remove a tailwind directive from an existing list. 
An example:
```python 
mytags = [
        bg / green / 1,
        fc / blue / 1,
        jc.start, 
        flx.row,
    ]
 remove_from_twtag_list(mytags, jc.start)
```
Note: will throw ValueError if the request removeal object is not present in the list.
    

### Store tailwind styles as Json 
All the  styles applied to a component can be exported out as json, organized by utility
 class. For example, to print out   json use command:
 
```
res = tt.styClause.to_json(
    *hover(*focus(bg/green/400), *focus(*placeholder(noop/fw.bold), fc/pink/100)))
   
```
which will output:
The `res` out:
```json
{
    "passthrough": [],
    "bg": {
        "_val": "green-400",
        "_modifier_chain": ["hover", "focus"]
    },
    "FontWeight": {
        "_val": "bold",
        "_modifier_chain": ["hover", "focus", "placeholder"]
    },
    "fc": {
        "_val": "pink-100",
        "_modifier_chain": ["hover", "focus"]
    }
}
```

### Load json back as tailwind style 
Finally, once can read back the json, to convert the original tailwind style statement:
```
claus = tt.styClause.to_clause(res)
print(tstr(*claus))
```

Which outputs the original tailwind expression
```
hover:focus:bg-green-400 hover:focus:placeholder:font-bold hover:focus:text-pink-100
```

### Not supported features
#### Background opacity modifiers are not yet supported
So, this expression will fail 


## All supported tailwind constructs in python as keywords or Enum classes

![All supported tailwind constructs in python as keywords or Enum classes](/utils/tailwind_constructs_for_ofjustpy.png?raw=true "Optional Title")

## Reference

### Style Tags
<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">python keyword</th>
<th scope="col" class="org-left">tailwind construct</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">bd</td>
<td class="org-left">border</td>
</tr>


<tr>
<td class="org-left">from_</td>
<td class="org-left">from</td>
</tr>


<tr>
<td class="org-left">to_</td>
<td class="org-left">to</td>
</tr>


<tr>
<td class="org-left">via_</td>
<td class="org-left">to</td>
</tr>


<tr>
<td class="org-left">cc</td>
<td class="org-left">None</td>
</tr>


<tr>
<td class="org-left">container</td>
<td class="org-left">container</td>
</tr>


<tr>
<td class="org-left">inherit</td>
<td class="org-left">inherit</td>
</tr>


<tr>
<td class="org-left">current</td>
<td class="org-left">current</td>
</tr>


<tr>
<td class="org-left">transparent</td>
<td class="org-left">transparent</td>
</tr>


<tr>
<td class="org-left">first</td>
<td class="org-left">first</td>
</tr>


<tr>
<td class="org-left">full</td>
<td class="org-left">full</td>
</tr>


<tr>
<td class="org-left">screen</td>
<td class="org-left">screen</td>
</tr>


<tr>
<td class="org-left">hidden</td>
<td class="org-left">hidden</td>
</tr>


<tr>
<td class="org-left">last</td>
<td class="org-left">last</td>
</tr>


<tr>
<td class="org-left">none</td>
<td class="org-left">none</td>
</tr>


<tr>
<td class="org-left">scroll</td>
<td class="org-left">scroll</td>
</tr>


<tr>
<td class="org-left">span</td>
<td class="org-left">span</td>
</tr>


<tr>
<td class="org-left">text</td>
<td class="org-left">text</td>
</tr>


<tr>
<td class="org-left">visible</td>
<td class="org-left">visible</td>
</tr>


<tr>
<td class="org-left">auto</td>
<td class="org-left">auto</td>
</tr>


<tr>
<td class="org-left">group</td>
<td class="org-left">group</td>
</tr>


<tr>
<td class="org-left">double</td>
<td class="org-left">double</td>
</tr>


<tr>
<td class="org-left">clip</td>
<td class="org-left">clip</td>
</tr>


<tr>
<td class="org-left">invisible</td>
<td class="org-left">invisible</td>
</tr>


<tr>
<td class="org-left">absolute</td>
<td class="org-left">absolute</td>
</tr>


<tr>
<td class="org-left">grow</td>
<td class="org-left">grow</td>
</tr>


<tr>
<td class="org-left">bg</td>
<td class="org-left">bg</td>
</tr>


<tr>
<td class="org-left">x</td>
<td class="org-left">x</td>
</tr>


<tr>
<td class="org-left">y</td>
<td class="org-left">y</td>
</tr>


<tr>
<td class="org-left">duration</td>
<td class="org-left">duration</td>
</tr>


<tr>
<td class="org-left">inset</td>
<td class="org-left">inset</td>
</tr>


<tr>
<td class="org-left">max</td>
<td class="org-left">max</td>
</tr>


<tr>
<td class="org-left">min</td>
<td class="org-left">min</td>
</tr>


<tr>
<td class="org-left">offset</td>
<td class="org-left">offset</td>
</tr>


<tr>
<td class="org-left">opacity</td>
<td class="org-left">opacity</td>
</tr>


<tr>
<td class="org-left">order</td>
<td class="org-left">order</td>
</tr>


<tr>
<td class="org-left">ring</td>
<td class="org-left">ring</td>
</tr>


<tr>
<td class="org-left">row</td>
<td class="org-left">row</td>
</tr>


<tr>
<td class="org-left">rows</td>
<td class="org-left">rows</td>
</tr>


<tr>
<td class="org-left">col</td>
<td class="org-left">col</td>
</tr>


<tr>
<td class="org-left">cols</td>
<td class="org-left">cols</td>
</tr>


<tr>
<td class="org-left">space</td>
<td class="org-left">space</td>
</tr>


<tr>
<td class="org-left">stroke</td>
<td class="org-left">stroke</td>
</tr>


<tr>
<td class="org-left">gap</td>
<td class="org-left">gap</td>
</tr>


<tr>
<td class="org-left">end</td>
<td class="org-left">end</td>
</tr>


<tr>
<td class="org-left">fc</td>
<td class="org-left">text</td>
</tr>


<tr>
<td class="org-left">G</td>
<td class="org-left">grid</td>
</tr>


<tr>
<td class="org-left">H</td>
<td class="org-left">h</td>
</tr>


<tr>
<td class="org-left">lh</td>
<td class="org-left">leading</td>
</tr>


<tr>
<td class="org-left">mr</td>
<td class="org-left">m</td>
</tr>


<tr>
<td class="org-left">ovf</td>
<td class="org-left">overflow</td>
</tr>


<tr>
<td class="org-left">pd</td>
<td class="org-left">p</td>
</tr>


<tr>
<td class="org-left">ph</td>
<td class="org-left">placeholder</td>
</tr>


<tr>
<td class="org-left">resize</td>
<td class="org-left">resize</td>
</tr>


<tr>
<td class="org-left">sb</td>
<td class="org-left">b</td>
</tr>


<tr>
<td class="org-left">sl</td>
<td class="org-left">l</td>
</tr>


<tr>
<td class="org-left">sr</td>
<td class="org-left">r</td>
</tr>


<tr>
<td class="org-left">st</td>
<td class="org-left">t</td>
</tr>


<tr>
<td class="org-left">top</td>
<td class="org-left">top</td>
</tr>


<tr>
<td class="org-left">right</td>
<td class="org-left">right</td>
</tr>


<tr>
<td class="org-left">bottom</td>
<td class="org-left">bottom</td>
</tr>


<tr>
<td class="org-left">left</td>
<td class="org-left">left</td>
</tr>


<tr>
<td class="org-left">start</td>
<td class="org-left">start</td>
</tr>


<tr>
<td class="org-left">W</td>
<td class="org-left">w</td>
</tr>


<tr>
<td class="org-left">zo</td>
<td class="org-left">z</td>
</tr>


<tr>
<td class="org-left">noop</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">outline</td>
<td class="org-left">outline</td>
</tr>


<tr>
<td class="org-left">shadow</td>
<td class="org-left">shadow</td>
</tr>
</tbody>
</table>




### Style values
<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Tailwind Utility Class</th>
<th scope="col" class="org-left">Python enum class</th>
<th scope="col" class="org-left">python attr names</th>
<th scope="col" class="org-left">tailwind utility</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">DisplayBox</td>
<td class="org-left">db</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">b</td>
<td class="org-left">block</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">bi</td>
<td class="org-left">inline-block</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">i</td>
<td class="org-left">inline</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">f</td>
<td class="org-left">flex</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">fi</td>
<td class="org-left">inline-flex</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">t</td>
<td class="org-left">table</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">g</td>
<td class="org-left">grid</td>
</tr>


<tr>
<td class="org-left">BoxLayout</td>
<td class="org-left">db</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">b</td>
<td class="org-left">block</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">bi</td>
<td class="org-left">inline-block</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">i</td>
<td class="org-left">inline</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">f</td>
<td class="org-left">flex</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">fi</td>
<td class="org-left">inline-flex</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">t</td>
<td class="org-left">table</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">g</td>
<td class="org-left">grid</td>
</tr>


<tr>
<td class="org-left">WrapAround</td>
<td class="org-left">wa</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">r</td>
<td class="org-left">float-right</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">l</td>
<td class="org-left">float-left</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">n</td>
<td class="org-left">float-none</td>
</tr>


<tr>
<td class="org-left">ClearWrap</td>
<td class="org-left">wc</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">l</td>
<td class="org-left">clear-left</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">r</td>
<td class="org-left">clear-right</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">b</td>
<td class="org-left">clear-both</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">n</td>
<td class="org-left">clear-none</td>
</tr>


<tr>
<td class="org-left">ObjectFit</td>
<td class="org-left">of</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">cn</td>
<td class="org-left">object-contain</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">cv</td>
<td class="org-left">object-cover</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">f</td>
<td class="org-left">object-fill</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">n</td>
<td class="org-left">object-none</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">sd</td>
<td class="org-left">object-scale-down</td>
</tr>


<tr>
<td class="org-left">ObjectPosition</td>
<td class="org-left">op</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">b</td>
<td class="org-left">object-bottom</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">c</td>
<td class="org-left">object-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">l</td>
<td class="org-left">object-left</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">lb</td>
<td class="org-left">object-left-bottom</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">lt</td>
<td class="org-left">object-left-top</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">r</td>
<td class="org-left">object-right</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rb</td>
<td class="org-left">object-right-bottom</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">t</td>
<td class="org-left">object-top</td>
</tr>


<tr>
<td class="org-left">Visibility</td>
<td class="org-left">visibility</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">v</td>
<td class="org-left">visible</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">nv</td>
<td class="org-left">invisible</td>
</tr>


<tr>
<td class="org-left">FlexLayout</td>
<td class="org-left">flx</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">row</td>
<td class="org-left">flex-row</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rrow</td>
<td class="org-left">flex-row-reverse</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">col</td>
<td class="org-left">flex-col</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rcol</td>
<td class="org-left">flex-col-reverse</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">wrap</td>
<td class="org-left">flex-wrap</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rwrap</td>
<td class="org-left">flex-wrap-reverse</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">nowrap</td>
<td class="org-left">flex-nowrap</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">one</td>
<td class="org-left">flex-1</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">auto</td>
<td class="org-left">flex-auto</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">initial</td>
<td class="org-left">flex-initial</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">none</td>
<td class="org-left">flex-none</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">grow</td>
<td class="org-left">flex-grow</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">nogrow</td>
<td class="org-left">flex-grow-0</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">shrink</td>
<td class="org-left">flex-shrink</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">noshrink</td>
<td class="org-left">flex-shrink-0</td>
</tr>


<tr>
<td class="org-left">JustifyContent</td>
<td class="org-left">jc</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">justify-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">justify-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">justify-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">between</td>
<td class="org-left">justify-between</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">evenly</td>
<td class="org-left">justify-evenly</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">around</td>
<td class="org-left">justify-around</td>
</tr>


<tr>
<td class="org-left">JustifyItems</td>
<td class="org-left">ji</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">justify-items-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">justify-items-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">justify-items-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">stretch</td>
<td class="org-left">justify-items-stretch</td>
</tr>


<tr>
<td class="org-left">JustifySelf</td>
<td class="org-left">js</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">auto</td>
<td class="org-left">justify-self-auto</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">justify-self-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">justify-self-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">justify-self-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">stretch</td>
<td class="org-left">justify-self-stretch</td>
</tr>


<tr>
<td class="org-left">AlignContent</td>
<td class="org-left">ac</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">content-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">content-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">content-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">between</td>
<td class="org-left">content-between</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">evenly</td>
<td class="org-left">content-evenly</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">around</td>
<td class="org-left">content-around</td>
</tr>


<tr>
<td class="org-left">AlignItems</td>
<td class="org-left">ai</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">items-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">items-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">items-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">stretch</td>
<td class="org-left">items-stretch</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">baseline</td>
<td class="org-left">items-baseline</td>
</tr>


<tr>
<td class="org-left">PlaceContent</td>
<td class="org-left">pc</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">place-content-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">place-content-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">place-content-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">between</td>
<td class="org-left">place-content-between</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">evenly</td>
<td class="org-left">place-content-evenly</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">around</td>
<td class="org-left">place-content-around</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">stretch</td>
<td class="org-left">place-content-stretch</td>
</tr>


<tr>
<td class="org-left">PlaceItems</td>
<td class="org-left">pi</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">place-items-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">place-items-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">place-items-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">stretch</td>
<td class="org-left">place-items-stretch</td>
</tr>


<tr>
<td class="org-left">PlaceSelf</td>
<td class="org-left">ps</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">auto</td>
<td class="org-left">place-self-auto</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">place-self-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">place-self-end</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">place-self-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">stretch</td>
<td class="org-left">place-self-stretch</td>
</tr>


<tr>
<td class="org-left">FontFamily</td>
<td class="org-left">ff</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">sans</td>
<td class="org-left">font-sans</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">serif</td>
<td class="org-left">font-serif</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">mono</td>
<td class="org-left">font-mono</td>
</tr>


<tr>
<td class="org-left">FontSize</td>
<td class="org-left">fz</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xs</td>
<td class="org-left">text-xs</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">sm</td>
<td class="org-left">text-sm</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">_</td>
<td class="org-left">text-base</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">lg</td>
<td class="org-left">text-lg</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl</td>
<td class="org-left">text-xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl2</td>
<td class="org-left">text-2xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl3</td>
<td class="org-left">text-3xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl4</td>
<td class="org-left">text-4xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl5</td>
<td class="org-left">text-5xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl6</td>
<td class="org-left">text-6xl</td>
</tr>


<tr>
<td class="org-left">FontWeight</td>
<td class="org-left">fw</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">thin</td>
<td class="org-left">font-thin</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">extralight</td>
<td class="org-left">font-extralight</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">light</td>
<td class="org-left">font-light</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">normal</td>
<td class="org-left">font-normal</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">medium</td>
<td class="org-left">font-medium</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">bold</td>
<td class="org-left">font-bold</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">extrabold</td>
<td class="org-left">font-extrabold</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">black</td>
<td class="org-left">font-black</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">semibold</td>
<td class="org-left">font-semibold</td>
</tr>


<tr>
<td class="org-left">LetterSpace</td>
<td class="org-left">ls</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">tighter</td>
<td class="org-left">tracking-tighter</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">tight</td>
<td class="org-left">tracking-tight</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">normal</td>
<td class="org-left">tracking-normal</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">wide</td>
<td class="org-left">tracking-wide</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">wider</td>
<td class="org-left">tracking-wider</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">widest</td>
<td class="org-left">tracking-widest</td>
</tr>


<tr>
<td class="org-left">LineHeight</td>
<td class="org-left">lh</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">none</td>
<td class="org-left">leading-none</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">tight</td>
<td class="org-left">leading-tight</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">snug</td>
<td class="org-left">leading-snug</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">normal</td>
<td class="org-left">leading-normal</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">relaxed</td>
<td class="org-left">leading-relaxed</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">loose</td>
<td class="org-left">leading-loose</td>
</tr>


<tr>
<td class="org-left">ListItems</td>
<td class="org-left">li</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">none</td>
<td class="org-left">list-none</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">disc</td>
<td class="org-left">list-disc</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">decimal</td>
<td class="org-left">list-decimal</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">inside</td>
<td class="org-left">list-inside</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">outside</td>
<td class="org-left">list-outside</td>
</tr>


<tr>
<td class="org-left">TextAlign</td>
<td class="org-left">ta</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">left</td>
<td class="org-left">text-left</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">center</td>
<td class="org-left">text-center</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">right</td>
<td class="org-left">text-right</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">justify</td>
<td class="org-left">text-justify</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">start</td>
<td class="org-left">text-start</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">end</td>
<td class="org-left">text-end</td>
</tr>


<tr>
<td class="org-left">TextTransform</td>
<td class="org-left">tt</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">u</td>
<td class="org-left">uppercase</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">l</td>
<td class="org-left">lowercase</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">c</td>
<td class="org-left">capitalize</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">n</td>
<td class="org-left">normal-case</td>
</tr>


<tr>
<td class="org-left">VerticalAlign</td>
<td class="org-left">va</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">top</td>
<td class="org-left">align-top</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">middle</td>
<td class="org-left">align-middle</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">bottom</td>
<td class="org-left">align-bottom</td>
</tr>


<tr>
<td class="org-left">BackgroundAttachment</td>
<td class="org-left">ba</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">f</td>
<td class="org-left">bg-fixed</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">l</td>
<td class="org-left">bg-local</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">s</td>
<td class="org-left">bg-scroll</td>
</tr>


<tr>
<td class="org-left">BorderRadius</td>
<td class="org-left">bdr</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">sm</td>
<td class="org-left">rounded-sm</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">md</td>
<td class="org-left">rounded-md</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">lg</td>
<td class="org-left">rounded-lg</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">full</td>
<td class="org-left">rounded-full</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">none</td>
<td class="org-left">rounded-none</td>
</tr>


<tr>
<td class="org-left">BorderStyle</td>
<td class="org-left">bds</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">solid</td>
<td class="org-left">border-solid</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">dashed</td>
<td class="org-left">border-dashed</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">dotted</td>
<td class="org-left">border-dotted</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">double</td>
<td class="org-left">border-double</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">none</td>
<td class="org-left">border-none</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">collapse</td>
<td class="org-left">border-collapse</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">separate</td>
<td class="org-left">border-separate</td>
</tr>


<tr>
<td class="org-left">Outline</td>
<td class="org-left">outline</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">none</td>
<td class="org-left">outline-none</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">_</td>
<td class="org-left">outline</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">dashed</td>
<td class="org-left">outline-dashed</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">dotted</td>
<td class="org-left">outline-dotted</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">double</td>
<td class="org-left">outline-double</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">hidden</td>
<td class="org-left">outline-hidden</td>
</tr>


<tr>
<td class="org-left">BoxShadow</td>
<td class="org-left">shadow</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">sm</td>
<td class="org-left">shadow-sm</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">_</td>
<td class="org-left">shadow</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">md</td>
<td class="org-left">shadow-md</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">lg</td>
<td class="org-left">shadow-lg</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl</td>
<td class="org-left">shadow-xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl2</td>
<td class="org-left">shadow-2xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">none</td>
<td class="org-left">shadow-none</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">inner</td>
<td class="org-left">shadow-inner</td>
</tr>


<tr>
<td class="org-left">Table</td>
<td class="org-left">tbl</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">auto</td>
<td class="org-left">table-auto</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">fixed</td>
<td class="org-left">table-fixed</td>
</tr>


<tr>
<td class="org-left">BoxTopo</td>
<td class="org-left">bt</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">bd</td>
<td class="org-left">border</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">container</td>
<td class="org-left">container</td>
</tr>


<tr>
<td class="org-left">PlacementPosition</td>
<td class="org-left">ppos</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">static</td>
<td class="org-left">static</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">fixed</td>
<td class="org-left">fixed</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">absolute</td>
<td class="org-left">absolute</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">relative</td>
<td class="org-left">relative</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">sticky</td>
<td class="org-left">sticky</td>
</tr>


<tr>
<td class="org-left">BoxSizing</td>
<td class="org-left">boxsz</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">b</td>
<td class="org-left">box-border</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">c</td>
<td class="org-left">box-content</td>
</tr>


<tr>
<td class="org-left">Prose</td>
<td class="org-left">prse</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">sm</td>
<td class="org-left">prose-sm</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">_</td>
<td class="org-left">prose-base</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">lg</td>
<td class="org-left">prose-lg</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl</td>
<td class="org-left">prose-xl</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">xl2</td>
<td class="org-left">prose-2xl</td>
</tr>


<tr>
<td class="org-left">GridFlow</td>
<td class="org-left">gf</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">row</td>
<td class="org-left">grid-flow-row</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">col</td>
<td class="org-left">grid-flow-col</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rowd</td>
<td class="org-left">grid-flow-row-dense</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">cold</td>
<td class="org-left">grid-flow-col-dense</td>
</tr>


<tr>
<td class="org-left">GridAuto</td>
<td class="org-left">ga</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">cauto</td>
<td class="org-left">grid-cols-auto</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">cmin</td>
<td class="org-left">grid-cols-min</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">cmax</td>
<td class="org-left">grid-cols-max</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">cfr</td>
<td class="org-left">grid-cols-fr</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rauto</td>
<td class="org-left">grid-rows-auto</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rmin</td>
<td class="org-left">grid-ros-min</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rmax</td>
<td class="org-left">grid-rows-max</td>
</tr>


<tr>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">rfr</td>
<td class="org-left">grid-rows-fr</td>
</tr>
</tbody>
</table>


### EndNotes
- Docs (in readthedocs format): https://github.com/Monallabs-org/py-tailwind-utils  

- Developed By: webworks.monallabs.in

