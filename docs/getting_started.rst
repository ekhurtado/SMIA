Getting Started
===============

|github| |readthedocs| |pypi| |dockerhub| |youtube| |doi|

----

.. |github| image:: https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white
   :target: https://github.com/ekhurtado/SMIA
   :alt: GitHub

.. |readthedocs| image:: https://img.shields.io/badge/readthedocs-%238CA1AF.svg?style=for-the-badge&logo=readthedocs&logoColor=white
   :target: https://smia.readthedocs.io/en/latest/
   :alt: Read the Docs

.. |pypi| image:: https://img.shields.io/badge/pypi-%23008bdd.svg?style=for-the-badge&logo=pypi&logoColor=white
   :target: https://pypi.org/project/smia/
   :alt: PyPI

.. |dockerhub| image:: https://img.shields.io/badge/dockerhub-%233775A9.svg?style=for-the-badge&logo=docker&logoColor=white
   :target: https://hub.docker.com/r/ekhurtado/smia
   :alt: DockerHub

.. |youtube| image:: https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white
   :target: https://www.youtube.com/playlist?list=PLs6bFF_iqW3GB_8bUMn1QqoiXcQDXPvJh
   :alt: YouTube

.. |doi| image:: https://img.shields.io/badge/Paper-%23fab608.svg?style=for-the-badge&logo=doi&logoColor=white
   :target: https://doi.org/10.1016/j.jii.2025.100915
   :alt: DOI

SMIA is a software that implements an AAS-compliant Digital Twin (DT) that is based on a flexible manufacturing-centered ontology.

.. image:: _static/images/SMIA_logo_positive.png
  :align: center
  :width: 400
  :alt: SMIA main logo

The features of the SMIA approach include:

    - free & open-source
    - AAS-compliant: standardized approach
    - Ontology-based
    - easily customizable and extendable
    - self-configuration at software startup
    - easy to start-up
    - containerized solution

Documentation project structure
-------------------------------

The SMIA project documentation repository is structured as follows:

    :octicon:`repo;1em` :ref:`SMIA User Guide`: these guides helps with the usage of SMIA software and related tools.

    :octicon:`repo-pull;1em` :ref:`SMIA Use Cases`: these pages detail all the use cases developed within the SMIA approach.

    .. :octicon:`repo;1em` :ref:`AAS Developer Guide`: this guide helps with the development of the :term:`AAS model`, that is the basis for SMIA self-configuration.

    :octicon:`code-review;1em` :ref:`API documentation`: the entire documented source code of SMIA software.

    :octicon:`book;1em` :ref:`Glossary`: the glossary shows the list of terms relating to the SMIA approach.

    :octicon:`versions;1em` :ref:`Contributing`: shows the different ways to contribute to the SMIA approach.

    :octicon:`info;1em` :ref:`About the Project`: general information about the SMIA approach (e.g. contact information).

    :octicon:`link-external;1em` :ref:`Recommended Links`: information related to SMIA approach is available in this section.

    :octicon:`code-of-conduct;1em` :ref:`Code of Conduct`: the definition of community standards for the participation of the contributors.

    :octicon:`tag;1em` :ref:`Release Notes`: notes about all the releases and pre-releases of SMIA software development.


Additional resources
--------------------

There are some additional resources offered within the SMIA approach. All of these resources are available in the GitHub repository.

    .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_resources/aas_ontology_reader/
            :color: primary
            :outline:

            :octicon:`mark-github;1em` AAS ontology reader

    This tool contains the source code of a reader capable of analyzing an AAS model based on a given OWL ontology.

    .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_resources/aasx_package_explorer_resources/
            :color: primary
            :outline:

            :octicon:`mark-github;1em` AASX Package Explorer Resources

    This tool contains the JSON files to extend the AASX Package Explorer software with the Capability-Skill-Service (CSS) model.

    .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_resources/css_smia_ontology/
            :color: primary
            :outline:

            :octicon:`mark-github;1em` CSS-SMIA ontology model

    This tool contains the ontology for the Capability-Skill-Service (CSS) model in an OWL file. It also provides some ExtendedClasses implemented in Python.

    .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_tools/smia_operator_agent/
            :color: primary
            :outline:

            :octicon:`mark-github;1em` SMIA Operator Agent

    This tool provides a SPADE agent with an easy-to-use graphical interface. This agent enables to automatically discover available SMIA instances and their corresponding CSS-enriched information, as well as to request the execution of specific capabilities and assign them to the appropriate agents.







.. TODO hay que pensar como hacer esta pagina

.. TODO Pensar si añadir aqui las guias

.. Getting started pages examples

.. `<https://faaast-service.readthedocs.io/en/latest/basics/getting-started.html>`_

.. `<https://ranchermanager.docs.rancher.com/getting-started/overview>`_

.. `<https://kubernetes.io/docs/setup/>`_
