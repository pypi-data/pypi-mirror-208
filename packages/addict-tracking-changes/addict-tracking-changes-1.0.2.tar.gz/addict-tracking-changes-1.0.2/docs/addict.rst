addict-tracking-changes Library Documentation
=============================================

addict-tracking-changes is a Python library that provides a custom Dict class that enhances the functionality of Python dictionaries. It tracks changes made to the dictionary, allows freezing and unfreezing of keys, and provides utility functions for working with the dictionary.

Note: Its recommended to use dpath.new to create or set a new value for tracking to work properly. The dot expression also tested to work as well. 

Originally, this repository was a fork of `addict <https://github.com/mewwts/addict>`_ by Mats Julian Olsen.
Overtime, it has substantially diverged in functionality and codebase that it seemed to make
sense to break out as its own repository.

The original addict: provides an alternative and succinct interface to manipulate a dictionary. This is especially
useful when dealing with heavily nested dictionaries. As an example (taken from https://github.com/mewwts/addict),
a dictionary created using the standard python dictionary interface looks as follows:

.. code-block:: python

    body = {
        'query': {
            'filtered': {
                'query': {
                    'match': {'description': 'addictive'}
                },
                'filter': {
                    'term': {'created_by': 'Mats'}
                }
            }
        }
    }

can be summarized to the following three lines:

.. code-block:: python

    body = Dict()
    body.query.filtered.query.match.description = 'addictive'
    body.query.filtered.filter.term.created_by = 'Mats'

This repo builds on the original addict and adds contraptions to track key additions in the dictionary.
This feature comes in quite handy in building reactive webapps where one has to respond 
to all the changes made on the browser. Addict-tracking-changes is the underpinning
data-structure in `ofjustpy <https://github.com/Monallabs-org/ofjustpy>`_: a python-based web framework built from `justpy <https://github.com/justpy-org/justpy>`_.

The functions relevant to tracking changed history are:
``get_changed_history`` and ``clear_changed_history``.
The ``get_changed_history`` returns an iterator of XPath style paths like ``/a/b/c/e``.


Installation
------------

This project is not on PyPI. It's a simple package with no third-party dependency. 
Simply clone from GitHub and include the source directory in your PYTHONPATH.


Behaviour when values are instances of container types
------------------------------------------------------

Addict works as expected when the values of keys are simple data types (such as string, int, float, etc.). However, for container types such as dict, list, tuples, etc. the behaviour somewhat differs.

- dicts are treated as opaque objects just like simple data types

.. code-block:: python

   from addict import Dict

   mydict = Dict()
   mydict.a.b.c = {'kk': 1}
   mydict.a.b.e = {'dd': 1}

   for _ in mydict.get_changed_history():
       print(_)

This will print:

.. code-block:: text

   /a/b/c
   /a/b/e

and not:

.. code-block:: text

   /a/b/cc/kk
   /a/b/e/dd

- lists are seen as containers, i.e., `get_changed_history` will report path for each element of the list

.. code-block:: python

   from addict import Dict

   mydict = Dict()

   mydict.a.b = [1, [1]]
   mydict.a.c = [2, [2, [3]]]

`get_changed_history` will report the following paths:

.. code-block:: text

   /a/b/0,
   /a/b/1/0,
   /a/c/0,
   /a/c/1/0,
   /a/c/1/1

- tuple, namedtuple, sets behave the same as dict and are treated as opaque data structures.

Known bugs and Caveats
----------------------

1. Only tracks field additions. Deletions and updates are not tracked.
2. `freeze` doesn't guard against deletions
3. Building dict from another dict as shown in the following expression won't work:

.. code-block:: python

   cjs_cfg = Dict(other_dict, track_changes=True)

Instead, use:

.. code-block:: python

   cjs_cfg = Dict(track_changes = True)
   with open("other_dict.pickle", "rb") as fh:
       x = pickle.load(fh)
   for _ in oj.dictWalker(x):
       oj.dnew(cjs_cfg, _[0], _[1])


Class: Dict
-----------

A custom Dict class that extends the built-in Python dict class with additional features.

Initialization
~~~~~~~~~~~~~~

.. code-block:: python

   d = Dict(<dictionary>, track_changes=<boolean>)

- ``<dictionary>``: A dictionary object or any object that can be converted to a dictionary.
- ``track_changes``: A boolean flag that indicates whether the dictionary should track the changes made to it. Default is False.

Methods
~~~~~~~

- ``freeze(shouldFreeze=True)``: Freezes the dictionary and its nested dictionaries, preventing the addition of new keys. If shouldFreeze is set to False, the dictionary will be unfrozen.

- ``unfreeze()``: Unfreezes the dictionary and its nested dictionaries, allowing the addition of new keys.

- ``get_changed_history(prefix="", path_guards=None)``: Returns a generator that yields the paths of the changed keys in the dictionary.

- ``clear_changed_history()``: Clears the history of changes for the dictionary and its nested dictionaries.

- ``set_tracker(track_changes=False)``: Sets the tracking flag for the dictionary and its nested dictionaries. If track_changes is True, the dictionary will track changes made to it.

Utility Functions
~~~~~~~~~~~~~~~~~

- ``walker(adict, ppath="", guards=None)``: A generator function that recursively walks through a dictionary and yields the paths and values of its keys. If guards is a list of path strings, the function will stop walking at the guarded paths and yield their values.

- ``get_changed_history_list(arritems, tprefix="", path_guards=None)``: Returns a generator that yields the paths of the changed keys in a list.

- ``clear_changed_history_list(arritems)``: Clears the history of changes for a list.

