Introduction
============

GrizlyUDVacator is a tool designed to help with the generation of Unlawful Detainer (UD) vacator documents. It uses a rule-based engine to analyze case details and generate appropriate legal documents.

Features
--------

- Automated document generation based on CCP 473(b) rules
- Interactive CLI interface for data collection
- Rule-based validation and decision making
- Template-based document generation
- Comprehensive error handling and validation

Architecture
------------

The project is organized into several key components:

- ``cli/``: Command-line interface for user interaction
- ``backend/``: Core business logic and rules engine
- ``backend/rules/``: Implementation of legal rules and validation
- ``backend/generator/``: Document generation logic
- ``tests/``: Test suite for ensuring code quality

Getting Started
--------------

To get started with GrizlyUDVacator, please refer to the :doc:`installation` guide.

For detailed usage instructions, see the :doc:`usage` section.

.. toctree::
   :maxdepth: 1

   installation
   usage
   api/index
