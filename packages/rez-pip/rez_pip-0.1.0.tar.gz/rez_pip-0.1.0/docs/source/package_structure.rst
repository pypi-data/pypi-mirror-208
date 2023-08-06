=================
Package structure
=================

This page documents an implementation detail. The content of this page shouldn't be relied on
to do any reverse engineer or hack things around.

The packages created by rez-pip will follow a common structure. Let's take a look at an hypothetical
package called ``packageA``:

.. code-block::

    <install path>
    ├── package.py
    ├── python
    │   ├── packageA
    │   │   ├── moduleA.py
    │   │   └── moduleB.py
    │   └── packageA-0.5.7.dist-info
    │       ├── ...
    │       └── ...
    ├── share
    │   └── man
    │       ├── ...
    │       └── ...
    └── scripts
        └── publish.py
