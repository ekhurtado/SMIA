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

       .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_tools/infrastructure_components/smia_ism
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

.. dropdown:: :octicon:`cache;1em;sd-text-primary` FIPA-SMIACL message schema for SMIA ISM infrastructure services

    .. list-table::
       :header-rows: 1
       :widths: 10 25 40

       * - Attribute
         - Established Value(s)
         - Description
       * - ``performative``
         - ``request``, ``query-if``, ``query-ref``
         - The communicative act: ``request`` to execute an infrastructure service; ``query-if`` and ``query-ref`` to query about them.
       * - ``ontology``
         - ``aas-infrastructure-service``
         - The SMIA ontology classification for infrastructure services.
       * - ``protocol``
         -
         - The interaction protocol (e.g., ``fipa-request`` or ``fipa-query``)
       * - ``language``
         -
         - The language of the message (``smia-language`` is the default value in SMIA).
       * - ``encoding``
         -
         - The encoding format of the message body (``application/json`` is the default value in SMIA).

The content of the FIPA-SMIACL message is also validated against the JSON schema corresponding to the specified ontology for these kind of services (``ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE``):

.. dropdown:: :octicon:`cache;1em;sd-text-primary` JSON schema for infrastructure service messages

    .. list-table::
       :header-rows: 1
       :widths: 15 10 12 53

       * - Field
         - Type
         - Mandatory
         - Description
       * - ``serviceID``
         - ``string``
         - Yes
         - The unique identifier of the infrastructure service to be executed. The SMIA core includes a list of these in ``smia.utilities.aas_related_services_info.py``.
       * - ``serviceType``
         - ``enum``
         - Yes
         - Category of the infrastructure service: ``RegistryService`` for registration operations or ``DiscoveryService`` for lookup operations.
       * - ``serviceParams``
         - Object
         - No
         - Parameters required by the specific service. The expected structure depends on the ``serviceID`` value.


If the infrastructure service request is valid, a single-execution behavior is launched for its dedicated management. Thus, it is leveraged the same decoupled pattern from the SMIA core for incoming communications: the dynamic generation of asynchronous threads to enable an efficient and scalable management of interactions, while minimizing potential failures (if a problem arises, the global execution is not affected).

Infrastructure Services available
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SMIA ISM dynamically links infrastructure service identifiers to related executable methods by leveraging the ``smia.logic.agent_services.AgentServices`` module, thereby enabling their decoupled execution. This strategic decision simplifies the addition of new services and the maintenance of existing ones, requiring only a change in the associated executable method. In addition, it takes advantage of this module’s built-in features, such as the registration and maintenance of identifiers and associated methods, automatic validation of received parameters (e.g., whether the data type is valid) and efficient execution of methods regardless of their implementation (whether they are defined as static, generic, or class methods, and configured for either synchronous or asynchronous execution).

The infrastructure services currently exposed and managed by SMIA ISM are as follows (which are requested by adding their identifiers to the ``serviceID`` field in the JSON body):

* **Registry services:** These expose registry-related functionalities, including operations with identifiers such as :bdg-primary:`RegisterSMIAInstance` and :bdg-primary:`RegisterCSSElements`.
    * Available at ``AASRelatedServicesInfo.AAS_INFRASTRUCTURE_REGISTRY_x`` within ``smia.utilities.aas_related_services_info.py``.
* **Discovery services:** These enable advanced asset lookup, exposing functionalities with identifiers such as :bdg-primary:`GetSMIAInstanceIDByAssetID`, :bdg-primary:`GetAssetIDBySMIAInstanceID`, :bdg-primary:`GetAllAssetIDByCapability`, and :bdg-primary:`GetAssetAdministrationShellById`.
    * Available at ``AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_x`` within ``smia.utilities.aas_related_services_info.py``.

.. note::

    The ``serviceParams`` field of the JSON body is conditionally based on the ``serviceID`` value.

    * For the **Discovery services**, the identifier required by the external infrastructure must be specified as a plain ``string`` depending on the service. In accordance with the service naming convention, these identifiers appear in the service name itself after *By* (e.g., ``assetID`` for ``GetSMIAInstanceIDByAssetID``), with the exception of CSS elements, which must also be IRIs (e.g., the capability IRI for ``GetAllAssetIDByCapability``).
    * For the **Registry services**, the object required by the external infrastructure must be specified. The structure of this object is defined by the external infrastructure. For example, the data schemas for SMIA-I KB are provided in :octicon:`repo;1em` :ref:`SMIA ecosystem SMIA-I KB <SMIA ecosystem SMIA-I KB API schemas>`. Thus, in ``RegisterSMIAInstance``, the *SMIAinstance schema* must be added, and in `RegisterCSSElements`, a list of *Capability schemas* and *Skill schemas* must be added.


Execution Workflow Example
--------------------------

When a manufacturing plan task requires a specific capability rather than a predefined asset, the SMIA Process Engine (PE) must dynamically discover available options. The interaction follows a distributed FIPA-ACL-compliant sequence:

#. **Capability Discovery Request:** The system requests a discovery service from the SMIA ISM to find all assets offering the required capability using the ``GetAllAssetIDByCapability`` identifier.
#. **External Infrastructure Query:** The SMIA ISM queries the SMIA-I KB for the associated CSS elements, as each instance has previously registered all its CSS information.
#. **Identifier Retrieval:** The SMIA ISM returns the identifiers of the appropriate compatible assets.
#. **Distributed Negotiation:** Finally, the resulting associated SMIA instances are requested to engage in a social, distributed negotiation to determine the most appropriate candidate.



