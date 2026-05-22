.. _SMIA ecosystem SMIA PE:

SMIA ecosystem: SMIA PE
=======================

SMIA Production Execution (PE) is an extended agent with proactive autonomy, responsible for autonomously orchestrating and executing specific manufacturing process workflows. These workflows are described using a CSS-enriched BPMN model, which defines the sequence of tasks along with contingencies for handling unforeseen events. Unlike reactive agents, SMIA PE represents production plans as logical assets and uses SMIA's native extension mechanisms to achieve the required autonomy.

.. note::

    SMIA PE software has been used in the :octicon:`repo;1em` :ref:`Flexible small-scale manufacturing <Use case flexible small-scale manufacturing>`, which has an associated visual resource available on :octicon:`video;1em` `Youtube <https://www.youtube.com/watch?v=f5_2QddHT5g&list=PLs6bFF_iqW3HEwYAFOMHvW0xEngXnVF9K>`_.

    SMIA PE requires valid CSS-driven BPMN workflows. To facilitate the design and development of these workflows, a plugin for Camunda Modeler, the leading BPMN editor, is offered within the SMIA ecosystem, detailed in :octicon:`repo;1em` :ref:`SMIA ecosystem Camunda Modeler`.

Source Code Reference
---------------------

The SMIA PE acts proactively to execute flexible manufacturing through standardized interaction protocols based on :term:`FIPA-SMIACL` with the SMIA agents associated with involved production assets. Its embedded Graphical User Interface (GUI) displays the software's operation in real time and provides control mechanisms for the process. The GUI is accessible via a web browser and has been developed using the native web interface functionalities of SPADE.

.. dropdown:: Link to SMIA PE source code
       :octicon:`link;1em;sd-text-primary`

       .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_tools/extended_agents/smia_pe
            :color: primary
            :outline:

            :octicon:`mark-github;1em` SMIA PE agent source code

.. seealso::

    The API documentation for the SMIA ecosystem source code is also available at :octicon:`repo;1em` :ref:`API documentation SMIA ecosystem <API documentation SMIA ecosystem>`.

Internal Design and Capabilities
--------------------------------

To achieve sufficient autonomy to interpret flexible workflows and provide their automated execution, the SMIA PE design relies on two main extended capabilities:

* **AutomatedProductionCapability**: An agent capability endowed with autonomy to interpret, analyze, and execute modular production plans. It uses *Spiffworkflow*, an open-source Python package, to parse the CSS-enriched BPMN files. It is implemented through the agent behavior *BPMNPerformerBehavior*. Another complementary behavior (*ReceiveProductionACLBehavior*) manages the suspension of workflow execution until the associated incoming communication is received (if SMIA PE needs to interact with other components, it must wait until the interaction is complete).
* **PEGUICapability**: An agent capability that provides the embedded web GUI for operational management by a human responsible for production (e.g., stopping and starting execution). It is implemented through the agent behaviour *PEGUIBehaviour*.

Operational Lifecycle
---------------------

The operational procedure required to deploy and utilize the software is structured into two main phases, enabling the design and subsequent autonomous execution of flexible manufacturing plans.

* **Manufacturing Design Phase:** This phase centers on modeling the production plan as a logical asset. It involves identifying available physical and logical assets and designing the production process as a CSS-driven BPMN workflow. This procedure (detailed in :octicon:`repo;1em` :ref:`SMIA ecosystem Camunda Modeler`) involves defining required capabilities, skills, and contingency tasks, and is concludes by describing the production plan as an active, encapsulated BPMN file within an AASX package. This represents the CSS-enriched AAS model of the production plan from which the SMIA PE instance can self-configure.
* **Manufacturing Execution Phase:** Following the design, this phase involves the autonomous execution. It requires the instantiation of the specific SMIA PE instance and all involved assets via SMIA instances, and the deployment of the supporting infrastructure (e.g., XMPP Server, SMIA ISM, AAS Repository). Within this operational environment, the SMIA PE proactively analyzes the generated BPMN process to orchestrate the distributed logic.

Deployment Environment
----------------------

To deploy the SMIA PE software, you need a valid environment that meets the operational requirements of any SMIA agent. A valid environment containing SMIA PE can be easily generated using the tool provided in this documentation platform: :ref:`SMIA Environment Builder`: in step 3, *Include CSS-enriched Manufacturing Plan* must be selected, and the AASX file containing the BPMN workflow must be added.

It is recommended to deploy it in virtualized environments that include the specific SMIA PE agent, the SMIA agents involved in the process to be executed, and the necessary supporting infrastructure. Therefore, Docker Compose or Kubernetes can be selected in the *Environment Builder*.

The support infrastructure must be selected in step 2 of the *Environment Builder*: the AAS server, SMIA-I KB, and SMIA ISM.

When deploying, centralize the container and service definitions within the specific file: ``docker-compose.yml`` via Docker Compose and the specific YAML file via Kubernetes.

- The JID configuration is managed via the ``AGENT_ID`` and ``AGENT_PSSWD`` environment variables.
- Verify that the specific production plan model (`AASX file`) is located in the ``aas/`` directory.


Using the SMIA PE
-----------------


Accessing the GUI
~~~~~~~~~~~~~~~~~

To access the SMIA PE control panel, open a web browser and navigate to the interface:

.. code:: bash

    http://localhost:10000/smia_pe

.. note::

    In virtualized environments, the IP address should be changed to that of the container. It should also be verified whether the container's exposed port matches or if a different one has been defined.

Execution Workflow
~~~~~~~~~~~~~~~~~~

Following deployment, the SMIA PE autonomously manages the execution of the modular production plan. The operation follows a logical internal workflow:

#. **Plan Initialization:** Upon startup, the agent extracts the BPMN file from the AASX package and parses it using *Spiffworkflow* to extract essential functional information.
#. **Dynamic Discovery:** For tasks lacking a pre-assigned asset, SMIA PE queries the SMIA ISM to discover all assets offering the required manufacturing capability.
#. **Decentralized Negotiation:** If multiple assets are found, the agent initiates the FIPA-CNP protocol. Participating SMIA instances negotiate through peer-to-peer social interactions to determine the optimal candidate.
#. **Task Execution:** Once the appropriate asset is identified, SMIA PE requests task execution using the FIPA-RP protocol.
#. **Contingency Management:** If the production process defines events (e.g., a timeout modeled via a BPMN *ExclusiveGateway*), the agent monitors these conditions. If a timeout is met, it automatically redirects the workflow to predefined recovery tasks.

Through this workflow, the SMIA PE ensures dynamic and flexible execution, interacting seamlessly with the multi-agent system and underlying infrastructure.