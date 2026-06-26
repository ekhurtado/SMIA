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

.. seealso::

    The API documentation for the SMIA ISM source code is also available at :octicon:`repo;1em` :ref:`API documentation SMIA ecosystem <API documentation SMIA ecosystem>`.

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


Execution example
-----------------

When an SMIA instance requires global information or needs to expose its capabilities beyond its own ACL interface, it requests an infrastructure service from the SMIA ISM. Possible scenarios include, but are not limited to, the following:

* **Expose its own information**: each SMIA instance retrieves all information about its asset during its self-configuration phase. If the instance wants to be available when another instance requests global information, it must request :bdg-primary:`RegisterSMIAInstance`. Additionally, if it wants to expose its CSS information extracted during that phase, it will request :bdg-primary:`RegisterCSSElements`. This ensures the availability of both the instance and its functional information.
* **Discovery of SMIAs representing assets with a given capability**: when an SMIA instance needs to send a CSS execution request for a production task but does not know who can perform it, it must gather some global information to initialize a distributed negotiation and identify the most suitable asset. This situation can occur during the execution of the :octicon:`repo;1em` :ref:`SMIA ecosystem SMIA PE <SMIA ecosystem SMIA PE>`.
    #. **Discovery of assets with a given capability**: first, it needs to obtain the assets associated with that capability. If the associated SMIA instances have previously registered their CSS information in the SMIA-I KB, this can be obtained using the capability's IRI via :bdg-primary:`GetAllAssetIDByCapability`.
    #. **Discovery of assets with a given capability**: then, once the list of assets has been obtained, it is necessary to retrieve the identifiers of their associated SMIA instances in order to enable communication via FIPA-SMIACL. The identifier of the SMIA agent associated with a given asset can be obtained via :bdg-primary:`GetSMIAInstanceIDByAssetID`.

The SMIA internal code provides utilities that facilitate the requesting of infrastructure services from SMIA ISM by any SMIA agent. Below are two code examples for the different types of services. Both code snippets are part of a SPADE behavior, which is responsible for sending messages.

.. dropdown:: :octicon:`code;1em;sd-text-primary` Sample code for registering CSS capabilities and skills

    .. code:: python

        from smia.logic import inter_smia_interactions_utils, , acl_smia_messages_utils
        from smia.utilities.aas_related_services_info import AASRelatedServicesInfo
        from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas

        capability_json = {"iri": "http://www.w3id.org/upv-ehu/gcis/css-smia#Capability01",
          "assets": [{"kind": "Instance","id": "http://example.com/ids/asset001"}],
          "name": "capability01", "isRealizedBy": ["http://www.w3id.org/hsu-aut/css#Skill01"],
          "category": "AssetCapability", "hasLifecycle": "ASSURANCE"
        }
        skill_json = {"iri": "http://www.w3id.org/hsu-aut/css#Skill01", "hasImplementationType": "OPERATION",
          "accessibleThrough": ["http://www.w3id.org/hsu-aut/css#SkillInterface01"],
          "name": "skill01"
        }
        css_elements_json = {'capabilities': [capability_json], 'skills': [skill_json]}

        # Obtain all the asset identifiers associated to the given capability
        smia_ism_jid = (f"{AASRelatedServicesInfo.SMIA_ISM_ID}@"
                        f"{await acl_smia_messages_utils.get_xmpp_server_from_jid(self.agent.jid)}")
        register_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
            # 'gcis1@xmpp.jp', await acl_smia_messages_utils.create_random_thread(self.agent),
            smia_ism_jid, await acl_smia_messages_utils.create_random_thread(self.agent),
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE,
            protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=await acl_smia_messages_utils.
            generate_json_from_schema(ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE, serviceID=
            AASRelatedServicesInfo.AAS_INFRASTRUCTURE_REGISTRY_CSS_ELEMENTS, serviceType=
            AASRelatedServicesInfo.AAS_INFRASTRUCTURE_SERVICE_TYPE_REGISTRY, serviceParams=css_elements_json))
        await self.send(register_acl_msg)


.. dropdown:: :octicon:`code;1em;sd-text-primary` Sample code for discovering assetd with a given capability

    .. code:: python

        from smia.logic import inter_smia_interactions_utils, , acl_smia_messages_utils
        from smia.utilities.aas_related_services_info import AASRelatedServicesInfo
        from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas

        # Obtain all the asset identifiers associated to the given capability
        smia_i_kb_api_body = await acl_smia_messages_utils.
            generate_json_from_schema(ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE,
            serviceID=AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ALL_ASSET_BY_CAPABILITY,
            serviceType=AASRelatedServicesInfo.AAS_SERVICE_TYPE_DISCOVERY, serviceParams=capability_iri)
        request_assets_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
            f"{AASRelatedServicesInfo.SMIA_ISM_ID}@"
            f"{await acl_smia_messages_utils.get_xmpp_server_from_jid(self.myagent.jid)}",
            await acl_smia_messages_utils.create_random_thread(self.myagent), FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
            ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE, protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL,
            msg_body=smia_i_kb_api_body)
        await self.send(request_assets_acl_msg)



