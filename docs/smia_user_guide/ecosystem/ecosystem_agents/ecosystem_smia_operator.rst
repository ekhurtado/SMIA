.. _SMIA ecosystem SMIA Operator:

SMIA ecosystem: SMIA Operator
=============================

The SMIA Operator is a specialized tool that features a graphical interface allowing human users to easily interact with deployed agents. This tool provides a structured view of the functional information (:term:`CSS model`) of the assets and enables users to request tasks from associated SMIA agents without having to deal with the complexity of the required I4.0 Language (FIPA-SMIACL).

Source Code Reference
---------------------

The SMIA Operator represents a human worker and acts as a Digital Twin (DT). Its Graphical User Interface (GUI) has been developed using native web interface functionalities of SPADE.

The source code can be downloaded directly from the official GitHub repository for manually provisioned environments.

.. dropdown:: Link to SMIA Operator source code
       :octicon:`link;1em;sd-text-primary`

       .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_tools/extended_agents/smia_operator_agent
            :color: primary
            :outline:

            :octicon:`mark-github;1em` SMIA Operator agent source code

Deployment Environment
----------------------

The first step is the establishment of an appropriate deployment environment. A valid environment containing SMIA Operator can be easily generated using the tool provided in this documentation platform: :ref:`SMIA Environment Builder`: in step 3, *SMIA Operator* must be selected. There are two primary types of environments for the SMIA Operator.

Local deployment
~~~~~~~~~~~~~~~~

In a local environment, SMIA instances are executed locally.

#. Download the tool from the provided GitHub link.
#. Configure the ``smia_operator_starter.py`` script. The JID must be configured to connect to the same XMPP server to enable agent communication.
#. Specify the path for the ``SMIA_Operator_article.aasx`` model within the starter script. Verify that the model is located in ``smia_archive/config/aas``.
#. Execute the Python launcher script.

Virtualized deployment
~~~~~~~~~~~~~~~~~~~~~~

For virtualized environments, Docker Compose or Kubernetes can be used. The SMIA Operator requires a specific Docker image built upon the core provided by SMIA. This image is available in the `SMIA Docker Hub <https://hub.docker.com/r/ekhurtado/smia-tools/tags>`_.

When deploying via Docker Compose, centralize the container and service definitions within a ``docker-compose.yml`` file.

- The JID configuration is managed via the ``AGENT_ID`` and ``AGENT_PSSWD`` environment variables.
- Verify that the ``SMIA_Operator_article.aasx`` model is located in the ``aas/`` directory.

Execution is triggered by invoking the following command within the directory containing the YAML file and the ``aas/`` folder:

.. code:: bash

    docker compose up

If using a Kubernetes cluster, assuming the required YAML files are located in a ``deploy/`` folder, execute the following command:

.. code:: bash

    kubectl apply -f deploy/

Once deployed, each container initiates its lifecycle by autonomously self-configuring according to its corresponding AAS model.

Using the SMIA Operator
-----------------------

Following the successful instantiation of the SMIA agents, their performance and behavior can be validated. The SMIA Operator autonomously orchestrates the underlying FIPA-SMIACL interactions.

Accessing the GUI
~~~~~~~~~~~~~~~~~

To access the SMIA Operator control panel, open a web browser and navigate to the interface (see :numref:`fig:smia-use-case-operator-dashboard`):

.. code:: bash

    http://localhost:10000/smia_operator

.. note::

    In virtualized environments, the IP address should be changed to that of the container.

Execution Workflow
~~~~~~~~~~~~~~~~~~

The user interface is deliberately designed to abstract underlying technical details and prioritize operational simplicity. The interaction follows a clear operational workflow:

#. **Load CSS Information:** At the top of the GUI, use the :bdg-primary-line:`LOAD` button to execute an automatic search and analysis of available SMIA agents. General statistics are displayed, and the bottom left table is updated with the detected CSS elements, such as capabilities, skills, constraints, or properties.
#. **Select Capability:** Target specific manufacturing capabilities using the :bdg-primary-line:`SELECT` button. The system interactively prompts for required values and updates the bottom right table with compatible assets and their SMIA instances. This separates the capability decision from agent assignment.
#. **Request Execution:** Use the :bdg-primary-line:`REQUEST` button to trigger execution.

   - If a single SMIA instance is selected, it directly executes the capability.
   - If multiple agents are selected, they initiate an autonomous distributed negotiation protocol (via FIPA-SMIACL) to determine the most suitable agent for the task (see :numref:`fig:smia-use-case-acl-messages`).

The outcome of the process, including interpretation steps and negotiation between agents, is recorded chronologically in an execution timeline accessible to the user. This representation brings traceability and operational transparency to the distributed industrial environment.