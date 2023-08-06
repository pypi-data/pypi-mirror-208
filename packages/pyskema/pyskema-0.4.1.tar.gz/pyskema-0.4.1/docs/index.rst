.. Pyskema documentation master file, created by
   sphinx-quickstart on Tue Mar  7 14:56:46 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pyskema's documentation!
===================================

About
-----

Pyskema is a small module used to define schema for structured data.

The schema can be used to validate, document and generate data.

Installation
------------

Use :code:`pip install pyskema`.

Usage
-----

Here is a simple example of defining a model of data:

.. code:: python

    from pyskema import Node, AtomType

    model = Node.of_record({
        "number of schleem": Node.of_atom(AtomType.INT),
        "length of dinglepop": Node.of_atom(AtomType.FLOAT),
        "color of fleeb": Node.of_atom(AtomType.OPTION, [
            "pink",
            "red",
            "octarine",
        ]),
    })

The model can be used to validate a concrete piece of data from any source (see :py:mod:`pyskema.validate`).

.. code:: python

    from pyskema.validate import validate, InvalidDataError
    from json import load

    with open("plumbus.json") as f:
        data = load(f)

    try:
        validate(data, model, fail=True):
    except InvalidDataError as e:
        print("The data does not match:")
        explanation, = e.args
        print(explanation)
    else:
        print("all good!")


For documentation purpose, you can automatically describe a schema (see :py:mod:`pyskema.describe`).

.. code:: python

    from pyskema import Node, AtomType, describe

    model = Node.of_record(
        {
            "n_schleem": Node.of_atom(
                AtomType.STR,
                description="number of dangling schleems",
            ),
            "l_ding": Node.of_atom(
                AtomType.FLOAT,
                description="length of a the dinglepop in mm",
            ),
            "c_fleeb": Node.of_atom(
                AtomType.OPTION,
                [
                    "pink",
                    "red",
                    "octarine",
                ],
                description="color of the fleeb",
            ),
        },
        description="a plumbus specification"
    )

    # >>> describe(model)
    # a plumbus specification
    #   n_schleem: number of dangling schleems
    #       value of type str
    #   l_ding: length of a the dinglepop in mm
    #       value of type float
    #   c_fleeb: color of the fleeb
    #       one of 'pink', 'red', or 'octarine'


You can also clone an existing model with modifications with methods :py:func:`pyskema.schema.Node.delete` and :py:func:`pyskema.schema.Node.inject`.

More details can be found in the `reference <./ref/pyskema.html>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   ref/pyskema

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
