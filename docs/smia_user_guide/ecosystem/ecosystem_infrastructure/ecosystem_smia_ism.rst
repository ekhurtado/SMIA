.. _SMIA ecosystem SMIA ISM:

SMIA ecosystem: SMIA ISM
========================

The SMIA ISM (Infrastructure Services Manager) is an infrastructure agent that bridges the gap between the normalized MAS composed by SMIA instances and non-agent infrastructure. This mediator agent encapsulates essential infrastructure services and exposes them to the MAS using the standardized :term:`FIPA-SMIACL` language.

.. note::

    This architectural decoupling ensures the autonomous nature of the agent ecosystem without compromising its integrity. It guarantees seamless operational execution of the SMIA instances representing the manufacturing assets and the corresponding production plan. For this reason, SMIA ISM is necessary in environments where agents need to interact with external infrastructure.

Source Code Reference
---------------------

Regarding internal development, the SMIA ISM leverages SMIA extension mechanisms to incorporate sufficient autonomy to manage the exposed services, as well as connectivity to external infrastructure. Extended agent capabilities are developed as a cyclic behaviour that leverages SMIA's internal module ``smia.logic.agent_services.AgentServices`` to manage the infrastructure services (registration, querying, execution, etc.).

.. dropdown:: Link to SMIA ISM logic source code
       :octicon:`link;1em;sd-text-primary`

       .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_tools/extended_agents/smia_ism
            :color: primary
            :outline:

            :octicon:`mark-github;1em` SMIA ISM agent source code

.. .. seealso::

    .. The API documentation for the SMIA ISM source code is also available at :octicon:`repo;1em` :ref:`API documentation SMIA ecosystem <API documentation SMIA ecosystem>`.

Architecture and implementation
-------------------------------

SMIA agents are empowered to coordinate on a peer-to-peer basis to resolve complex flexible manufacturing scenarios. The SMIA ISM acts as a key component for efficiently decoupling and linking two distinct environments:

* The interoperable and standardized agent-based environment communicating via an I4.0 language (:term:`FIPA-SMIACL`).
* The external infrastructure environment, currently composed of OpenAPI-compliant services, such as the SMIA-I KB and BaSyx AAS Repository.

To ensure consistency, the agent utilizes a standardized interaction pattern based on the OpenAPI specification with this external infrastructure. Thus, the SMIA ISM communicates peer-to-peer with other agents via FIPA-SMIACL while simultaneously managing external infrastructure communications through appropriate protocols, such as HTTP-based OpenAPI.

Infrastructure Services request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Internally, requests for infrastructure services received by the SMIA ISM from the agent environment are validated against the corresponding schema: ``SMIAACLMessageInfo.SMIA_ISM_ACL_INFRASTRUCTURE_SERVICE_TEMPLATE``. This schema is detailed in the following table:

[ADD TABLE]

The content of the FIPA-SMIACL message is also validated against the JSON schema corresponding to the specified ontology (``ACLSMIAJSONSchemas.JSON_SCHEMA_ACL_SMIA_ONTOLOGIES_MAP``). If the infrastructure service request is valid, a single-execution behavior is launched for its dedicated management. Thus, it is leveraged the same decoupled pattern from the SMIA core for incoming communications: the dynamic generation of asynchronous threads to enable an efficient and scalable management of interactions, while minimizing potential failures (if a problem arises, the global execution is not affected).

Infrastructure Services available
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

al aprovechar el módulo ``smia.logic.agent_services.AgentServices`` para la gestión de los servicios que expone al entorno agentico se logra

The SMIA ISM dynamically links infrastructure service identifiers to related executable methods, enabling their decoupled execution. This strategic decision simplifies the addition of new services and the maintenance of existing ones, requiring only a change in the associated executable method.

It exposes and manages the following primary services to the Multi-Agent System:

* **Registry services:** These expose registry-related functionalities, including operations such as ``RegisterSMIAInstance`` and ``RegisterCSSElement``.
* **Discovery services:** These enable advanced asset lookup, exposing functionalities such as ``GetSMIAInstanceIDByAssetID``, ``GetAllAssetIDByCapability``, and ``GetAssetAdministrationShellById``.

Execution Workflow Example
--------------------------

When a manufacturing plan task requires a specific capability rather than a predefined asset, the SMIA Process Engine (PE) must dynamically discover available options. The interaction follows a distributed FIPA-ACL-compliant sequence:

#. **Capability Discovery Request:** The system requests a discovery service from the SMIA ISM to find all assets offering the required capability using the ``GetAllAssetIDByCapability`` identifier.
#. **External Infrastructure Query:** The SMIA ISM queries the SMIA-I KB for the associated CSS elements, as each instance has previously registered all its CSS information.
#. **Identifier Retrieval:** The SMIA ISM returns the identifiers of the appropriate compatible assets.
#. **Distributed Negotiation:** Finally, the resulting associated SMIA instances are requested to engage in a social, distributed negotiation to determine the most appropriate candidate.



