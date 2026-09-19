.. _Guided tutorial simulated assets:

Step-by-step tutorial: Simulated assets
=======================================


This document contains a step-by-step guide to building a SMIA agent and deploying it alongside the entire platform. An asset simulator is provided as part of the ecosystem infrastructure, enabling the evaluation of both the agent’s and the platform’s performance. It offers detailed steps to follow, as well as source code for specific parts, to successfully reproduce the development tutorial.

.. note::

    All resources for this tutorial are available in the official SMIA repository.

    .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/examples/tutorials/SMIA_extension_simulated_assets
            :color: primary
            :outline:

            :octicon:`container;1em` Step-by-step tutorial GitHub resources

.. TODO HAY QUE AÑADIR LOS RECURSOS A GITHUB


Introduction
------------

Tutorial Description
~~~~~~~~~~~~~~~~~~~~

The tutorial consists of three phases. It starts by generating the necessary pre-configuration, such as the CSS-enriched AAS model for each SMIA instance. Next, the entire SMIA platform is deployed to evaluate all the instances associated with these CSS-enriched AAS models, thanks to the necessary infrastructure (in particular, SMIA Operator). Finally, it evaluates the autonomous interaction between SMIA instances by deploying and running a BPMN manufacturing plan executed by an SMIA PE agent. The three phases are illustrated in the following figure:

.. figure:: ../../_static/images/guides_images/SMIA_guided_tutorial_simAss_steps.jpg
   :alt: SMIA simulated assets guided tutorial steps

   **Figure**: SMIA simulated assets guided tutorial steps

The objective is to evaluate the CSS-enriched AAS models using simulated assets to test their performance. To do this, we will use the Assets Simulator, an infrastructure component of the SMIA ecosystem.

.. note::

    The guide for Asset Simulators is available at :octicon:`repo;1em` :ref:`SMIA ecosystem Assets Simulators`.


In this tutorial, we will use the HTTP-based simulator, which provides three types of assets, each with different capabilities:

The following figure shows the CSS-enriched AAS elements for the three types of assets provided by the HTTP asset simulator:

.. figure:: ../../_static/images/guides_images/SMIA_guided_tutorial_simAss_asset_info.jpg
   :alt: SMIA simulated assets guided tutorial assets info

   **Figure**: SMIA simulated assets guided tutorial assets info
