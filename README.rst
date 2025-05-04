GrizlyUDVacator
===============

A tool for generating Unlawful Detainer (UD) vacator documents.

Features
--------

- Automated document generation based on CCP 473(b) rules
- Interactive CLI interface for data collection
- Rule-based validation and decision making
- Template-based document generation
- Comprehensive error handling and validation

Installation
------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/jurisgpt/GrizlyUDVacator.git
      cd GrizlyUDVacator

2. Create and activate a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt
      pip install -r requirements-dev.txt

   Note: The development requirements include docxtpl and python-docx for DOCX document generation.

Usage
-----

.. code-block:: bash

   make interview

Development
-----------

To run tests:

.. code-block:: bash

   make test

To check code quality:

.. code-block:: bash

   make lint

To analyze code complexity:

.. code-block:: bash

   make analyze

To build documentation:

.. code-block:: bash

   make docs

License
-------

MIT License
