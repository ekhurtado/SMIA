SMIA Communication Guide
========================

.. _SMIA Communication Guide:

The objective of this guide is to assist in understanding how SMIA agents communicate with each other using the FIPA-ACL standard, which is presented as an I4.0 language. This standard enables proactive and peer-to-peer interactions between SMIA instances.

ACL-SMIA Message Structure
--------------------------

In order to establish proper interactions, we need to adapt SPADE messages to be ACL-compliant and present a structure according to the SMIA approach. We must present a standard structure to enable correct communication with all SMIA agents.

The following table details the FIPA-ACL parameters used within the SMIA approach:

===================  ======================  ===================================================================================
    Parameter            Established by                                          Description
===================  ======================  ===================================================================================
``sender``             SPADE / FIPA-ACL        The ID of the agent that sends the message (e.g., ``senderID@xmppServer``).
``receiver``           FIPA-ACL / SPADE        The ID of the agent that receives the message (e.g., ``receiverID@xmppServer``).
``conversation-id``    FIPA-ACL / SPADE        Identification of the ongoing sequence of communicative acts (thread).
``protocol``           FIPA-ACL                The interaction protocol employed (e.g., ``fipa-contract-net``, ``fipa-request``).
``performative``       FIPA-ACL                The type of the communicative act of the ACL message (e.g., ``propose``, ``request``).
``ontology``           FIPA-ACL                The ontology used to give a meaning to the symbols in the content expression.
``content``            FIPA-ACL / SPADE        The content of the message; or the object of the action (typically JSON).
``encoding``           FIPA-ACL                The specific encoding of the content language expression (e.g., ``application/json``).
``language``           FIPA-ACL                The language in which the content parameter is expressed (e.g., ``smia-language``).
===================  ======================  ===================================================================================

.. note::

    There are other optional parameters that could be used in the future depending on the protocol, such as ``reply-to`` (to indicate that the response must be sent to a different agent) or ``reply-by`` (to establish a timeout or deadline for the response).

SMIA Ontology Library
~~~~~~~~~~~~~~~~~~~~~

The meaning of a message is achieved by combining the ``performative`` (the communicative act) and the ``ontology`` (the meaning of the symbols in the content). While performatives are established by FIPA, the possible values for ``ontology`` in the SMIA approach are gathered from the possible services mentioned in the Functional View of the AAS:

==============================  ========================================================================================================
       Ontology value                                                         Description
==============================  ========================================================================================================
``asset-related-service``       Services provided by the asset or computing infrastructure outside it.
``agent-related-service``       Services provided by the SMIA instance related to social capabilities (e.g., collaboration, negotiation).
``aas-service``                 Infrastructure services provided by the AAS itself for the management of asset-related information.
``aas-infrastructure-service``  Services necessary to register SMIA instances and make them findable to offer global information. These interactions generally are performed against SMIA ISM (see :octicon:`repo;1em` :ref:`SMIA ecosystem SMIA ISM`).
``css-service``                 Services related to the Capability-Skill-Service (CSS) model (e.g., request the execution of a capability).
==============================  ========================================================================================================

.. attention::

    Depending on the ontology value, the structure of the ``content`` (or body) of the ACL-SMIA message will differ. JSON schemas should be used to validate incoming messages depending on the specified ontology.

Constructing the SMIACL Message
-------------------------------

To construct the SPADE message, the FIPA-ACL parameters must be properly placed into the fields of the ``Message`` object provided by the SPADE framework. The mapping is established as follows:

- ``Message.sender`` = sender
- ``Message.to`` = receiver // to
- ``Message.thread`` = conversation-id // thread
- ``Message.metadata`` = protocol, performative, ontology, encoding, language
- ``Message.body`` = content // body

- La clase ``smia.utilities.fipa_acl_info.FIPAACLInfo`` (ver :octicon:`repo;1em` :ref:`API documentation`) recoge los atributos y valores dictaminados por FIPA:
    - Los atributos para la estrucura del mensaje (para añadir o extraer información específica): ``FIPA_ACL_PERFORMATIVE_ATTRIB``, ``FIPA_ACL_ONTOLOGY_ATTRIB``, ``FIPA_ACL_PROTOCOL_ATTRIB``, ``FIPA_ACL_ENCODING_ATTRIB``, ``FIPA_ACL_LANGUAGE_ATTRIB``
    - Los valores para las performativas dictaminadas por FIPA-ACL se puede obtener desde ``FIPA_ACL_PERFORMATIVE_x``: ``FIPA_ACL_PERFORMATIVE_CFP``, ``FIPA_ACL_PERFORMATIVE_INFORM``, ``FIPA_ACL_PERFORMATIVE_REQUEST``, ``FIPA_ACL_PERFORMATIVE_PROPOSE``, etc.
    - Los valores para los protocolos dictaminados por FIPA: ``FIPA_ACL_REQUEST_PROTOCOL``, ``FIPA_ACL_CONTRACT_NET_PROTOCOL``, ``FIPA_ACL_QUERY_PROTOCOL``
- La clase ``smia.utilities.fipa_acl_info.ACLSMIAOntologyInfo`` (ver :octicon:`repo;1em` :ref:`API documentation`) recoge el SMIA Ontology Library:
    - ``ACL_ONTOLOGY_ASSET_RELATED_SERVICE``, ``ACL_ONTOLOGY_AGENT_RELATED_SERVICE``, ``ACL_ONTOLOGY_AAS_SERVICE``, ``ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE``, ``ACL_ONTOLOGY_CSS_SERVICE``

.. TODO REPASAR ESTA SECCION, MEJORARLA Y PASAR A INGLES TEXTO DE CASTELLANO (este si puede dejarse en la version final)

Sending a message from SMIA instance
------------------------------------

Once the structure is clear and the message has been constructed, it can be sent from within any agent capability (i.e., a SPADE Behavior).

.. dropdown:: Source code example for sending an ACL-SMIA message
    :octicon:`code;1em;sd-text-primary`

    .. tip::

        The ``create_acl_smia_message`` method handles JSON serialization and default metadata fields automatically, so you only need to pass the required parameters.

    .. code:: python

        from spade.behaviour import OneShotBehaviour
        from smia.logic import inter_smia_interactions_utils
        from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas

        class SendCSSRequestBehaviour(OneShotBehaviour):
            async def run(self):
                # 1. Define the required information for the css-service
                CSS_INFO = {
                    "capabilityIRI": "http://www.w3id.org/upv-ehu/gcis/css-smia#Drilling",
                    "skillIRI": "http://www.w3id.org/hsu-aut/css##DrillHole",
                    "capConstraints": {"http://www.w3id.org/hsu-aut/css#depth": 50}
                    "skillParameters": {"http://www.w3id.org/hsu-aut/css#maxDepth": 100}
                }

                # 2. Define the content based on the css-service ontology structure (it can be defined using JSON schemas)
                msg_body = await acl_smia_messages_utils.generate_json_from_schema(
                    ACLSMIAJSONSchemas.JSON_SCHEMA_CSS_SERVICE, capabilityIRI=CSS_INFO.get('capabilityIRI'),
                    skillIRI=CSS_INFO.get('skillIRI'), constraints=CSS_INFO.get('capConstraints'),
                    skillParams=CSS_INFO.get('skillParameters'))

                # 3. Build the ACL-SMIA message using the utility method
                acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
                    receiver="receiver_agent@ejabberd",
                    thread="req-thread-001",
                    performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
                    ontology=ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE,
                    protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL,
                    msg_body=msg_body
                )

                # 4. Send the message
                await self.send(acl_msg)
                print(f"Message sent to {acl_msg.to} with ontology {acl_msg.metadata['ontology']}")

    .. note::

        The method automatically sets ``encoding`` to ``application/json`` and ``language`` to ``smia-language`` by default if they are not provided. See :octicon:`repo;1em` :ref:`API documentation` for the complete list of constants available in ``FIPAACLInfo`` and ``ACLSMIAOntologyInfo``.