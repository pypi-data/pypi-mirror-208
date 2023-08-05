======
pop-ml
======

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/


pop-ml is a Python library that simplifies the integration of AI-powered translation
capabilities into any Python project.  It leverages Hugging Face Transformers and pretrained
tokenizers to provide an accessible translation experience. pop-ml aims to offer a
straightforward API for translating strings in Python code, ensuring compatibility with
widely-used projects.

About
=====


pop-ml is a comprehensive Python library designed to facilitate the integration of AI-
powered translation capabilities into Python projects. The primary goal of pop-ml is to
provide developers with an easy-to-use and seamless translation experience, allowing them
to translate strings in their Python code to any language.

The library is built on top of the Hugging Face Transformers library and utilizes pretrained
tokenizers to deliver accurate and efficient translations. By leveraging state-of-the-art
language models, pop-ml ensures high-quality translations while maintaining simplicity in
its API.


What is POP?
------------

This project is built with `pop <https://pop.readthedocs.io/>`__, a Python-based
implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring
together concepts and wisdom from the history of computing in new ways to solve
modern computing problems.

For more information:

* `Intro to Plugin Oriented Programming (POP) <https://pop-book.readthedocs.io/en/latest/>`__
* `pop-awesome <https://gitlab.com/vmware/pop/pop-awesome>`__
* `pop-create <https://gitlab.com/vmware/pop/pop-create/>`__

Getting Started
===============

Prerequisites
-------------

* Python 3.8+
* git *(if installing from source, or contributing to the project)*

Installation
------------

.. note::

   If wanting to contribute to the project, and setup your local development
   environment, see the ``CONTRIBUTING.rst`` document in the source repository
   for this project.

If wanting to use ``pop-ml``, you can do so by either
installing from PyPI or from source.

Install from PyPI
+++++++++++++++++

To install pop-ml from PyPI, simply run the following command:

.. code-block:: bash

    pip install pop-ml

This will install the latest version of pop-ml, along with all required dependencies.

Install from source
+++++++++++++++++++

To install pop-ml from source, first clone the repository from GitLab:

.. code-block:: bash

    git clone https://gitlab.com/vmware/pop/pop-ml.git

Next, navigate to the cloned repository directory:

.. code-block:: bash

    cd pop-ml

Finally, install the package using pip:

.. code-block:: bash

    pip install .

Usage
=====

pop-ml can be used both as a command-line tool (pop-translate) and as a Python library.
Below are examples of how to use pop-ml in both ways.

CLI Examples
------------

To use the pop-translate command-line tool, you can pass the text you want to translate as
an argument, along with any additional options:

.. code-block:: bash

    pop-translate "Hello, World!" --translate-to es

This command will translate the input text "Hello, world!" from English (en) to Spanish (es).

To see a full list of available options, run:

.. code-block:: bash

    pop-translate --help


Python Examples
---------------

Here is an example of how to use pop-ml as a Python library:


.. code-block:: python

    import pop.hub

    # Initialize the hub
    hub = pop.hub.Hub()

    # Add the "ml" dynamic namespace to the hub
    hub.pop.sub.add(dyne_name="ml")

    # Load config values onto hub.OPT
    hub.pop.config.load(["pop_ml"], cli="pop_ml")

    # Call the idempotent "init" of pop-ml's tokenizer using values from config
    hub.ml.tokenizer.init(
        model_name=hub.OPT.pop_ml.model_name,
        dest_lang=hub.OPT.pop_ml.dest_lang,
        source_lang=hub.OPT.pop_ml.source_lang,
        pretrained_model=hub.OPT.pop_ml.pretrained_model_class,
        pretrained_tokenizer=hub.OPT.pop_ml.pretrained_tokenizer_class,
    )
    # Call the function to translate the text
    result = hub.ml.tokenizer.translate([text])
    print(result)


In this example, we initialize the hub, load the "ml" dynamic namespace and config values
onto it, initialize the tokenizer, and call the function to translate the text. The output will be
the translated text.

Roadmap
=======

Reference the `open issues <https://gitlab.com/vmware/pop/pop-ml/issues>`__ for a list of
proposed features (and known issues).

Acknowledgements
================

* `Img Shields <https://shields.io>`__ for making repository badges easy.
