`py-tailwind-utils <https://github.com/Monallabs-org/py-tailwind-utils>`__
==========================================================================

A library that makes working with Tailwind CSS in python easier. It
provides set of operators, functions, and python native objects that
make it easier to express and manipulate tailwind directives.

Instead of styling a component of with a long string such “bg-pink-400
ring-offset-red-200 justify-content-start text-black-800”, using this
library you would instead write the same as first class python
statement:

.. code:: python

   tstr(bg/pink/4, ring/offset/red/2, jc.start, fc/black/8)

| This has several advantages:
| - makes manipulation of styles such as
| – passing style directives to functions,
| – substitution of style through variable assignment a lot easier. -
  makes it feasible to do bookkeeping and analyis of style used across
  various components of an webpage
| - is basis for theme manipulation, i.e., bulk modify styles of several
  components using a single command.

A word of caution: This library does pollute the namespace of your
python file/module, so be careful if using “from py_tailwind_utils
import \*“. Also, not all construct of tailwind is available here.

Usage
-----

Tailwind constructs as python objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To begin with the library exports name that reflect various tailwind
constructs. For, e.g. ``bg`` reflects tailwind utility class ``bg``,
``bd`` reflects ``border`` and so on. See table for mapping between
python constructs and tailwind constructs.

Tailwind expression builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The above python-tailwind constructs support division operator using
which one can create tailwind styling expression such as “bg-green-100”,
“ring-offset-red-200”, etc. In py-tailwind-utils, these are expressed as
first class python objects as ``bg/green/1`` and ``ring/offset/red/2``.

Tailwind utility as python enums
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library provides enum classes that encapsulate options for a
tailwind utility. For e.g. for various options for justify content, the
library provides enum class ``JustifyContent`` (or ``jc``) as follows:

::

   class JustifyContent(Enum):
       start = "justify-start"
       end = "justify-end"
       center = "justify-center"
       between = "justify-between"
       evenly = "justify-evenly"
       around = "justify-around"

The helps group directives or identify duplicates in a style definition.

Tailwind modifier functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

modifiers are expressed using functions over tailwind expression. For
example,

::

   hover(jc.end, bg/green/1, fc/blue/8)

::

   *hover(*focus(bg/green/400), *focus(*placeholder(noop/fw.bold), fc/pink/100))

Convert python style expression to tailwind class expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``tstr`` function converts python tailwind style expression to
string value containing tailwind directives. In the example,

::

   from py_tailwind_utils import tstr
   tstr(bg/pink/4, ring/offset/red/2, jc.start, fc/pink/8)

``tstr`` will convert to proper tailwind definition:

::

   bg-pink-400 ring-offset-red-200 justify-start text-pink-800

Append/merge tailwind directive to an existing style list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides ``conc_twtags`` function to add/merge/append new directive to
an exisiting list of styles. For e.g. if

.. code:: python

   mytags = [
           bg / green / 1,
           fc / blue / 1,
           flx.row,
       ]

is an exisiting set of styles, and if we add ``bg/blue/1`` using
``conc_twtags``, then it will perform a smart merge, i.e., it will
override the exisiting directive that belong to the same utility class.
So,

.. code:: python

   classes  = tstr(conc_twtags(*mytags, bg/blue/1))

will result in:

::

   bg-blue-100 text-blue-100 flex-row

This feature of ``py-tailwind-tags`` comes in very useful for theme
customization.

Remove a tailwind directive
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``remove_from_twtag_list`` to remove a tailwind directive from an
existing list. An example:

.. code:: python

   mytags = [
           bg / green / 1,
           fc / blue / 1,
           jc.start, 
           flx.row,
       ]
    remove_from_twtag_list(mytags, jc.start)

Note: will throw ValueError if the request removeal object is not
present in the list.

Store tailwind styles as Json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the styles applied to a component can be exported out as json,
organized by utility class. For example, to print out json use command:

::

   res = tt.styClause.to_json(
       *hover(*focus(bg/green/400), *focus(*placeholder(noop/fw.bold), fc/pink/100)))
      

which will output: The ``res`` out:

.. code:: json

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

Load json back as tailwind style
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, once can read back the json, to convert the original tailwind
style statement:

::

   claus = tt.styClause.to_clause(res)
   print(tstr(*claus))

Which outputs the original tailwind expression

::

   hover:focus:bg-green-400 hover:focus:placeholder:font-bold hover:focus:text-pink-100

All supported tailwind constructs in python as keywords or Enum classes
-----------------------------------------------------------------------

.. figure:: /utils/tailwind_constructs_for_ofjustpy.png?raw=true
   :alt: Optional Title

   All supported tailwind constructs in python as keywords or Enum
   classes

Reference
---------

Style Tags
~~~~~~~~~~

.. raw:: html

   <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">

.. raw:: html

   <colgroup>

.. raw:: html

   <col  class="org-left" />

.. raw:: html

   <col  class="org-left" />

.. raw:: html

   </colgroup>

.. raw:: html

   <thead>

.. raw:: html

   <tr>

.. raw:: html

   <th scope="col" class="org-left">

python keyword

.. raw:: html

   </th>

.. raw:: html

   <th scope="col" class="org-left">

tailwind construct

.. raw:: html

   </th>

.. raw:: html

   </tr>

.. raw:: html

   </thead>

.. raw:: html

   <tbody>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

bd

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

from\_

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

from

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

to\_

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

to

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

via\_

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

to

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

cc

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

None

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

container

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

container

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

inherit

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inherit

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

current

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

current

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

transparent

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

transparent

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

first

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

first

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

full

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

full

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

screen

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

screen

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

hidden

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

hidden

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

last

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

last

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

scroll

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

scroll

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

span

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

span

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

text

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

visible

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

visible

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

auto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

auto

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

group

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

group

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

double

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

double

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

clip

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

clip

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

invisible

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

invisible

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

absolute

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

absolute

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

grow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grow

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

bg

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bg

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

x

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

x

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

y

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

y

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

duration

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

duration

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

inset

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inset

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

max

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

max

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

min

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

min

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

offset

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

offset

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

opacity

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

opacity

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

order

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

order

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

ring

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ring

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

row

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

row

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

rows

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rows

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

col

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

col

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

cols

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cols

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

space

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

space

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

stroke

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

stroke

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

gap

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

gap

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

fc

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

G

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

H

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

h

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

lh

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

leading

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

mr

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

m

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

ovf

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

overflow

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

pd

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

p

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

ph

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

placeholder

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

resize

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

resize

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

sb

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

b

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

sl

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

l

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

sr

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

r

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

st

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

t

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

top

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

top

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

right

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

right

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

bottom

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bottom

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

left

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

left

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

W

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

w

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

zo

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

z

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

noop

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

outline

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

shadow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

Style values
~~~~~~~~~~~~

.. raw:: html

   <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">

.. raw:: html

   <colgroup>

.. raw:: html

   <col  class="org-left" />

.. raw:: html

   <col  class="org-left" />

.. raw:: html

   <col  class="org-left" />

.. raw:: html

   <col  class="org-left" />

.. raw:: html

   </colgroup>

.. raw:: html

   <thead>

.. raw:: html

   <tr>

.. raw:: html

   <th scope="col" class="org-left">

Tailwind Utility Class

.. raw:: html

   </th>

.. raw:: html

   <th scope="col" class="org-left">

Python enum class

.. raw:: html

   </th>

.. raw:: html

   <th scope="col" class="org-left">

python attr names

.. raw:: html

   </th>

.. raw:: html

   <th scope="col" class="org-left">

tailwind utility

.. raw:: html

   </th>

.. raw:: html

   </tr>

.. raw:: html

   </thead>

.. raw:: html

   <tbody>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

DisplayBox

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

db

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

b

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

block

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bi

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inline-block

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

i

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inline

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

f

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

fi

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inline-flex

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

t

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

table

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

g

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

BoxLayout

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

db

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

b

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

block

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bi

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inline-block

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

i

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inline

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

f

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

fi

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inline-flex

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

t

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

table

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

g

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

WrapAround

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

wa

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

r

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

float-right

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

l

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

float-left

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

n

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

float-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

ClearWrap

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

wc

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

l

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

clear-left

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

r

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

clear-right

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

b

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

clear-both

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

n

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

clear-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

ObjectFit

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

of

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cn

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-contain

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cv

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-cover

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

f

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-fill

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

n

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sd

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-scale-down

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

ObjectPosition

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

op

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

b

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-bottom

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

c

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

l

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-left

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lb

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-left-bottom

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lt

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-left-top

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

r

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-right

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rb

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-right-bottom

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

t

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

object-top

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

Visibility

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

visibility

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

v

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

visible

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

nv

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

invisible

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

FlexLayout

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flx

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

row

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-row

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rrow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-row-reverse

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

col

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-col

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rcol

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-col-reverse

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

wrap

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-wrap

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rwrap

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-wrap-reverse

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

nowrap

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-nowrap

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

one

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-1

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

auto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-auto

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

initial

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-initial

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-grow

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

nogrow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-grow-0

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shrink

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-shrink

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

noshrink

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

flex-shrink-0

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

JustifyContent

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

jc

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

between

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-between

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

evenly

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-evenly

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

around

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-around

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

JustifyItems

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ji

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-items-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-items-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-items-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

stretch

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-items-stretch

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

JustifySelf

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

js

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

auto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-self-auto

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-self-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-self-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-self-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

stretch

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify-self-stretch

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

AlignContent

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ac

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

content-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

content-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

content-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

between

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

content-between

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

evenly

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

content-evenly

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

around

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

content-around

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

AlignItems

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ai

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

items-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

items-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

items-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

stretch

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

items-stretch

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

baseline

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

items-baseline

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

PlaceContent

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

pc

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-content-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-content-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-content-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

between

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-content-between

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

evenly

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-content-evenly

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

around

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-content-around

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

stretch

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-content-stretch

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

PlaceItems

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

pi

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-items-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-items-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-items-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

stretch

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-items-stretch

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

PlaceSelf

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ps

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

auto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-self-auto

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-self-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-self-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-self-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

stretch

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

place-self-stretch

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

FontFamily

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ff

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sans

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-sans

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

serif

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-serif

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

mono

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-mono

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

FontSize

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

fz

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xs

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-xs

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sm

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-sm

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

\_

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-base

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lg

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-lg

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl2

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-2xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl3

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-3xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl4

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-4xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl5

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-5xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl6

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-6xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

FontWeight

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

fw

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

thin

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-thin

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

extralight

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-extralight

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

light

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-light

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

normal

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-normal

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

medium

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-medium

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bold

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-bold

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

extrabold

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-extrabold

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

black

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-black

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

semibold

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

font-semibold

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

LetterSpace

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ls

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tighter

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tracking-tighter

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tight

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tracking-tight

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

normal

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tracking-normal

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

wide

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tracking-wide

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

wider

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tracking-wider

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

widest

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tracking-widest

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

LineHeight

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lh

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

leading-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tight

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

leading-tight

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

snug

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

leading-snug

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

normal

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

leading-normal

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

relaxed

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

leading-relaxed

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

loose

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

leading-loose

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

ListItems

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

li

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

list-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

disc

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

list-disc

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

decimal

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

list-decimal

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inside

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

list-inside

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outside

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

list-outside

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

TextAlign

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ta

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

left

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-left

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

center

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-center

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

right

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-right

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

justify

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-justify

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

start

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-start

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

end

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

text-end

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

TextTransform

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tt

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

u

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

uppercase

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

l

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lowercase

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

c

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

capitalize

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

n

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

normal-case

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

VerticalAlign

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

va

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

top

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

align-top

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

middle

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

align-middle

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bottom

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

align-bottom

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

BackgroundAttachment

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ba

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

f

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bg-fixed

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

l

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bg-local

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

s

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bg-scroll

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

BorderRadius

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bdr

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sm

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rounded-sm

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

md

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rounded-md

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lg

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rounded-lg

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

full

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rounded-full

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rounded-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

BorderStyle

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bds

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

solid

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border-solid

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

dashed

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border-dashed

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

dotted

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border-dotted

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

double

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border-double

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

collapse

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border-collapse

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

separate

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border-separate

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

Outline

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

\_

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

dashed

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline-dashed

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

dotted

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline-dotted

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

double

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline-double

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

hidden

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

outline-hidden

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

BoxShadow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sm

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow-sm

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

\_

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

md

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow-md

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lg

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow-lg

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow-xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl2

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow-2xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

none

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow-none

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

inner

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

shadow-inner

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

Table

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

tbl

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

auto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

table-auto

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

fixed

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

table-fixed

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

BoxTopo

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bt

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

bd

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

border

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

container

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

container

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

PlacementPosition

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ppos

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

static

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

static

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

fixed

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

fixed

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

absolute

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

absolute

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

relative

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

relative

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sticky

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sticky

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

BoxSizing

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

boxsz

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

b

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

box-border

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

c

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

box-content

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

Prose

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

prse

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

sm

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

prose-sm

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

\_

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

prose-base

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

lg

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

prose-lg

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

prose-xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

xl2

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

prose-2xl

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

GridFlow

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

gf

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

row

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-flow-row

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

col

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-flow-col

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rowd

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-flow-row-dense

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cold

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-flow-col-dense

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

GridAuto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

ga

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cauto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-cols-auto

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cmin

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-cols-min

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cmax

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-cols-max

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

cfr

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-cols-fr

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rauto

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-rows-auto

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rmin

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-ros-min

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rmax

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-rows-max

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

 

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

rfr

.. raw:: html

   </td>

.. raw:: html

   <td class="org-left">

grid-rows-fr

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

EndNotes
~~~~~~~~

Developed By: webworks.monallabs.in
