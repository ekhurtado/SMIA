.. _SMIA ecosystem SMIA-I KB:

SMIA ecosystem: SMIA-I KB
==========================

SMIA-I KB (Knowledge Base) provides system information to identify SMIA agents and their CSS functional information for dynamic scenarios. This Knowledge Base offers identifying manufacturing capabilities and associated SMIA instances. The suffix "-I" denotes its function as a support infrastructure component for SMIA instances but not an agent itself, offering complete decoupling.

.. note::

    SMIA-I KB has been used in the :octicon:`repo;1em` :ref:`Flexible small-scale manufacturing <Use case flexible small-scale manufacturing>`, which has an associated visual resource available on :octicon:`video;1em` `Youtube <https://www.youtube.com/watch?v=f5_2QddHT5g&list=PLs6bFF_iqW3HEwYAFOMHvW0xEngXnVF9K>`_.


Source Code Reference
---------------------

The SMIA-I KB leverages an OWL ontological database, enabling efficient management of CSS-related information. Developed in Python, it leverages *OWLready2*, the same ontology library as SMIA. To ensure consistency in its connectivity with the external infrastructure, a homogeneous interaction pattern based on the OpenAPI specification is used.

.. dropdown:: Link to SMIA-I KB source code
       :octicon:`link;1em;sd-text-primary`

       .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/additional_tools/infrastructure_components/smia_i_kb
            :color: primary
            :outline:

            :octicon:`mark-github;1em` SMIA-I KB source code

.. .. seealso::

    .. The API documentation for the SMIA-I KB source code is also available at :octicon:`repo;1em` :ref:`API documentation SMIA ecosystem <API documentation SMIA ecosystem>`.


Deployment Environment
----------------------

SMIA-I KB can be deployed locally by downloading the source code and simply running the module in the ``src`` directory with ``python -m swagger_server``. However, it is recommended to deploy it in a virtualized environment for a self-contained deployment environment. The Docker image of the SMIA-I KB is available in the `SMIA Docker Hub <https://hub.docker.com/r/ekhurtado/smia-tools/tags>`_.

A valid virtualized environment containing SMIA-I KB can be easily generated using the tool provided in this documentation platform: :octicon:`repo;1em` :ref:`SMIA Environment Builder`. To achieve the desired result, in step 2 *SMIA-I KB* must be selected within the infrastructure components.

The deployment command depends on the selected virtualization environment: Docker Compose (``docker compose up``) or Kubernetes (``kubectl apply -f deploy/``). Once deployed, the SMIA-I KB initializes the server and exposes its REST API at the configured port.

.. note::

    As mentioned in the :octicon:`repo;1em` :ref:`SMIA Environment Builder`, if SMIA-I KB is deployed for the SMIA agentic environment, the deployment of the :octicon:`repo;1em` :ref:`SMIA ecosystem SMIA ISM` infrastructure component is required to mediate agent interactions with the Knowledge Base.

Interface and Interaction
-------------------------

The SMIA-I KB exposes a homogeneous and standardized HTTP/REST API following the OpenAPI 3.0.4 specification, built on top of *Flask* Python package. This API provides full programmatic control over the Capability-Skill-Service (CSS) model Knowledge Base, enabling SMIA agents and external manufacturing applications to query capabilities, manage skill parameters, and discover registered SMIA agent instances. All ontology resources (capabilities, skills, constraints, SMIA instances, etc.) are managed through this API, which acts as the exclusive interaction gateway for external components such as SMIA agents (mediated by SMIA ISM) and the AAS Repository.

.. note::

    The SMIA-I KB server listens on port ``8080`` and exposes the API at the base path ``/api/v3``. It is recommended to containerize it, since it is available as a Docker image under ``ekhurtado/smia-tools:latest-smia-kb``.

API overview
~~~~~~~~~~~~

=======================  ======================================================
**Base URL**             ``https://<SMIA-I KB IP>:<SMIA-I KB PORT>/api/v3``
**Content Type**         ``application/json`` (``application/xml`` also
                         supported)
**Specification**        OpenAPI 3.0.4
**Identifier Encoding**  Ontology IRIs must be Base64-URL-encoded when used
                         as path parameters. The Serialization API provides
                         encode/decode utilities for this purpose.
=======================  ======================================================

.. tip::

    SMIA-I KB also offers a web-based graphical interface accessible via the path ``/api/v3/ui/``. It provides detailed information on the complete API, as well as interactive utilities that allow users to send HTTP requests to each specific API and receive the response, along with examples to ensure that these requests comply with the specification.


API reference
~~~~~~~~~~~~~

.. _fig-smia-i-kb-api:

.. figure:: ../../../_static/images/SMIA-I_KB_interface_illustration.png
    :align: center
    :width: 700
    :alt: SMIA-I KB interface

    **Figure**: SMIA-I KB interface

The API is organized into several functional areas corresponding to the CSS (Capability-Skill-Service) model and SMIA operative environment. The :ref:`fig-smia-i-kb-api` illustrates the main resource groups. The following list provides details on each of them.

.. note::

    The ``Serialization API`` is not shown in the figure because it does not interact with the internal database. It provides useful endpoints for users working with AAS and OWL identifiers (*capabilityIdentifier*, *skillIdentifier*), since the OpenAPI specification requires Base64-URL-encoded parameters. The Serialization API provides encode/decode utilities for this purpose.


.. dropdown:: :octicon:`cache;1em;sd-text-primary` Capability API

    This API manages the Capability layer of the CSS model, providing endpoints for creating, reading, updating, and deleting **Capabilities** and their related elements (constraints, skill references, assets).

    .. list-table::
       :header-rows: 1
       :widths: 28 8 22 42

       * - Path
         - Method
         - Description
         - Parameters
       * - ``/capabilities``
         - :bdg-success:`GET`
         - Returns all capabilities
         -
       * -
         - :bdg-warning:`POST`
         - Add a new capability
         - *Body:* ``Capability`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)

       * -
         -
         -
         -
       * - ``/capabilities/$identifiers``
         - :bdg-success:`GET`
         - Returns all capability IRI identifiers
         -

       * -
         -
         -
         -
       * - ``/capabilities/{capabilityIdentifier}``
         - :bdg-success:`GET`
         - Returns a specific capability
         - *Path:* ``capabilityIdentifier`` (Base64)
       * -
         - :bdg-warning:`PUT`
         - Updates an existing capability
         - *Path:* ``capabilityIdentifier`` (Base64); *Body:* ``Capability`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)
       * -
         - :bdg-danger:`DELETE`
         - Deletes a specific capability
         - *Path:* ``capabilityIdentifier`` (Base64)

       * -
         -
         -
         -
       * - ``/capabilities/{capabilityIdentifier}/skill-refs``
         - :bdg-success:`GET`
         - Returns skill references of a capability
         - *Path:* ``capabilityIdentifier`` (Base64)
       * -
         - :bdg-warning:`POST`
         - Add a skill reference to a capability
         - *Path:* ``capabilityIdentifier`` (Base64); *Body:* ``ReferenceIRI`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)

       * -
         -
         -
         -
       * - ``/capabilities/{capabilityIdentifier}/capabilitiesConstraints``
         - :bdg-success:`GET`
         - Returns constraints of a capability
         - *Path:* ``capabilityIdentifier`` (Base64)
       * -
         - :bdg-warning:`POST`
         - Add a constraint to a capability
         - *Path:* ``capabilityIdentifier`` (Base64); *Body:* ``CapabilityConstraint`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)

       * -
         -
         -
         -
       * - ``/capabilities/{capabilityIdentifier}/capabilitiesConstraints/{capabilityConstraintIdentifier}``
         - :bdg-success:`GET`
         - Returns a specific constraint
         - *Path:* both identifiers (Base64)
       * -
         - :bdg-warning:`PUT`
         - Updates a constraint
         - *Path:* both identifiers; *Body:* ``CapabilityConstraint`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)
       * -
         - :bdg-danger:`DELETE`
         - Deletes a constraint
         - *Path:* both identifiers

       * -
         -
         -
         -
       * - ``/capabilities/{capabilityIdentifier}/assets``
         - :bdg-success:`GET`
         - Returns assets of a capability
         - *Path:* ``capabilityIdentifier`` (Base64)
       * -
         - :bdg-warning:`POST`
         - Add an asset to a capability
         - *Path:* ``capabilityIdentifier`` (Base64); *Body:* plain string (asset ID)


.. dropdown:: :octicon:`cache;1em;sd-text-primary` Skill API

    This API manages the Skill layer of the CSS model, providing endpoints for creating, reading, updating, and deleting **Skills** and their associated parameters.

    .. list-table::
       :header-rows: 1
       :widths: 20 10 20 30

       * - Path
         - Method
         - Description
         - Parameters
       * - ``/skills``
         - :bdg-success:`GET`
         - Returns all skills
         -
       * -
         - :bdg-warning:`POST`
         - Add a new skill
         - *Body:* ``Skill`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)

       * -
         -
         -
         -
       * - ``/skills/$identifiers``
         - :bdg-success:`GET`
         - Returns all skill IRI identifiers
         -

       * -
         -
         -
         -
       * - ``/skills/{skillIdentifier}``
         - :bdg-success:`GET`
         - Returns a specific skill by IRI
         - *Path:* ``skillIdentifier`` (Base64)
       * -
         - :bdg-warning:`PUT`
         - Updates an existing skill
         - *Path:* ``skillIdentifier`` (Base64); *Body:* ``Skill`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)
       * -
         - :bdg-danger:`DELETE`
         - Deletes a skill
         - *Path:* ``skillIdentifier`` (Base64)

       * -
         -
         -
         -
       * - ``/skills/{skillIdentifier}/parameters``
         - :bdg-success:`GET`
         - Returns parameters of a skill
         - *Path:* ``skillIdentifier`` (Base64)
       * -
         - :bdg-warning:`POST`
         - Add a parameter to a skill
         - *Path:* ``skillIdentifier`` (Base64); *Body:* ``SkillParameter`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)

       * -
         -
         -
         -
       * - ``/skills/{skillIdentifier}/parameters/{skillParameterIdentifier}``
         - :bdg-success:`GET`
         - Returns a specific parameter
         - *Path:* both identifiers (Base64)
       * -
         - :bdg-warning:`PUT`
         - Updates a skill parameter
         - *Path:* both identifiers; *Body:* ``Skill`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)
       * -
         - :bdg-danger:`DELETE`
         - Deletes a skill parameter
         - *Path:* both identifiers


.. dropdown:: :octicon:`cache;1em;sd-text-primary` SMIA API

    This API manages deployed SMIA agent instances, providing endpoints for registering and querying **SMIA instances** that are part of the normalized manufacturing ecosystem.

    .. list-table::
       :header-rows: 1
       :widths: 28 10 20 42

       * - Path
         - Method
         - Description
         - Parameters
       * - ``/smiaInstances``
         - :bdg-success:`GET`
         - Returns all registered SMIA instances
         -
       * -
         - :bdg-warning:`POST`
         - Register a new SMIA instance
         - *Body:* ``SMIAinstance`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)

       * -
         -
         -
         -
       * - ``/smiaInstances/$identifiers``
         - :bdg-success:`GET`
         - Returns all SMIA instance identifiers
         -

       * -
         -
         -
         -
       * - ``/smiaInstances/{smiaInstanceIdentifier}``
         - :bdg-success:`GET`
         - Returns a specific SMIA instance
         - *Path:* ``smiaInstanceIdentifier``
       * -
         - :bdg-warning:`PUT`
         - Updates an existing SMIA instance
         - *Path:* ``smiaInstanceIdentifier``; *Body:* ``SMIAinstance`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)
       * -
         - :bdg-danger:`DELETE`
         - Deletes a SMIA instance
         - *Path:* ``smiaInstanceIdentifier``


.. dropdown:: :octicon:`cache;1em;sd-text-primary` AAS Repository API

    This API manages the interaction with an AAS server, providing endpoints for integrating with an **AAS Repository** to automatically extract CSS information into the Knowledge Base.

    .. list-table::
       :header-rows: 1
       :widths: 20 10 20 30

       * - Path
         - Method
         - Description
         - Parameters
       * - ``/checkAASRepository``
         - :bdg-success:`GET`
         - Checks availability of the AAS Repository
         - *Query:* ``AASRepositoryURL``

       * -
         -
         -
         -
       * - ``/extractCSSFromAASRepository``
         - :bdg-success:`GET`
         - Extracts CSS information from the AAS Repository
         - *Query:* ``AASRepositoryURL``


.. dropdown:: :octicon:`cache;1em;sd-text-primary` Serialization API

    Utility endpoints for encoding and decoding ontology IRIs in Base64-URL format. These are essential for constructing path parameters in the Capability and Skill API endpoints, which require encoded identifiers.

    .. list-table::
       :header-rows: 1
       :widths: 20 10 20 30

       * - Path
         - Method
         - Description
         - Parameters
       * - ``/serialization``
         - :bdg-warning:`PUT`
         - Encodes a plain string into Base64-URL format
         - *Body:* ``ReferenceIRI`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`) (plain string)

       * -
         -
         -
         -
       * - ``/deserialization``
         - :bdg-warning:`PUT`
         - Decodes a Base64-URL string back to plain text
         - *Body:* ``ReferenceIRIencoded`` (:ref:`REF <SMIA ecosystem SMIA-I KB API schemas>`)


API schemas
~~~~~~~~~~~

.. _SMIA ecosystem SMIA-I KB API schemas:

The following **schemas** define the data structures that are used in request bodies and responses across the API. Although the format is defined in an abstract manner and supports both JSON and XML serialization, it is recommended to use **JSON**.

.. dropdown:: :octicon:`file-badge;1em;sd-text-primary` Capability schema

    .. list-table:: Capability
       :header-rows: 1
       :widths: 20 15 10 55

       * - Field
         - Type
         - Req.
         - Description
       * - ``iri``
         - ``ReferenceIRI``
         - Yes
         - Unique ontology IRI identifier (e.g., ``http://name.org/css-smia#Capability01``)
       * - ``name``
         - ``string``
         - Yes
         - Name of the capability (e.g., ``capability01``)
       * - ``category``
         - ``enum``
         - Yes
         - ``AgentCapability`` or ``AssetCapability``
       * - ``hasLifecycle``
         - ``enum``
         - Yes
         - ``ASSURANCE``, ``OFFER``, or ``REQUIREMENT``
       * - ``isRealizedBy``
         - ``[ReferenceIRI]``
         - Yes
         - Skill IRIs that realize this capability
       * - ``assets``
         - ``[Asset]``
         - Yes
         - Assets that can perform this capability
       * - ``isRestrictedBy``
         - ``[CapabilityConstraint]``
         - No
         - Constraints that restrict this capability

.. dropdown:: :octicon:`file-badge;1em;sd-text-primary` Skill schema

    .. list-table:: Skill
       :header-rows: 1
       :widths: 20 15 10 55

       * - Field
         - Type
         - Req.
         - Description
       * - ``iri``
         - ``ReferenceIRI``
         - Yes
         - Unique ontology IRI identifier
       * - ``name``
         - ``string``
         - Yes
         - Name of the skill (e.g., ``skill01``)
       * - ``accessibleThrough``
         - ``[ReferenceIRI]``
         - No
         - Skill interface IRIs through which the skill is accessible
       * - ``hasParameter``
         - ``[SkillParameter]``
         - No
         - Associated skill parameters
       * - ``hasImplementationType``
         - ``string``
         - No
         - Implementation type (e.g., ``OPERATION``, ``SPADE_BEHAVIOUR``)

.. dropdown:: :octicon:`file-badge;1em;sd-text-primary` SMIAinstance schema

    .. list-table:: SMIAinstance
       :header-rows: 1
       :widths: 20 15 10 55

       * - Field
         - Type
         - Req.
         - Description
       * - ``id``
         - ``ReferenceSMIA``
         - Yes
         - SMIA instance identifier (e.g., ``agentInstance001``)
       * - ``asset``
         - ``Asset``
         - Yes
         - Associated asset information
       * - ``aasID``
         - ``ReferenceAAS``
         - Yes
         - AAS identifier of the instance
       * - ``status``
         - ``string``
         - No
         - Current status (e.g., ``Running``)
       * - ``startedTimeStamp``
         - ``integer``
         - No
         - Unix timestamp of when the instance started
       * - ``smiaVersion``
         - ``string``
         - No
         - SMIA software version (e.g., ``0.2.3``)

.. dropdown:: :octicon:`file-badge;1em;sd-text-primary` Asset schema

    .. list-table:: Asset
       :header-rows: 1
       :widths: 20 15 10 55

       * - Field
         - Type
         - Req.
         - Description
       * - ``id``
         - ``string``
         - Yes
         - Asset identifier (e.g., ``http://example.com/ids/asset001``)
       * - ``kind``
         - ``enum``
         - Yes
         - ``Type``, ``Instance``, or ``NotApplicable``
       * - ``type``
         - ``ReferenceAAS``
         - No
         - AAS reference for the asset

.. dropdown:: :octicon:`file-badge;1em;sd-text-primary` CapabilityConstraint schema

    .. list-table:: CapabilityConstraint
       :header-rows: 1
       :widths: 20 15 10 55

       * - Field
         - Type
         - Req.
         - Description
       * - ``iri``
         - ``ReferenceIRI``
         - Yes
         - Unique ontology IRI identifier
       * - ``name``
         - ``string``
         - Yes
         - Name of the constraint (e.g., ``capabilityConstraint01``)
       * - ``hasCondition``
         - ``enum``
         - Yes
         - ``INVARIANT``, ``PRECONDITION``, or ``POSTCONDITION``

.. dropdown:: :octicon:`file-badge;1em;sd-text-primary` SkillParameter schema

    .. list-table:: SkillParameter
       :header-rows: 1
       :widths: 20 15 10 55

       * - Field
         - Type
         - Req.
         - Description
       * - ``iri``
         - ``ReferenceIRI``
         - Yes
         - Unique ontology IRI identifier
       * - ``name``
         - ``string``
         - Yes
         - Name of the parameter (e.g., ``skillParameter01``)
       * - ``hasType``
         - ``enum``
         - Yes
         - ``INPUT``, ``OUTPUT``, or ``INOUTPUT``



Usage Examples
--------------

HTTP requests examples
~~~~~~~~~~~~~~~~~~~~~~

**Retrieve all capabilities**

.. code-block:: bash

    curl -X GET "https://<IP>:<PORT>/api/v3/capabilities" \
         -H "Accept: application/json"

**Register a new SMIA instance**

.. code-block:: bash

    curl -X POST "https://<IP>:<PORT>/api/v3/smiaInstances" \
         -H "Content-Type: application/json" \
         -d '{
           "id": "agentInstance001",
           "asset": {
             "id": "http://example.com/ids/asset001",
             "kind": "Instance"
           },
           "aasID": "http://example.com/ids/aasElement001",
           "status": "Running",
           "smiaVersion": "0.3.3"
         }'

**Encode an IRI for use as a path parameter**

.. code-block:: bash

    curl -X PUT "https://<IP>:<PORT>/api/v3/serialization" \
         -H "Content-Type: application/json" \
         -d '"http://name.org/css-smia#Capability01"'

**Check AAS Repository availability**

.. code-block:: bash

    curl -X GET "https://<IP>:<PORT>/api/v3/checkAASRepository?AASRepositoryURL=http://<AAS server IP>:<AAS server PORT>"

FIPA-SMIACL examples
~~~~~~~~~~~~~~~~~~~~

El acceso a SMIA-I KB desde un agente SMIA se realiza mediante el componente de infraestructura SMIA ISM, para asegurar el desacople con los servicios externos y mantener el entorno agéntico totalmente normalizado. The code provided is part of a SPADE behavior, which is responsible for sending messages.

.. seealso::

    El componente SMIA ISM se detalla en su página de documentación dedicada: :octicon:`repo;1em` :ref:`SMIA ecosystem SMIA ISM`.

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



